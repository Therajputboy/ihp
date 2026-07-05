import sys
from pathlib import Path

# Add the parent directory to the system path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

# Import the utils module
from utils import db
from utils.schemas import routes, trucks

all_routes = db.get_all(
    routes.table_name,
    routes.json_fields
)
for route in all_routes:
    status = route.get("status", {})
    # if status != "completed":
    route.update({
        "assigned_to": "unassigned",
        "assigned_to_user": [],
        "status": "completed"
    })
    db.create(
        routes.table_name,
        route.get("route_id"),
        route,
        routes.exclude_from_indexes,
        routes.json_fields
    )

all_trucks = db.get_all(
    trucks.table_name,
    trucks.json_fields
)
for truck in all_trucks:
    truck.update(
    {
        "assigned": 0
    }
    )
    db.create(
        trucks.table_name,
        truck.get("truckid"),
        truck,
        trucks.exclude_from_indexes,
        trucks.json_fields
    )

