# Initiate a flask app

from flask import Flask
from flask_cors import CORS
from urllib.parse import quote as url_quote
from routes.user_route import bp_user
from routes.routes import bp_route
from routes.trucks  import bp_truck
from routes.devices import bp_device
from routes.admin_report import bp_admin_report
from routes.admin_truck_report import bp_truck_report
from routes.admin_route_report import bp_route_report

app = Flask(__name__)
# Allow all origins in CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Register the blueprint
app.register_blueprint(bp_user, url_prefix='/v2/app/user')
app.register_blueprint(bp_route, url_prefix='/v2/app/route')
app.register_blueprint(bp_truck, url_prefix="/v2/app/trucks")
app.register_blueprint(bp_device, url_prefix="/v2/app/devices")
app.register_blueprint(bp_admin_report, url_prefix='/v2/app/admin/reports')
app.register_blueprint(bp_truck_report, url_prefix='/v2/app/admin/reports')
app.register_blueprint(bp_route_report, url_prefix='/v2/app/admin/reports')

if __name__ == '__main__':
    app.run(debug=True, port=8080)

# gcloud builds submit --tag gcr.io/ihp-rpp/backend-app --project ihp-rpp
# gcloud run deploy --image gcr.io/ihp-rpp/backend-app --platform managed --project ihp-rpp
# gcloud datastore indexes create index.yaml --project=ihp-rpp

# gcloud builds submit --tag gcr.io/ihp-gps/backend-app --project ihp-gps
# gcloud run deploy --image gcr.io/ihp-gps/backend-app --platform managed --project ihp-gps
# gcloud datastore indexes create index.yaml --project=ihp-gps