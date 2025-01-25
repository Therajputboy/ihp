# create a blueprint

from flask import Blueprint, request, jsonify


bp_user = Blueprint('bp_user', __name__)

@bp_user.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return jsonify(data)