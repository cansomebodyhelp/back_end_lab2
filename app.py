from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('configure.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Модели

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    categories = db.relationship('Category', backref='user', lazy=True)
    expenses = db.relationship('Expense', backref='user', lazy=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    expenses = db.relationship('Expense', backref='category', lazy=True)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

# Схемы

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    is_default = fields.Bool(default=False)
    user_id = fields.Int(allow_none=True)


class ExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True)
    date = fields.DateTime(default=datetime.utcnow)
    description = fields.Str()
    user_id = fields.Int(required=True)
    category_id = fields.Int(required=True)


# Роуты

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

    if category['is_default']:

        category = Category(
            name=category['name'],
            is_default=True,
            user_id=None
        )
    else:

        category = Category(
            name=category['name'],
            is_default=False,
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


@app.route('/expense', methods=['POST'])
def create_expense():
    data = request.get_json()
    try:
        expense_schema = ExpenseSchema()
        expense = expense_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400


    expense = Expense(
        amount=expense['amount'],
        date=expense.get('date', datetime.utcnow()),
        description=expense.get('description'),
        user_id=expense['user_id'],
        category_id=expense['category_id']
    )

    db.session.add(expense)
    db.session.commit()
    return expense_schema.dump(expense), 201


@app.route('/expenses', methods=['GET'])
def get_expenses():
    user_id = request.args.get("user_id", type=int)
    category_id = request.args.get("category_id", type=int)

    query = Expense.query

    if user_id:
        query = query.filter_by(user_id=user_id)

    if category_id:
        query = query.filter_by(category_id=category_id)

    expenses = query.all()
    expense_schema = ExpenseSchema(many=True)
    return jsonify(expense_schema.dump(expenses))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
