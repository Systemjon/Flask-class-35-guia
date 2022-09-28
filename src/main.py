"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Contact
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route("/contact", methods=['POST'])
def create():
    """ 
        Crea una instancia y la almacena en la base de datos. En caso ocurra un error en el proceso, se returna el error correspondiente
    """
    body = request.json
    new_contact = Contact.create(body) #Creamos la instancia ejecutando el método de clase creado en models

    if not isinstance(new_contact, Contact): #Si no es una instancia de Contact, quiere decir que ocurrió un error
        print(new_contact)
        return jsonify({
            "message": new_contact["message"]
        }), new_contact["status"]

    contact = Contact.query.filter_by(email=new_contact.email).one_or_none()  #Obtenemos el contacto para acceder al id, el cual es generado luego de que la instancia se guarda en la base de datos.
    return jsonify({
        "id":  contact.id,
        "name": contact.name
    }), 201


@app.route("/v2/contact", methods=["POST"])
def handle_contact():
    """ 
        Crea una instancia y la devuelve
    """
    body = request.json
    
    if body.get("phone") is None:
        return jsonify({
            "message": "Missing phone"
        }), 400

    if body.get("name") is None:
        return jsonify({
            "message": "Missing name"
        }), 400

    if body.get("email") is None:
        return jsonify({
            "message": "Missing email"
        }), 400
    
    email_exist = Contact.query.filter_by(email=body.get("email")).one_or_none()
    if email_exist:
        return jsonify({
            "message": "Email alredy exists"
        }), 400

    new_contact = Contact(name=body["name"], email=body["email"], phone=body["phone"])
    
    if not isinstance(new_contact, Contact):
        return jsonify({
            "message": "An error occur",
        }), 500
    new_contact.save_and_commit()   
    contact = Contact.query.filter_by(email=new_contact.email).one()
    return jsonify({
        "id": contact.id,
        "name": contact.name
    }), 201




# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
