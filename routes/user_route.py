# create a blueprint

from flask import Blueprint, request, jsonify, make_response
from utils.exceptionlogging import ExceptionLogging
import traceback
import logging
from utils.storagemanager import upload_file_to_gcs
from utils.jwt import jwt_required, generate_jwt_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
from utils import db
from utils.schemas import users, routes, driver_routes, feedback as feedback_table, log_table
from utils.email import send_mail
import random
import uuid

bp_user = Blueprint('bp_user', __name__)

def marker_update(userid):
    '''
        Affected Table: Routes
        Action: On delete of Marker or on update of role: marker to driver
        Validations: On marker assigned to route. If the marker route is Acive Raise Exception,
                     If the marker route is scheduled, remove the marker from route and set route status to created
    '''
    marker_route = db.get_by_filter(routes.table_name, [("markerid", "=", userid, "status" != 'completed')], routes.json_fields)
    if any(route.get("status") == "active" for route in marker_route):
        raise Exception("Active marker cannot be deleted.")
    
    # Update the Table Route for Markers
    for route in marker_route.copy():
        route_id = route.get("route_id")
        log_entry={
            "markerid": userid,
            "action": "deletemarkerfromroute",
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "extras": {
                "assigned_to_route": route.get("route_name", ''),
                "route_status": route.get("status", ''),
                "table": routes.table_name,
                "table_id": route_id
                }
            }
        route.update({'markerid': '','status': 'created', 'assigned_to': '', 'assigned_to_user': ''})
        db.create(
            routes.table_name,
            route_id,
            route,
            routes.exclude_from_indexes,
            routes.json_fields
        )
        db.create(
            log_table.table_name,
            None,             
            log_entry,
            log_table.exclude_from_indexes,
            log_table.json_fields
        )


def driver_update(userid):
    '''
        Affected Table: DriverRoutes
        Action: On delete of Driver or on update of role: driver to marker
        Validations: On driver assigned to route. If the driver route is Acive Raise Exception,
                     If the driver route is scheduled, delete all the entries of the driver from the table
    '''
    drivers_route = db.get_by_filter(driver_routes.table_name, [("driverid", "=", userid, "status" != 'completed')], driver_routes.json_fields)     
    if any(route.get("statuss") == "active" for route in drivers_route):
        raise Exception("Active driver cannot be deleted.")
            
    # Delete routes of driver that are not completed
    for path in drivers_route:
        driver_route_id = path.get('driver_route_id', None)
        log_entry={
            "driverid": userid,
            "action": "deletedriverfromroute",
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
             "extras": {
                 "assigned_to_route": path.get("route_name", ''),
                 "route_status": path.get("status", ''),
                 "route_id": path.get("route_id", ''),
                 "table": driver_routes.table_name,
                "table_id": driver_route_id
                }
            }
        db.delete(driver_routes.table_name, driver_route_id)
        db.create(
            log_table.table_name,
            None,
            log_entry,
            log_table.exclude_from_indexes,
            log_table.json_fields
        )

@bp_user.route('/upsert', methods=['POST'])
@jwt_required
def create_user():
    try:
        payload, result = {
            "message": "Oops! Something went wrong. Please try again."
        }, 400
        data = request.form.to_dict()
        logging.info(data)
        userid = data['userid']
        password = data['password']
        confirm_password = data['confirm_password']
        email = data['email']
        role = data['role']
        name = data['name']

        extras = {}
        if password != confirm_password:
            raise Exception("Passwords do not match.")
        update = False
        check_existing_user = db.get(users.table_name, userid, users.json_fields)
        if check_existing_user:
            update = True

            existing_role = check_existing_user.get('role', '')

            if existing_role != role:
                role_change_restrictions = {
                    ("admin", "driver"): f"Admin cannot be assigned as {role}",
                    ("admin", "marker"): f"Admin cannot be assigned as {role}",
                    ("driver", "admin"): f"{role} cannot be assigned as Admin",
                    ("marker", "admin"): f"{role} cannot be assigned as Admin",
                    }
                if (existing_role, role) in role_change_restrictions:
                    raise Exception(role_change_restrictions[(existing_role, role)])
                
                role_update_map = {
                    ("marker", "driver"): marker_update,
                    ("driver", "marker"): driver_update,
                    }
                role_update_map.get((existing_role, role), lambda x: None)(userid)

            log_entry_for_update={
            "userid": check_existing_user.get("userid", ''),
            "action": "updateemployee",
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
             "extras": {
                 "old_data": {
                     'name': check_existing_user.get("name", ''), 'password': check_existing_user.get("password", ''),
                     'email': check_existing_user.get("email", ''), 'role': check_existing_user.get("role", '')
                     },
                "updated_data": {
                    'name': name, 'password': password,
                    'email': email, 'role': role
                },
                "table": users.table_name,
                "table_id": userid
                }
            }
        
        file = request.files.get('image')
        imageurl = ""
        if file:
            file.filename = "users/" + userid + "." + "png"
            imageurl = upload_file_to_gcs(file, 'ihp-rpp-bucket')
        extras.update({"imageurl": imageurl})
        created_by = request.userid
        new_user = {
            "userid": userid,
            "password": generate_password_hash(password),
            "role": role,
            "name": name,
            "extras": extras,
            "created_by": created_by,
            "created_on": datetime.now(pytz.timezone('Asia/Kolkata')),
            "status": 1,
            "email": email
        }
        db.create(
            users.table_name,
            userid,
            new_user,
            users.exclude_from_indexes,
            users.json_fields
        )
        result = 200
        payload.update({"message": "User created successfully.",
                        "userid": new_user})
        if update:
            db.create(
                log_table.table_name,
                None,
                log_entry_for_update,
                log_table.exclude_from_indexes,
                log_table.json_fields
            )
            payload.update({"message": "User updated successfully.",
                            "userid": new_user})
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), str(e))
        payload.update({"message": str(e)})
    return jsonify(payload), result


@bp_user.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        logging.info(data)
        userid = data['userid']
        password = data['password']
        user = db.get(users.table_name, userid, users.json_fields)
        if not user:
            raise Exception("User does not exist.")
        if not( user and check_password_hash(user['password'], password) and user['status'] == 1):
            raise Exception("Password is incorrect.")
        data = {
            "message": "Login successful.",
            "user": user,
            "role": user['role']
        }   
        sessionid = uuid.uuid4().hex
        user['sessionid'] = sessionid
        db.create(
            users.table_name,
            userid,
            user,
            users.exclude_from_indexes,
            users.json_fields
        )
        result = 200
        jwt_payload = {
            "userid": userid,
            "role": user['role'],
            "name": user['name'],
            "sessionid": sessionid
        }
        cookie = generate_jwt_token(jwt_payload)
        data.update({"token": cookie})
        resp = make_response(jsonify(data), result)
        resp.set_cookie('cookie', cookie)
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), str(e))
        data = {
            "message": str(e)
        }
        result = 400
        return jsonify(data), result
    return resp


# CREATE A RESET PASSWORD ENDPOINT WHICH WILL SEND OTP TO THE USER'S EMAIL, AND THEN VERIFY THE OTP, AND THEN RESET THE PASSWORD

@bp_user.route('/resetpassword', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        logging.info(data)
        userid = data['userid']
        action = data.get('action', "sendotp")
        user = db.get(users.table_name, userid, users.json_fields)
        if not user:
            raise Exception("User does not exist.")
        
        email = user.get('email')
        if not email:
            raise Exception("Email is not provided.")
        # SEND OTP TO THE USER'S EMAIL
        if action == "sendotp":
            otp = random.randint(1000, 9999)
            # SEND OTP TO EMAIL
            data = {
                "message": "OTP sent to email."
            }
            send_mail(email, "OTP for password reset", f"Your OTP is {otp}")
            user['otp'] = otp
            result = 200
            # return jsonify(data), result
        
        if action == "verifyotp":
            otp = data['otp']
            if user['otp'] != otp:
                raise Exception("OTP is incorrect.")
            data = {
                "message": "OTP verified."
            }
            user['otp'] = None
            result = 200
            # return jsonify(data), result

        if action == "resetpassword":
            password = data['password']
            confirm_password = data['confirm_password']
            if password != confirm_password:
                raise Exception("Passwords do not match.")
            user['password'] = generate_password_hash(password)
            # db.update(users.table_name, userid, user, users.json_fields)
            data = {
                "message": "Password reset successful."
            }
            result = 200
        
        db.create(
            users.table_name,
            userid,
            user,
            users.exclude_from_indexes,
            users.json_fields
        )
        result = 200
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), str(e))
        data = {
            "message": str(e)
        }
        result = 400
    return jsonify(data), result

@bp_user.route('/logout', methods=['POST'])
@jwt_required
def logout():
    try:
        data = {
            "message": "Logout successful."
        }
        result = 200
        userid = request.userid
        user = db.get(users.table_name, userid, users.json_fields)
        user['sessionid'] = None
        db.create(
            users.table_name,
            userid,
            user,
            users.exclude_from_indexes,
            users.json_fields
        )
        resp = make_response(jsonify(data), result)
        resp.set_cookie('cookie', '', expires=0)
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), str(e))
        data = {
            "message": str(e)
        }
        result = 400
        return jsonify(data), result
    return resp

@bp_user.route('/feedback', methods=['POST'])
@jwt_required
def feedback():
    try:
        data = request.form.to_dict()
        userid = request.userid
        user = db.get(users.table_name, userid, users.json_fields)
        if not user:
            raise Exception("User does not exist.")
        feedback = data['feedback']
        description = data.get('description', "")
        created_on = datetime.now(pytz.timezone('Asia/Kolkata'))
        feedbackid = uuid.uuid4().hex
        new_feedback = {
            "userid": userid,
            "feedback": feedback,
            "created_on": created_on,
            "extras": {
                "description": description,
                "images": []
            }
        }
        for index, file in enumerate(request.files):
            file_data = request.files[file]
            file_data.filename = "feedback/" + userid + "/" + feedbackid + "~" + str(index) + "." + "png"
            imageurl = upload_file_to_gcs(file_data, 'ihp-rpp-bucket')
            new_feedback['extras']['images'].append(imageurl)
        db.create(
            feedback_table.table_name,
            feedbackid,
            new_feedback,
            feedback_table.exclude_from_indexes,
            feedback_table.json_fields
        )
        data = {
            "message": "Feedback submitted successfully."
        }
        result = 200
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), str(e))
        data = {
            "message": str(e)
        }
        result = 400
    return jsonify(data), result


@bp_user.route('/list', methods=['GET'])
@jwt_required
def list_employees():
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
    }, 400
    try:
        # Fetch results
        employees = db.get_all(users.table_name, users.json_fields)

        emp_res = [
            {
                'image': emp.get('extras', {}).get('imageurl', None),
                'name': emp.get('name', None),
                'email': emp.get('email', None),
                'status': emp.get('status', None),
                'role': emp.get('role', None),
                'userid': emp.get('userid', None)
            } for emp in employees] 

        payload.update({"message": "Employees List fetched successfully.",
                        "employee_list": emp_res})
        result = 200

    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), e)
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)


@bp_user.route('/delete/<userid>', methods=['GET'])
@jwt_required
def delete_employee(userid):
    payload, result = {
        "message": "Oops! Something went wrong. Please try again."
        }, 400
    try:
        employee = db.get_by_filter(users.table_name, [("userid", "=", userid)], users.json_fields)
        
        if not employee:
            raise Exception("Employee does not exist.")
        
        if employee[0].get("role") == 'marker':
            marker_update(userid)

        elif employee[0].get("role") == 'driver':
            driver_update(userid)
        
        log_entry={
            "userid": userid,
            "action": "deleteemployee",
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "extras": {
                "name": employee[0].get("name", ''),
                "email": employee[0].get("email", ''),
                "role": employee[0].get("role", ''),
                "created_by": employee[0].get("created_by", ''),
                "table": users.table_name,
                "table_id": userid
            }
        }
        db.delete(users.table_name, userid)
        db.create(
            log_table.table_name,
            None,
            log_entry,
            log_table.exclude_from_indexes,
            log_table.json_fields
        )
        

        payload.update({"message": "Employee deleted successfully.",
                        "employee_deleted": userid})
        result = 200

    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), str(e))
        payload.update({"message": str(e)})
        return make_response(jsonify(payload), result)
    return make_response(jsonify(payload), result)
    



