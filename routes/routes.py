# create a blueprint

from flask import Blueprint, request, jsonify, make_response
from utils.exceptionlogging import ExceptionLogging
import traceback
from utils.storagemanager import upload_file_to_gcs
from utils.jwt import jwt_required, generate_jwt_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
from utils import db
from utils.schemas import users, routes as route_table, marked_routes
import uuid

route_user = Blueprint('route_user', __name__)

@route_user.route('/create', methods=['POST'])
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


@route_user.route('/assign', methods=['POST'])
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
        assigned_to = data.get('assigned_to', '')
        assigning_role = assigned_to.get('role', None)
        if assigning_role == 'marker':
            marker = assigned_to.get('marker', None)
            status = "scheduled"
            if not all([route_id, assigned_to]):
                raise Exception("Route id and member id are required.")
            route = db.get(users.table_name, route_id, users.json_fields)
            if not route:
                raise Exception("Route does not exist.")
            member = db.get(users.table_name, marker, users.json_fields)
            if not member:
                raise Exception("Member does not exist.")
            route.update({
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "status": status,
                "markerid": marker
            })
            db.create(
                route_table.table_name,
                route_id,
                route,
                route_table.exclude_from_indexes,
                route_table.json_fields
            )
        elif assigning_role == 'driver':
            pass
        result = 200
        payload.update({"message": "Route assigned successfully."})
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)


@route_user.route('/list', methods=['GET'])
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
            routes = db.get_all(route_table.table_name, route_table.json_fields)
        elif role == 'marker':
            routes = db.get_by_filter(route_table.table_name, [
                ["markerid", "==", userid]
            ], route_table.json_fields)
        elif role == 'driver':
            pass

        payload.update({"message": "Routes listed successfully.",
                        "routes": routes})
        result = 200
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)

@route_user.route('/travel', methods=['POST'])
@jwt_required
def travell_route():
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        data = request.form.to_dict()
        userid = request.userid
        user = request.user
        role = user['role']
        routeid = data['routeid']

        coordinates = data.get('coordinates', [])
        if role == 'marker':
            route = db.get(route_table.table_name, routeid, route_table.json_fields)
            if not route:
                raise Exception("Route does not exist.")
            if route['markerid'] != userid:
                raise Exception("You are not assigned to this route.")
            status = "active"
            route.update({
                "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
                "status": status
            })

            currentime = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y%m%d%H%M%S")
            checkpoints = []
            for index, coordinate in enumerate(coordinates):
                coordinate.update({
                    "id": f'{currentime}~{index}',
                })
            #     if coordinate.get('checkpoint', False):
            #         checkpoint_imgs = coordinate.
            paths = route.get('paths', [])
            marker_route_id = f'{routeid}~{userid}~{len(paths)}'
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
                    "updated_at": datetime.now(pytz.timezone('Asia/Kolkata'))
                }
            db.create(
                route_table.table_name,
                routeid,
                route,
                route_table.exclude_from_indexes,
                route_table.json_fields
            )
            

        
        result = 200
        payload.update({"message": "Route status updated successfully."})
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)