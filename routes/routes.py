# create a blueprint

from flask import Blueprint, request, jsonify, make_response
from utils.exceptionlogging import ExceptionLogging
import traceback
from utils.storagemanager import upload_file_to_gcs
from utils.jwt import jwt_required, generate_jwt_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pytz
from utils import db
from utils.schemas import users, routes as route_table, marked_routes, driver_routes, log_table, driver_travelled_path
import uuid, json
from utils.globalconstants import CustomException
from utils.logging import logger

bp_route = Blueprint('bp_route', __name__)

status_order = {
    "created": 1,
    "scheduled": 2,
    "active": 3,
    "marked": 4,
    "unassigned": 5,
    "completed": 6,
    "failed": 5
}

@bp_route.route('/create', methods=['POST'])
@jwt_required
def create_route():
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        data = request.get_json()
        adminid = request.userid
        admin_user = request.user
        if admin_user['role'] != 'admin':
            raise Exception("Only admin can create a route.")
        route_name = data['route_name']
        status = "created"
        if not all([route_name]):
            raise Exception("Route name is required.")
        route_id = uuid.uuid4().hex
        new_route = {
            "route_id": route_id,
            "route_name": route_name,
            "adminid": adminid,
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "status": status
        }
        db.create(
            route_table.table_name,
            route_id,
            new_route,
            route_table.exclude_from_indexes,
            route_table.json_fields
        )
        log_entry = {
            "userid": adminid,
            "action": "createroute",
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "extras": {
                "route_name": route_name,
                "table": route_table.table_name,
                "table_id": route_id,
            }
        }
        db.create(
            log_table.table_name,
            None,
            log_entry,
            log_table.exclude_from_indexes,
            log_table.json_fields
        )
        result = 200
        payload.update({"message": "Route created successfully.",
                        "route": new_route})
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)


@bp_route.route('/assign', methods=['POST'])
@jwt_required
def assign_route():
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        data = request.get_json()
        adminid = request.userid
        admin_user = request.user
        if admin_user['role'] != 'admin':
            raise CustomException("Only admin can assign a route.")
        
        route_id = data['route_id']
        route = db.get(route_table.table_name, route_id, route_table.json_fields)
        if not route:
            raise CustomException("Route does not exist.")
        
        assigned_to = data.get('assigned_to', {})
        assigning_role = assigned_to.get('role', None)
        memberid = assigned_to.get('member', None)
        status = "scheduled"
        if not all([route_id, assigned_to]):
            raise CustomException("Route id and member id are required.")
        
        member = db.get(users.table_name, memberid, users.json_fields)
        if not member:
            raise CustomException("Member does not exist.")
        
        if assigning_role == 'marker':
            if route['status'] not in  ['created', 'scheduled']:
                raise CustomException("Marker already assigned.")
            
            if route['status'] == 'active':
                raise CustomException("Route is already active.")
            
            if member['role'] != 'marker':
                raise CustomException("Member is not a marker.")
            
            route.update({
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "status": status,
                "markerid": memberid,
                "assigned_to": "marker",
                "assigned_to_user": memberid
            })
            db.create(
                route_table.table_name,
                route_id,
                route,
                route_table.exclude_from_indexes,
                route_table.json_fields
            )
        elif assigning_role == 'driver':                
            if member['role'] != 'driver':
                raise CustomException("Member is not a driver.")
            
            statushistory = [status + "@" + datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")]

            driver_route = db.get_by_filter(driver_routes.table_name, [
                ["route_id", "=", route_id],
                ["driverid", "=", memberid],
                ["status", "IN", ["scheduled", "active", "created"]]
            ], driver_routes.json_fields)
            if driver_route:
                db.delete(driver_routes.table_name, driver_route[0].get('driver_route_id', ''))
            driver_route_id = uuid.uuid4().hex
            driver_route = {
                "route_id": route_id,
                "driverid": memberid,
                "status": status,
                "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "statushistory": statushistory,
                "driver_route_id": driver_route_id,
                "extras": {
                    "route_data": route
                }
            }
            route.update({
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "recent_driver": memberid,
                "assigned_to": "driver",
                "assigned_to_user": memberid
            })
            db.create(
                driver_routes.table_name,
                driver_route.get('driver_route_id', ''),
                driver_route,
                driver_routes.exclude_from_indexes,
                driver_routes.json_fields
            )

            db.create(
                route_table.table_name,
                route_id,
                route,
                route_table.exclude_from_indexes,
                route_table.json_fields
            )
        log_entry={
            "userid": adminid,
            "action": "assignroute",
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "extras": {
                "route_name": route.get('route_name', ''),
                "table": route_table.table_name,
                "table_id": route_id,
                "assigned_to": assigning_role,
                "assigned_member": memberid
            }
        }
        db.create(
            log_table.table_name,
            None,
            log_entry,
            log_table.exclude_from_indexes,
            log_table.json_fields
        )
        result = 200
        payload.update({"message": "Route assigned successfully."})
    
    except CustomException as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        payload.update({"message": str(e.message)})
        return make_response(jsonify(payload), result)
    
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    
    return make_response(jsonify(payload), result)


@bp_route.route('/list', methods=['GET'])
@jwt_required
def list_routes():
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        userid = request.userid
        user = request.user
        role = user['role']
        status = request.args.get('status', '')
        all_users = db.get_all(users.table_name, users.json_fields)
        users_map = {}
        for u in all_users:
            uid = user.get('userid', '')
            users_map[uid] = u
        if role == 'admin':
            if status == 'driver':
                all_routes = db.get_by_filter(route_table.table_name, [
                    ["status", "=", "completed"],
                ], route_table.json_fields, order=["-created_at"])

                dr = db.get_by_filter(driver_routes.table_name,[
                    ["route_id", "IN", [route.get('route_id', '') for route in all_routes]]
                ], driver_routes.json_fields)
                route_map = {
                    route.get('route_id', ''): route for route in dr if route.get('status', '')
                }
                for route in all_routes:
                    if route.get('assigned_to') == 'unassigned':
                        route['status'] = 'unassigned'
                    else:
                        route['status'] = route_map.get(route.get('route_id', ''), {}).get('status', 'unassigned')
                        route['assigned_to'] = []
                        if route['status'] != 'unassigned':
                            route['assigned_to'].append(users_map.get(route_map.get(route.get('route_id', ''), {}).get('driverid', ''), {}))
                            salespersons = route_map.get('extras', {}).get('salespersons', [])
                            route['assigned_to'].extend([users_map.get(sp, {}) for sp in salespersons])
                routes = all_routes

            elif status == 'marker':
                routes = db.get_by_filter(route_table.table_name, [
                    ["status", "!=", "created"],
                    ["assigned_to", "=", "marker"]
                ], route_table.json_fields, order=["-created_at"])
                for route in routes:
                    route['assigned_to'] = [users_map.get(route.get('markerid', ''), {})]
            else:
                routes = db.get_by_filter(route_table.table_name, [
                    ["status", "=", "created"]
                ], order=["-created_at"],
                json_fields=route_table.json_fields)
                # routes = [route for route in routes if route.get('status', '') == 'created']


        elif role == 'marker':
            fetched_routes = db.get_by_filter(route_table.table_name, [
                ["markerid", "=", userid],
                ["status", "=", status]
            ], route_table.json_fields, order=["-created_at"])
            routes = []
            for route in fetched_routes:
                recent_driver = route.get('recent_driver', None)
                if recent_driver:
                    continue
                routes.append(route)
        elif role == 'driver':
            routes = db.get_by_filter(driver_routes.table_name, [
                ["driverid", "=", userid],
                ["status", "=", status]
            ], driver_routes.json_fields, order=["-created_at"])

        payload.update({"message": "Routes listed successfully.",
                        "routes": routes,
                        "role": role})
        result = 200
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    
    return make_response(jsonify(payload), result)

@bp_route.route('/marking', methods=['POST'])
@jwt_required
def mark_route():
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        data = request.form.to_dict()
        logger.info(data)
        userid = request.userid
        user = request.user
        role = user['role']
        routeid = data['routeid']
        status = data.get('status', '')

        coordinates = data.get('coordinates', [])
        if isinstance(coordinates, str):
            coordinates = json.loads(coordinates)
        if role != 'marker':
            raise CustomException("Only marker can mark a route.")
        
        if role == 'marker':
            route = db.get(route_table.table_name, routeid, route_table.json_fields)
            if not route:
                raise CustomException("Route does not exist.")
            
            if route['markerid'] != userid:
                raise CustomException("You are not assigned to this route.")
            
            if route['status'] == 'completed':
                raise CustomException("Route is already completed.")
            
            if not status:
                status = "active"

            if status == 'completed':
                log_entry = {
                    "userid": userid,
                    "action": "markroutecompleted",
                    "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    "extras": {
                        "route_name": route.get('route_name', ''),
                        "table": route_table.table_name,
                        "table_id": routeid,
                        "status": status
                    }
                }
                db.create(
                    log_table.table_name,
                    None,
                    log_entry,
                    log_table.exclude_from_indexes,
                    log_table.json_fields
                )
            if route['status'] == 'scheduled':
                log_entry = {
                    "userid": userid,
                    "action": "markrouteactive",
                    "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    "extras": {
                        "route_name": route.get('route_name', ''),
                        "table": route_table.table_name,
                        "table_id": routeid,
                        "status": status
                    }
                }
                db.create(
                    log_table.table_name,
                    None,
                    log_entry,
                    log_table.exclude_from_indexes,
                    log_table.json_fields
                )
            route.update({
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "status": status
            })
            if status == 'completed':
                route.update({
                    "completed_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    "assigned_to": "unassigned",
                })

            currentime = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y%m%d%H%M%S")
            checkpoints = []
            for index, coordinate in enumerate(coordinates):
                coordinate.update({
                    "id": f'{currentime}~{index}'
                })
                if coordinate.get('checkpoint', False):
                    coordinate['checkpoint'].update({
                        "id": f'{currentime}~{index}'
                    })
                    # file = request.files.get(f'checkpoint_{len(index)}', None)
                    # imageurl = ""
                    # if file:
                    #     file.filename = "checkpoints/" + {routeid} + "/" + f'{currentime}~{index}' + "." + "png"
                    #     imageurl = upload_file_to_gcs(file, 'ihp-rpp-bucket')
                    #     coordinate['checkpoint'].update({
                    #         "imageurl": imageurl
                    #     })
                    checkpoints.append(coordinate.pop('checkpoint'))
                    # Handle photo upload and save the image url properly
            paths = route.get('paths', [])
            if not paths:
                marker_route_id = f'{routeid}~{userid}~{0}'
                paths.append(marker_route_id)
                marker_route_data = {
                    "route_id": routeid,
                    "markerid": userid,
                    "path_id": marker_route_id,
                    "coordinates": coordinates,
                    # "checkpoint": checkpoint,
                    "status": status,
                    "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    "nextroutetime": datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=5),
                }
                db.create(
                    marked_routes.table_name,
                    marker_route_id,
                    marker_route_data,
                    marked_routes.exclude_from_indexes,
                    marked_routes.json_fields
                )
                
            else:
                
                last_active_marker_route = db.get(marked_routes.table_name, paths[-1], marked_routes.json_fields)
                if last_active_marker_route.get('status', '') != 'active':
                    raise Exception("Route is not active.")
                
                next_route_time = last_active_marker_route.get('nextroutetime', datetime.now(pytz.timezone('Asia/Kolkata')))

                if datetime.now(pytz.timezone('Asia/Kolkata')) < next_route_time:
                    coordinates = last_active_marker_route.get('coordinates', []) + coordinates
                    # marker_route_data = {
                    #     "route_id": routeid,
                    #     "markerid": userid,
                    #     "path_id": marker_route_id,
                    #     "coordinates": coordinates,
                    #     # "checkpoint": checkpoint,
                    #     "status": status,
                    #     "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    #     "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    #     "nextroutetime": datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=5),
                    # }
                    last_active_marker_route['coordinates'] = coordinates
                    last_active_marker_route['updated_at'] = datetime.now(pytz.timezone('Asia/Kolkata'))
                    marker_route_id = last_active_marker_route.get('path_id', '') 
                    marker_route_data = last_active_marker_route
                else:
                    marker_route_id = f'{routeid}~{userid}~{len(paths)}'
                    paths.append(marker_route_id)
                    marker_route_data = {
                        "route_id": routeid,
                        "markerid": userid,
                        "path_id": marker_route_id,
                        "coordinates": coordinates,
                        # "checkpoint": checkpoint,
                        "status": status,
                        "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                        "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                        "nextroutetime": datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=5),
                    }
                db.create(
                    marked_routes.table_name,
                    marker_route_id,
                    marker_route_data,
                    marked_routes.exclude_from_indexes,
                    marked_routes.json_fields
                )
            
            route["checkpoints"] = route.get("checkpoints", []) + checkpoints
            route["paths"] = paths
            db.create(
                route_table.table_name,
                routeid,
                route,
                route_table.exclude_from_indexes,
                route_table.json_fields
            )
        
        marked_paths = db.get_multi_by_key(marked_routes.table_name, paths, marked_routes.json_fields)
        paths_map = {}
        for path in marked_paths:
            path_id = path.get('path_id', '')
            paths_map[path_id] = path

        merged_coordinates = []
        for path_id in paths:
            merged_coordinates += paths_map.get(path_id, {}).get('coordinates', [])

        result = 200
        payload.update({"message": "Path details saved successfully.",
                        "checkpoints": route["checkpoints"],
                        "marked_coordinates": merged_coordinates})
    
    except CustomException as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        payload.update({"message": str(e.message)})
        return make_response(jsonify(payload), result)
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)

@bp_route.route('/update/checkpoint', methods=['POST'])
@jwt_required
def update_checkpoint():
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        data = request.form.to_dict()
        userid = request.userid
        user = request.user
        role = user['role']
        routeid = data['routeid']
        # pathid = data['pathid']
        checkpoint_id = data['checkpoint_id']
        contact = data.get('contact', '')
        location_name = data.get('location_name', '')
        image = request.files.get('image', None)
        if role != 'marker':
            raise CustomException("Only marker can update a checkpoint.")
        
        if role == 'marker':
            route = db.get(route_table.table_name, routeid, route_table.json_fields)
            if not route:
                raise CustomException("Route does not exist.")
            
            if route['markerid'] != userid:
                raise CustomException("You are not assigned to this route.")
            
            if route['status'] == 'completed':
                raise CustomException("Route is already completed.")
            
            checkpoints = route.get('checkpoints', [])
            for checkpoint in checkpoints:
                if checkpoint.get('id', '') == checkpoint_id:
                    checkpoint.update({
                        "contact": contact,
                        "location_name": location_name
                    })
                    if image:
                        image.filename = "checkpoints/" + {routeid} + "/" + checkpoint_id + "." + "png"
                        imageurl = upload_file_to_gcs(image, 'ihp-rpp-bucket')
                        checkpoint.update({
                            "imageurl": imageurl
                        })
                    break


            log_entry = {
                "userid": userid,
                "action": "checkpointupdated",
                "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "extras": {
                    "route_name": route.get('route_name', ''),
                    "table": route_table.table_name,
                    "table_id": routeid,
                    "status": 'active'
                }
            }
            db.create(
                log_table.table_name,
                None,
                log_entry,
                log_table.exclude_from_indexes,
                log_table.json_fields
            )
            route.update({
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            })

            db.create(
                route_table.table_name,
                routeid,
                route,
                route_table.exclude_from_indexes,
                route_table.json_fields
            )
    except CustomException as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        payload.update({"message": str(e.message)})
        return make_response(jsonify(payload), result)
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    
@bp_route.route('/<routeid>', methods=['GET'])
@jwt_required
def route_by_id(routeid):
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        user = request.user
        role = user['role']

        routeid = request.view_args.get('routeid', None)
        driver_route_id = request.args.get('driver_route_id', None)
        if not routeid:
            raise CustomException("Route id is required.")
        
        if not driver_route_id and role == "driver":
            raise CustomException("Driver route id is required.")
        
        route = db.get(route_table.table_name, routeid, route_table.json_fields)
        if not route:
            raise CustomException("Route does not exist.")
        
        paths = route.get('paths', [])
        marked_paths = db.get_multi_by_key(marked_routes.table_name, paths, marked_routes.json_fields)
        paths_map = {}
        for path in marked_paths:
            path_id = path.get('path_id', '')
            paths_map[path_id] = path

        merged_coordinates = []
        for path_id in paths:
            merged_coordinates += paths_map.get(path_id, {}).get('coordinates', [])
        
        route.update({
            "coordinates": merged_coordinates
        })
        driver_merged_coordinates = []
        if role == 'driver':
            driver_route = db.get(driver_routes.table_name, driver_route_id, driver_routes.json_fields)

            if driver_route:
                paths = driver_route.get('paths', [])
                driver_paths = db.get_multi_by_key(driver_travelled_path.table_name, paths, driver_travelled_path.json_fields)

                driver_paths_map = {}
                for path in driver_paths:
                    path_id = path.get('path_id', '')
                    driver_paths_map[path_id] = path

                driver_merged_coordinates = []
                for path_id in paths:
                    driver_merged_coordinates += driver_paths_map.get(path_id, {}).get('coordinates', [])

            route.update({
                "driver_travelled_coordinates": driver_merged_coordinates
            })
        payload.update({"message": "Route details fetched successfully.",
                        "route": route})
        result = 200

    except CustomException as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        payload.update({"message": str(e.message)})
        return make_response(jsonify(payload), result)
    
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    
    return make_response(jsonify(payload), result)

@bp_route.route('/delete/<routeid>', methods=['GET'])
@jwt_required
def delete_path_by_id(routeid):
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        # routeid = request.view_args.get('routeid', None)
        user = request.user
        role = user['role']
        if role != 'admin':
            raise CustomException("Only admin can delete a route.")
        
        if not routeid:
            raise CustomException("Route id is required.")
        
        route = db.get(route_table.table_name, routeid, route_table.json_fields)
        if not route:
            raise CustomException("Route does not exist.")
        
        assigned_to = route.get('assigned_to', '')
        delete = False
        if assigned_to == 'driver':
            driver_routes = db.get_by_filter(driver_routes.table_name, [
                                ["route_id", "=", routeid],
                                ["status", "IN", ['scheduled', "active"]]
                            ], driver_routes.json_fields)

            if driver_routes:
                raise CustomException("Route is active by driver {0}, cannot be deleted.".format(driver_routes[0].get("driverid", "")))
            delete = True
        if assigned_to == 'marker':
            if route['status'] == 'active':
                raise CustomException("Route is active by marker {0}, cannot be deleted.".format(route.get("markerid")))
            delete = True
            
            
        log_entry = {
            "userid": request.userid,
            "action": "deleteroute",
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "extras": {
                "route_name": route.get('route_name', ''),
                "table": route_table.table_name,
                "table_id": routeid,
            }
        }
        db.create(
            log_table.table_name,
            None,
            log_entry,
            log_table.exclude_from_indexes,
            log_table.json_fields
        )
        if delete:
            db.delete(route_table.table_name, routeid)
            payload.update({"message": "Route deleted successfully."})
        else:
            payload.update({"message": "Route cannot be deleted."})
        
        payload.update({"message": "Route deleted successfully."})
        result = 200

    except CustomException as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        payload.update({"message": str(e.message)})
        return make_response(jsonify(payload), result)
    
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    
    return make_response(jsonify(payload), result)

@bp_route.route('/driver/travel', methods=['POST'])
@jwt_required
def driver_travel():
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        data = request.get_json()
        driverid = request.userid
        driver = request.user 
        if driver['role'] != 'driver':
            raise CustomException("Only driver can travel a route.")
        
        driver_route_id = data.get('driver_route_id', None)
        status = data.get('status', '')

        driver_route = db.get(driver_routes.table_name, driver_route_id, driver_routes.json_fields)
        if not driver_route:
            raise CustomException("Route does not exist.")
        
        if not status:
            status = "active"

        route_id = driver_route.get('route_id', '')
        route_data = db.get(route_table.table_name, route_id, route_table.json_fields)
        if not route_data:
            raise CustomException("Route does not exist.")
        
        coordinates = data.get('coordinates', [])
        if isinstance(coordinates, str):
            coordinates = json.loads(coordinates)
        
        if status == 'completed':
            log_entry = {
                "userid": driverid,
                "action": "drivertravelcompleted",
                "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "extras": {
                    "route_name": driver_route.get('route_name', ''),
                    "table": driver_routes.table_name,
                    "table_id": driver_route_id,
                    "status": status
                }
            }
            db.create(
                log_table.table_name,
                None,
                log_entry,
                log_table.exclude_from_indexes,
                log_table.json_fields
            )
        if driver_route['status'] == 'scheduled':
            log_entry = {
                "userid": driverid,
                "action": "drivertravelactive",
                "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "extras": {
                    "route_name": driver_route.get('route_name', ''),
                    "table": driver_routes.table_name,
                    "table_id": driver_route_id,
                    "status": status
                }
            }
            db.create(
                log_table.table_name,
                None,
                log_entry,
                log_table.exclude_from_indexes,
                log_table.json_fields
            )
        driver_route.update({
            "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "status": status
        })
        route_data.update({
            "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "status": status
        })
        if status == 'completed':
            route_data.update({
                "assigned_to": "unassigned",
            })
        currentime = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y%m%d%H%M%S")
        checkpoints_covered = []
        for index, coordinate in enumerate(coordinates):
            coordinate.update({
                "id": f'{currentime}~{index}'
            })
            checkpoint_id = coordinate.get('checkpoint_id', None)
            if checkpoint_id:
                checkpoints_covered.append(checkpoint_id)
        
        driver_route["checkpoints_covered"] = driver_route.get("checkpoints_covered", []) + checkpoints_covered
        paths = driver_route.get('paths', [])
        if not paths:
            driver_route_path_id = f'{driver_route_id}~{0}'

            driver_travelled_path_data = {
                "route_id": driver_route.get('route_id', ''),
                                    "driverid": driverid,
                "path_id": driver_route_path_id,
                "coordinates": coordinates,
                # "checkpoint": checkpoint,
                "status": status,
                "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "nextroutetime": datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=5),
            }
            db.create(
                driver_travelled_path.table_name,
                driver_route_path_id,
                driver_travelled_path_data,
                driver_travelled_path.exclude_from_indexes,
                driver_travelled_path.json_fields
            )
            paths.append(driver_route_path_id)

        else:
            driver_route_path_id = f'{driver_route_id}~{len(paths)}'
            last_active_driver_route_path = db.get(driver_travelled_path.table_name, paths[-1], driver_travelled_path.json_fields)
            if last_active_driver_route_path.get('status', '') != 'active':
                raise Exception("Route is not active.")
            
            next_route_time = last_active_driver_route_path.get('nextroutetime', datetime.now(pytz.timezone('Asia/Kolkata')))
            if datetime.now(pytz.timezone('Asia/Kolkata')) < next_route_time:
                coordinates = last_active_driver_route_path.get('coordinates', []) + coordinates
                driver_travelled_path_data = {
                    "route_id": driver_route.get('route_id', ''),
                    "path_id": driver_route_path_id,
                    "driverid": driverid,
                    "coordinates": coordinates,
                    # "checkpoint": checkpoint,
                    "status": status,
                    "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    "nextroutetime": last_active_driver_route_path.get('nextroutetime', datetime.now(pytz.timezone('Asia/Kolkata'))) + timedelta(minutes=5),
                }

            else:
                
                driver_travelled_path_data = {
                    "route_id": driver_route.get('route_id', ''),
                    "path_id": driver_route_path_id,
                    "driverid": driverid,
                    "coordinates": coordinates,
                    # "checkpoint": checkpoint,
                    "status": status,
                    "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                    "nextroutetime": datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=5),
                }
            paths.append(driver_route_path_id)
            db.create(
                driver_travelled_path.table_name,
                driver_route_path_id,
                driver_travelled_path_data,
                driver_travelled_path.exclude_from_indexes,
                driver_travelled_path.json_fields
            )
        
        driver_route["paths"] = paths
        db.create(
            driver_routes.table_name,
            driver_route_id,
            driver_route,
            driver_routes.exclude_from_indexes,
            driver_routes.json_fields
        )
        db.create(
            route_table.table_name,
            route_id,
            route_data,
            route_table.exclude_from_indexes,
            route_table.json_fields
        )
        driver_merged_coordinates = []
        # driver_route = driver_route[0]
        paths = driver_route.get('paths', [])
        driver_paths = db.get_multi_by_key(driver_travelled_path.table_name, paths, driver_travelled_path.json_fields)

        driver_paths_map = {}
        for path in driver_paths:
            path_id = path.get('path_id', '')
            driver_paths_map[path_id] = path

        driver_merged_coordinates = []
        for path_id in paths:
            driver_merged_coordinates += driver_paths_map.get(path_id, {}).get('coordinates', [])

        result = 200
        payload.update({"message": "Route coordinated saved successfully.",
                        "driver_travelled_coordinates": driver_merged_coordinates})
    
    except CustomException as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        payload.update({"message": str(e.message)})
        return make_response(jsonify(payload), result)
    
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    
    return make_response(jsonify(payload), result)