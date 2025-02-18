# Initiate a flask app

from flask import Flask
from flask_cors import CORS
from urllib.parse import quote as url_quote
from routes.user_route import bp_user
from routes.routes import bp_route

app = Flask(__name__)
CORS(app)
# Register the blueprint
app.register_blueprint(bp_user, url_prefix='/v2/app/user')
app.register_blueprint(bp_route, url_prefix='/v2/app/route')

if __name__ == '__main__':
    app.run(debug=True, port=8080)

# gcloud builds submit --tag gcr.io/ihp-rpp/backend-app --project ihp-rpp
# gcloud run deploy --image gcr.io/ihp-rpp/backend-app --platform managed --project ihp-rpp