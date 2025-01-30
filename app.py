# Initiate a flask app

from flask import Flask
from urllib.parse import quote as url_quote
from routes.user_route import bp_user

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(bp_user, url_prefix='/v2/app/user')

if __name__ == '__main__':
    app.run(debug=True, port=8080)