from flask import Blueprint, request, jsonify
from utils.jwt import jwt_required
from utils import db
from utils.schemas import trucks as truck_table
from datetime import datetime
import pytz
import uuid
from datetime import datetime
from utils.schemas import driver_routes, users

bp_truck = Blueprint('bp_truck', __name__)

@bp_truck.route('/create', methods=['POST'])
@jwt_required
def create_truck():
    try:
        data = request.get_json()
        truckid = str(uuid.uuid4())
        rc_validity = data.get("rc_validity", "")
        insurance_validity = data.get("insurance_validity", "")
        load_capacity = data.get("load_capacity", 0)
        make_and_model = data.get("make_and_model", "")

        if not all([rc_validity, insurance_validity, load_capacity, make_and_model]):
            raise Exception("Mandatory fields missing.")
        
        if db.get_by_filter(truck_table.table_name, [["registration_number", "=", data['registration_number']]], truck_table.json_fields):
            raise Exception("Truck with the give registration number already exist.")
        
        insurance_validity = datetime.strptime(insurance_validity, "%d-%m-%Y")
        rc_validity = datetime.strptime(rc_validity, "%d-%m-%Y")
        
        truck = {
            "truckid": truckid,
            "registration_number": data['registration_number'],
            "rc_validity": rc_validity,
            "insurance_validity": insurance_validity,
            "load_capacity": load_capacity,
            "make_and_model": make_and_model,
            "status": data.get('status', 1),
            "extras": data.get('extras', {}),
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')),
            "created_by": request.userid,
            "assigned": 0
        }
        db.create(
            truck_table.table_name,
            truckid,
            truck,
            truck_table.exclude_from_indexes,
            truck_table.json_fields
        )
        return jsonify({"message": "Truck created successfully", "truck": truck}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@bp_truck.route('/read/<truckid>', methods=['GET'])
@jwt_required
def read_truck(truckid):
    try:
        truck = truck_detail(truckid)
        return {"truck": truck}, 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    

def truck_detail(truckid):
    truck = db.get(truck_table.table_name, truckid, truck_table.json_fields)
    if not truck:
        return jsonify({"message": "Truck not found"}), 400
    assigned = truck.get("assigned", 0)
    if assigned:
        scheduled_driver_routes = db.get_by_filter(
            driver_routes.table_name,
            [
                ["truckid","=", truckid],
                ["status", "=", "scheduled"]
            ],
            driver_routes.json_fields
        )
        if not scheduled_driver_routes:
            raise Exception("Truck not assigned to any route.")
        scheduled_driver_routes = scheduled_driver_routes[0]
        driverids = scheduled_driver_routes.get("driverid", [])
        drivers = db.get_by_filter(
            users.table_name,
            [["userid", "IN", driverids],
            ["status", "=", 1]],
            users.json_fields
        )
        drivers = [
            {
                "userid": driver.get("userid"),
                "name": driver.get("name"),
                "phone": driver.get("phone"),
            } for driver in drivers
        ]
        truck.update({
            "drivers": drivers,
            "driver_route_id": scheduled_driver_routes.get("driver_route_id"),
            "route_id": scheduled_driver_routes.get("route_id")
        })
    
    return truck
    

@bp_truck.route('/update/<truckid>', methods=['PUT'])
@jwt_required
def update_truck(truckid):
    try:
        data = request.get_json()
        truck = db.get(truck_table.table_name, truckid, truck_table.json_fields)
        if not truck:
            return jsonify({"message": "Truck not found"}), 400
        
        rc_validity = data.get("rc_validity", "")
        insurance_validity = data.get("insurance_validity", "")
        load_capacity = data.get("load_capacity", 0)
        make_and_model = data.get("make_and_model", "")

        if not all([rc_validity, insurance_validity, load_capacity, make_and_model]):
            raise Exception("Mandatory fields missing.")
        insurance_validity = datetime.strptime(insurance_validity, "%d-%m-%Y")
        rc_validity = datetime.strptime(rc_validity, "%d-%m-%Y")

        truck.update({
            "truckid": truckid,
            "registration_number": data['registration_number'],
            "rc_validity": rc_validity,
            "insurance_validity": insurance_validity,
            "load_capacity": load_capacity,
            "make_and_model": make_and_model,
            "status": data.get('status', 1),
            "extras": data.get('extras', {}),
            "updated_at": datetime.now(pytz.timezone('Asia/Kolkata'))
        })
        db.create(
            truck_table.table_name,
            truckid,
            truck,
            truck_table.exclude_from_indexes,
            truck_table.json_fields
        )
        return jsonify({"message": "Truck updated successfully", "truck": truck}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@bp_truck.route('/delete/<truckid>', methods=['DELETE'])
@jwt_required
def delete_truck(truckid):
    try:
        truck = db.get(truck_table.table_name, truckid, truck_table.json_fields)
        if not truck:
            return jsonify({"message": "Truck not found"}), 400
        db.delete(truck_table.table_name, truckid)
        return jsonify({"message": "Truck deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
@bp_truck.route('/list', methods=['GET'])
# @jwt_required
def list_trucks():
    try:
        # Optional filters (e.g., status or truck_number)
        status = request.args.get('status')
        assigned = request.args.get("assigned")

        # Build filters dynamically
        filters = []
        if status != None:
            filters.append(["status", "=", int(status)])
        if assigned != None:
            filters.append(["assigned", "=", int(assigned)])

        # Fetch trucks from the database
        trucks = db.get_by_filter(
            truck_table.table_name,
            filters,
            truck_table.json_fields
        )
        return jsonify({
            "message": "Trucks listed successfully",
            "trucks": trucks
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400