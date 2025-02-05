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
from utils.schemas import users, routes as route_table, marked_routes, driver_routes
import uuid, json

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
        # members = data.get('assigned_members', [])
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
            raise Exception("Only admin can assign a route.")
        route_id = data['route_id']
        route = db.get(route_table.table_name, route_id, route_table.json_fields)
        if not route:
            raise Exception("Route does not exist.")
        assigned_to = data.get('assigned_to', {})
        assigning_role = assigned_to.get('role', None)
        memberid = assigned_to.get('member', None)
        status = "scheduled"
        if not all([route_id, assigned_to]):
            raise Exception("Route id and member id are required.")
        member = db.get(users.table_name, memberid, users.json_fields)
        if not member:
            raise Exception("Member does not exist.")
        
        if assigning_role == 'marker':
            if route['status'] not in  ['created', 'scheduled']:
                raise Exception("Marker already assigned.")
            
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
                raise Exception(f'Route is already assigned to {route.get("recent_driver", "")}.')
            route.update({
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "status": status,
                "recent_driver": memberid,
                "assigned_to": "driver"
            })
            statushistory = [status + "@" + datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")]
            driver_route = {
                "route_id": route_id,
                "driverid": memberid,
                "status": status,
                "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "statushistory": statushistory,
                "extras": {},
                "coordinates": [],
                "checkpoint": []
            }
            db.create(
                driver_routes.table_name,
                None,
                driver_route,
                driver_routes.exclude_from_indexes,
                driver_routes.json_fields
            )
        result = 200
        payload.update({"message": "Route assigned successfully."})
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
            routes = db.get_all(route_table.table_name, route_table.json_fields, order=["-created_at"])
        elif role == 'marker':
            routes = db.get_by_filter(route_table.table_name, [
                ["markerid", "=", userid]
            ], route_table.json_fields, order=["-created_at"])
        elif role == 'driver':
            routes = db.get_by_filter(driver_routes.table_name, [
                ["driverid", "=", userid]
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
        status = ""

        coordinates = data.get('coordinates', [])
        if isinstance(coordinates, str):
            coordinates = json.loads(coordinates)
        if role == 'marker':
            route = db.get(route_table.table_name, routeid, route_table.json_fields)
            if not route:
                raise Exception("Route does not exist.")
            if route['markerid'] != userid:
                raise Exception("You are not assigned to this route.")
            # if route['status'] != 'scheduled':
            #     raise Exception("Route is not scheduled.")
            if route['status'] == 'completed':
                raise Exception("Route is already completed.")
            
            if not status:
                status = "active"

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
                paths.append(marker_route_id)
            else:
                # marker_route_id = f'{routeid}~{userid}~{len(paths)}'
                # paths.append(marker_route_id)
                # if datetime.now(pytz.timezone('Asia/Kolkata')) > datetime.strptime(route.get('nextroutetime', '')):
                last_active_marker_route = db.get(marked_routes.table_name, paths[-1], marked_routes.json_fields)
                if last_active_marker_route.get('status', '') != 'active':
                    raise Exception("Route is not active.")
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
            
            route["checkpioints"] = route.get("checkpoints", []) + checkpoints
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
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)


@bp_route.route('/route/<routeid>', methods=['GET'])
@jwt_required
def route_by_id():
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        routeid = request.view_args.get('routeid', None)
        if not routeid:
            raise Exception("Route id is required.")
        route = db.get(route_table.table_name, routeid, route_table.json_fields)
        if not route:
            raise Exception("Route does not exist.")
        
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
        payload.update({"message": "Route details fetched successfully.",
                        "route": route})
        result = 200
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)