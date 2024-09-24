from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yussuf.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.string(80), nullable= False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User

user_schema = UserSchema()
users_schema = UserSchema(many=True)

with app.app_context():
    db.create_all()

@app.route("/")
def route():
    return "This is my blog"

@app.route("/user/<int:id>")
def get_user(id):
    user = User.query.filter(User.id == id).first()
    return user_schema.dump(user)

@app.route("/users")
def get_users():
    all_users = User.query.all()
    return users_schema.dump(all_users), 200

@app.route("/users", methods=["POST"])
def add_user():
    username = request.json.get('username')
    email = request.json.get('email')

    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()

    return user_schema.dump(new_user), 201


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if user is None:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 204

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if user is None:
        return jsonify({"message": "User not found"}), 404

    username = request.json.get('username', user.username)
    email = request.json.get('email', user.email)

    user.username = username
    user.email = email
    db.session.commit()

    return user_schema.dump(user), 200



if __name__ == "__main__":
    app.run(debug=True)
