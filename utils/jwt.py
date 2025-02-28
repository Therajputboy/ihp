import jwt
from flask import request, jsonify
from functools import wraps
from utils.globalconstants import Config
from datetime import datetime, timedelta
from utils import db
from utils.schemas import users

def generate_jwt_token(jwt_payload):
    jwt_payload.update({
        "exp": datetime.now() + timedelta(hours=getattr(Config, 'JWT_EXPIRY_HOURS', 4))
    })
    token = jwt.encode(jwt_payload, Config.SECRET_KEY, algorithm='HS256')
    return token

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('cookie')
        if not token:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"message": "Token is missing"}), 403
            token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing"}), 403
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            request.userid = data['userid']
            user = db.get(users.table_name, request.userid, users.json_fields)
            if not user:
                return jsonify({"message": "User does not exist"}), 403
            request.user = user
            
        except Exception as e:
            return jsonify({"message": "Token is invalid"}), 403
        return f(*args, **kwargs)
    return decorated_function