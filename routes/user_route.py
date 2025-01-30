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
from utils.schemas import users
from utils.email import send_mail
import random

bp_user = Blueprint('bp_user', __name__)

@bp_user.route('/create', methods=['POST'])
@jwt_required
def create_user():
    try:
        payload, result = {
            "message": "Oops! Something went wrong. Please try again."
        }, 400
        data = request.form.to_dict()
        userid = data['userid']
        password = data['password']
        confirm_password = data['confirm_password']
        email = data['email']
        extras = {}
        if password != confirm_password:
            raise Exception("Passwords do not match.")
        if db.get(users.table_name, userid, users.json_fields):
            raise Exception("User already exists.")
        
        role = data['role']
        name = data['name']
        file = request.files['image']
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
    except Exception as e:
        ExceptionLogging.LogException(traceback.format_exc(), str(e))
        payload.update({"message": str(e)})
    return jsonify(payload), result


@bp_user.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
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
        result = 200
        jwt_payload = {
            "userid": userid,
            "role": user['role'],
            "name": user['name']
        }
        cookie = generate_jwt_token(jwt_payload)
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
            db.update(users.table_name, userid, user, users.json_fields)
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