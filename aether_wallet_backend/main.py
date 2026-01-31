from flask import Flask
# from routes.user import auth_bp
from routes.user import auth_bp
from routes.balance import balance_bp
from routes.category import category_bp
from routes.report import report_bp
from routes.contact import contact_bp
from routes.lending_transection import lending_bp
from bson import ObjectId
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app = Flask(__name__)

app.json_encoder = JSONEncoder

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(balance_bp, url_prefix='/balance')
app.register_blueprint(category_bp, url_prefix='/category')
app.register_blueprint(report_bp, url_prefix='/report')
app.register_blueprint(contact_bp, url_prefix='/contact')
app.register_blueprint(lending_bp, url_prefix='/lending')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


# to run : main.py