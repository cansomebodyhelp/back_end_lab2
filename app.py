from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    categories = db.relationship('Category', backref='user', lazy=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)




class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    is_default = fields.Bool(default=False)
    user_id = fields.Int()




@app.route('/', methods=['GET'])
def home():
    return "Єрмаков Богдан Романович ІО-25", 200


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    try:
        user_schema = UserSchema()
        user = user_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = User(name=user['name'])
    db.session.add(user)
    db.session.commit()
    return user_schema.dump(user), 201


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))


@app.route('/category', methods=['POST'])
def create_category():
    data = request.get_json()
    try:
        category_schema = CategorySchema()
        category = category_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    category = Category(
        name=category['name'],
        is_default=category.get('is_default', False),
        user_id=category.get('user_id')
    )
    db.session.add(category)
    db.session.commit()
    return category_schema.dump(category), 201


@app.route('/categories', methods=['GET'])
def get_categories():
    user_id = request.args.get("user_id", type=int)
    if user_id:
        categories = Category.query.filter_by(user_id=user_id).all()
    else:
        categories = Category.query.filter_by(is_default=True).all()

    category_schema = CategorySchema(many=True)
    return jsonify(category_schema.dump(categories))


if __name__ == '__main__':
    app.run(debug=True)
