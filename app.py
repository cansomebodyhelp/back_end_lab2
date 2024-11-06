from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Бази даних для зберігання даних в пам'яті
users = {}
categories = {}
records = {}

# Маршрути для користувачів
@app.route('/', methods=['GET'])
def home():
    return "Єрмаков Богдан Романович  ІО-25", 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "Користувача не знайдено"}), 404
    return jsonify(user)

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id in users:
        del users[user_id]
        return jsonify({"message": "Користувача видалено"}), 200
    return jsonify({"error": "Користувача не знайдено"}), 404

@app.route('/user', methods=['POST'])
def create_user():
    name = request.args.get("name", type=str)
    if not name:
        return jsonify({"error": "Параметр name обов'язковий"}), 400

    user_id = len(users) + 1
    user = {"id": user_id, "name": name}
    users[user_id] = user
    return jsonify(user), 201

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))

# Маршрути для категорій

@app.route('/category', methods=['GET'])
def get_categories():
    return jsonify(list(categories.values()))

@app.route('/category', methods=['POST'])
def create_category():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Параметр name обов'язковий"}), 400

    category_id = len(categories) + 1
    category = {"id": category_id, "name": name}
    categories[category_id] = category
    return jsonify(category), 201

@app.route('/category/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    if category_id in categories:
        del categories[category_id]
        return jsonify({"message": "Категорію видалено"}), 200
    return jsonify({"error": "Категорію не знайдено"}), 404

# Маршрути для записів

@app.route('/record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    record = records.get(record_id)
    if not record:
        return jsonify({"error": "Запис не знайдено"}), 404
    return jsonify(record)

@app.route('/record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    if record_id in records:
        del records[record_id]
        return jsonify({"message": "Запис видалено"}), 200
    return jsonify({"error": "Запис не знайдено"}), 404

@app.route('/record', methods=['POST'])
def create_record():
    user_id = request.args.get("user_id", type=int)
    category_id = request.args.get("category_id", type=int)
    amount = request.args.get("amount", type=float)

    if user_id is None or category_id is None or amount is None:
        return jsonify({"error": "Параметри user_id, category_id та amount обов'язкові"}), 400

    record_id = len(records) + 1
    record = {
        "id": record_id,
        "user_id": user_id,
        "category_id": category_id,
        "timestamp": datetime.now().isoformat(),
        "amount": amount
    }
    records[record_id] = record
    return jsonify(record), 201

@app.route('/record', methods=['GET'])
def get_records():
    user_id = request.args.get("user_id", type=int)
    category_id = request.args.get("category_id", type=int)

    # Перевірка наявності параметрів
    if user_id is None and category_id is None:
        return jsonify({"error": "Вкажіть user_id або category_id"}), 400

    # Фільтрація записів
    filtered_records = [
        record for record in records.values()
        if (user_id is None or record["user_id"] == user_id) and
           (category_id is None or record["category_id"] == category_id)
    ]

    return jsonify(filtered_records)

if __name__ == '__main__':
    app.run(debug=True)
