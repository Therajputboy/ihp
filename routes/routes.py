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

bp_route = Blueprint('bp_route', __name__)

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
            
            if member['role'] != 'marker':
                raise CustomException("Member is not a marker.")
            
            route.update({
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "status": status,
                "markerid": memberid,
                "assigned_to": "marker"
            })
            db.create(
                route_table.table_name,
                route_id,
                route,
                route_table.exclude_from_indexes,
                route_table.json_fields
            )
        elif assigning_role == 'driver':
            if route['status'] != 'completed':
                if not route.get('recent_driver', None):
                    raise CustomException("Route cannot be assigned to driver.")
                raise CustomException(f'Route is already assigned to {route.get("recent_driver", "")}.')
            
            if member['role'] != 'driver':
                raise CustomException("Member is not a driver.")
            
            route.update({
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "status": status,
                "recent_driver": memberid,
                "assigned_to": "driver"
            })
            db.create(
                route_table.table_name,
                route_id,
                route,
                route_table.exclude_from_indexes,
                route_table.json_fields
            )
            statushistory = [status + "@" + datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")]
            driver_route_id = uuid.uuid4().hex
            driver_route = {
                "route_id": route_id,
                "driverid": memberid,
                "status": status,
                "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "statushistory": statushistory,
                "driver_route_id": driver_route_id
            }
            db.create(
                driver_routes.table_name,
                driver_route_id,
                driver_route,
                driver_routes.exclude_from_indexes,
                driver_routes.json_fields
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
        if role == 'admin':
            routes = db.get_by_filter(route_table.table_name, [
                ["status", "!=", "deleted"]
            ], order=["-created_at"],
            json_fields=route_table.json_fields)

        elif role == 'marker':
            routes = db.get_by_filter(route_table.table_name, [
                ["markerid", "=", userid],
                ["status", "!=", "deleted"]
            ], route_table.json_fields, order=["-created_at"])

        elif role == 'driver':
            routes = db.get_by_filter(driver_routes.table_name, [
                ["driverid", "=", userid],
                ["status", "!=", "deleted"]
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
                marker_route_id = f'{routeid}~{userid}~{len(paths)}'
                
                last_active_marker_route = db.get(marked_routes.table_name, paths[-1], marked_routes.json_fields)
                if last_active_marker_route.get('status', '') != 'active':
                    raise Exception("Route is not active.")
                
                paths.append(marker_route_id)
                next_route_time = last_active_marker_route.get('nextroutetime', datetime.now(pytz.timezone('Asia/Kolkata')))

                if datetime.now(pytz.timezone('Asia/Kolkata')) < next_route_time:
                    coordinates = last_active_marker_route.get('coordinates', []) + coordinates
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

                else:
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
        
        result = 200
        payload.update({"message": "Path details saved successfully.",
                        "checkpoints": route["checkpioints"]})
    
    except CustomException as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        payload.update({"message": str(e.message)})
        return make_response(jsonify(payload), result)
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)


@bp_route.route('/<routeid>', methods=['GET'])
@jwt_required
def route_by_id(routeid):
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        routeid = request.view_args.get('routeid', None)
        if not routeid:
            raise CustomException("Route id is required.")
        
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
        user = request.user
        role = user['role']
        driver_merged_coordinates = []
        if role == 'driver':
            driver_route = db.get_by_filter(driver_routes.table_name, [
                ["route_id", "=", routeid],
                ["driverid", "=", user['userid']]
            ], driver_routes.json_fields)

            if driver_route:
                driver_route = driver_route[0]
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
        route.update({
            "status": "deleted"
        })
        db.create(
            route_table.table_name,
            routeid,
            route,
            route_table.exclude_from_indexes,
            route_table.json_fields
        )
        payload.update({"message": "Path deleted successfully."})
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
        result = 200
        payload.update({"message": "Route coordinated saved successfully."})
    
    except CustomException as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        payload.update({"message": str(e.message)})
        return make_response(jsonify(payload), result)
    
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    
    return make_response(jsonify(payload), result)