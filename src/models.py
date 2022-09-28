from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True)
    phone = db.Column(db.String(250))

    @classmethod
    def create(cls, body):
        """
            Crea una instancia y la devuelve. Si sucede un error en el proceso, se retorna el error en un diccionario
        """
        try:
            #Cuando usamos dict.get() obtenemos el valor de la llave indicada. Si la llave no existe, dict.get() nos retorna None por defecto (El valor de retorno puede ser cambiado)
            validated = cls.data_is_valid(name=body.get("name"), email=body.get("email"), phone=body.get("phone"))

            if type(validated) == dict: #Si validated es un diccionario, quiere decir que ocurrió un error
                raise Exception({ #Levantamos un error con la información del problema ocurrio. Este error es referente a la data o el email en específico
                    "message": validated["message"],
                    "status": validated["status"]
                })
            new_contact = cls(name=body["name"], email=body["email"], phone=body.get("phone", None)) #Creamos la instancia del Contacto

            if not isinstance(new_contact, cls):
                raise Exception({
                    "message": "Instance Error",
                    "status": 500
                })
            
            saved = new_contact.save_and_commit() #Salvamos la instancia creada en la sesion y le hacemos commit para crear el registro

            if not saved:
                raise Exception({
                    "message": "Data Base error",
                    "status": 500
                })
            return new_contact
        except Exception as error:
            #Retornamos el error que estamos levantando, el cual se estructuró como un diccionario con status y message como keys
            return error.args[0]

    @classmethod
    def data_is_valid(cls, **kwargs):
        """
            Verifica si la data enviada es correcta y está completa. También se verifica si el email es válido.
        """
        try:
            if kwargs["email"] is None:  #Si no nos enviaron un Email, levantamos un error.
                raise Exception({
                    "message": "Missing email",
                    "status": 400
                })
            if kwargs["name"] is None: #Si no nos enviaron un nombre, levantamos un error.
                raise Exception({
                    "message": "Missing name",
                    "status": 400
                })
            email_valid = cls.email_is_valid(kwargs["email"])
            if email_valid == False:  #Si el email existe en db, levantamos un error.
                raise Exception({
                    "message": "Invalid email",
                    "status": 400
                })
            if email_valid != True: #Si, email_valid es distinto de un booleano, existe un error en el servidor.
                raise Exception({
                    "message": "Server error",
                    "status": 500
                })
            
            return True
        except Exception as error:
            #Retornamos los errores
            return error.args[0]

        
    @classmethod
    def email_is_valid(cls, new_user_email):
        """
            Verifica si el email es válido. Sí el email existe en la base de datos, el email no es válido.
        """
        try:
            user_exist = cls.query.filter_by(email=new_user_email).one_or_none() #Consultamos en  la db si existe un registro con el email. Si existe, lo retorna. En caso contario, retorna None
            if user_exist:
                return False
            return True
        except Exception as error:
            return error.args[0]

    def save_and_commit(self):
        """
            Salva la instancia creada, en la base de datos. Si sucede algún error, 
            se retorna False y se revierten los cambios de la sesión
        """
        try:
            db.session.add(self)  #Guardamos la instancia en la sessión
            db.session.commit() #Creamos el registro en la db 
            return True
        except error:
            db.session.rollback() #Retornamos a la session mas reciente
            return False

    def serialize(self):
        """
            Convierte una instancia es un diccionario
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }

