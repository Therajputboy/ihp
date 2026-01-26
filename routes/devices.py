from flask import Blueprint, request, jsonify
from utils.jwt import jwt_required
from utils import db
from utils.schemas import devices as device_table, device_mapping
from datetime import datetime
import pytz
import uuid
from datetime import datetime

bp_device = Blueprint('bp_device', __name__)

@bp_device.route('/create', methods=['POST'])
@jwt_required
def create_device():
    try:
        data = request.get_json()
        device_number = data.get("device_number", "")
        device_name = data.get("device_name", "")
        phone = data.get("phone", "")
        purchase_date = data.get("purchase_date", "")
        brand_and_model = data.get("brand_and_model", "")

        if not all([device_number, device_name, phone, purchase_date, brand_and_model]):
            raise Exception("Mandatory fields missing")
        if db.get(device_table.table_name, device_number, device_table.json_fields):
            raise Exception(f"Device with device number {0} already exist".format(device_number))
        
        device = {
            "device_number": device_number,
            "phone": phone,
            "device_name": device_name,
            "purchase_date": datetime.strptime(purchase_date, "%d-%m-%Y"),
            "brand_and_model": brand_and_model,
            "status": data.get("status", 1),
            "extras": data.get('extras', {}),
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "updated_at": datetime.now(pytz.timezone('Asia/Kolkata'))
        }
        db.create(
            device_table.table_name,
            device_number,
            device,
            device_table.exclude_from_indexes,
            device_table.json_fields
        )
        return jsonify({"message": "Device created successfully", "device": device}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@bp_device.route('/read/<deviceid>', methods=['GET'])
def read_device(deviceid):
    try:
        device = db.get(device_table.table_name, deviceid, device_table.json_fields)
        if not device:
            return jsonify({"message": "Device not found"}), 400
        return jsonify({"device": device}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@bp_device.route('/update/<device_number>', methods=['PUT'])
@jwt_required
def update_device(device_number):
    try:
        data = request.get_json()
        device = db.get(device_table.table_name, device_number, device_table.json_fields)
        if not device:
            return jsonify({"message": "Device not found"}), 400
        
        device_number = data.get("device_number", "")
        device_name = data.get("device_name", "")
        phone = data.get("phone", "")
        purchase_date = data.get("purchase_date", "")
        brand_and_model = data.get("brand_and_model", "")
        status = data.get("status", 0)
        device.update({
            "device_number": device_number,
            "phone": phone,
            "device_name": device_name,
            "purchase_date": datetime.strptime(purchase_date, "%d-%m-%Y"),
            "brand_and_model": brand_and_model,
            "status": data.get("status", 1),
            "extras": data.get('extras', {}),
            "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "created_by": request.userid
        })
        db.create(
            device_table.table_name,
            device_number,
            device,
            device_table.exclude_from_indexes,
            device_table.json_fields
        )
        return jsonify({"message": "Device updated successfully", "device": device}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@bp_device.route('/delete/<device_number>', methods=['DELETE'])
@jwt_required
def delete_device(device_number):
    try:
        device = db.get(device_table.table_name, device_number, device_table.json_fields)
        if not device:
            return jsonify({"message": "Device not found"}), 400
        db.delete(device_table.table_name, device_number)
        return jsonify({"message": "Device deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    

@bp_device.route('/list', methods=['GET'])
# @jwt_required
def list_devices():
    try:
        # Optional filters (e.g., status or phone)
        status = request.args.get('status')
        phone = request.args.get('phone')

        # Build filters dynamically
        filters = []
        if status is not None:
            filters.append(["status", "=", int(status)])
        if phone:
            filters.append(["phone", "=", phone])

        # Fetch devices from the database
        devices = db.get_by_filter(
            device_table.table_name,
            filters,
            device_table.json_fields
            # order=["-created_at"]
        )
        dms = db.get_by_filter(
            device_mapping.table_name,
            [
                ["active", "=", True]
            ],
            device_mapping.json_fields
        )
        active_devices = {}
        for dm in dms:
            device_number = dm.get("device_number")
            if device_number not in active_devices:
                active_devices[device_number] = {
                    "device_number": device_number,
                    "truckid": dm.get("truckid"),
                    "registration_number": dm.get("extras", {}).get("registration_number", ""),
                    "drivers": dm.get("extras", {}).get("drivers", []) 
                }
        for device in devices:
            device_number = device.get("device_number")
            if device_number in active_devices:
                device.update(
                    active_devices[device_number]
                )

        return jsonify({
            "message": "Devices listed successfully",
            "devices": devices
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400