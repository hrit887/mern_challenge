from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['transaction_db']
collection = db['transactions']

@app.route('/initialize-database', methods=['GET'])
def initialize_database():
    try:
        response = requests.get('https://s3.amazonaws.com/roxiler.com/product_transaction.json')
        transactions = response.json()

        # Clear existing data
        collection.delete_many({})

        # Insert new data
        collection.insert_many(transactions)

        return "Database initialized with seed data.", 200
    except Exception as e:
        return str(e), 500

@app.route('/transactions', methods=['GET'])
def list_transactions():
    month = request.args.get('month')
    search = request.args.get('search')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    query = {}
    if month:
        month_index = datetime.strptime(month, "%B").month
        query['dateOfSale'] = {'$regex': f'-{month_index:02d}-'}

    if search:
        search_regex = {'$regex': search, '$options': 'i'}
        query['$or'] = [
            {'title': search_regex},
            {'description': search_regex},
            {'price': search_regex}
        ]

    transactions = list(collection.find(query).skip((page - 1) * per_page).limit(per_page))
    total = collection.count_documents(query)

    return jsonify({
        'transactions': transactions,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total
        }
    }), 200

@app.route('/statistics', methods=['GET'])
def statistics():
    month = request.args.get('month')

    try:
        month_index = datetime.strptime(month, "%B").month

        total_sales = collection.aggregate([
            {'$match': {'dateOfSale': {'$regex': f'-{month_index:02d}-'}}},
            {'$group': {'_id': None, 'total': {'$sum': '$price'}}}
        ])

        sold_items = collection.count_documents({'sold': True, 'dateOfSale': {'$regex': f'-{month_index:02d}-'}})
        not_sold_items = collection.count_documents({'sold': False, 'dateOfSale': {'$regex': f'-{month_index:02d}-'}})

        return jsonify({
            'totalSaleAmount': list(total_sales)[0]['total'] if total_sales else 0,
            'totalSoldItems': sold_items,
            'totalNotSoldItems': not_sold_items
        }), 200
    except Exception as e:
        return str(e), 500

@app.route('/bar-chart', methods=['GET'])
def bar_chart():
    month = request.args.get('month')

    try:
        month_index = datetime.strptime(month, "%B").month
        price_ranges = [
            {"range": "0-100", "min": 0, "max": 100},
            {"range": "101-200", "min": 101, "max": 200},
            {"range": "201-300", "min": 201, "max": 300},
            {"range": "301-400", "min": 301, "max": 400},
            {"range": "401-500", "min": 401, "max": 500},
            {"range": "501-600", "min": 501, "max": 600},
            {"range": "601-700", "min": 601, "max": 700},
            {"range": "701-800", "min": 701, "max": 800},
            {"range": "801-900", "min": 801, "max": 900},
            {"range": "901-above", "min": 901, "max": float('inf')}
        ]

        result = []

        for price_range in price_ranges:
            count = collection.count_documents({
                'dateOfSale': {'$regex': f'-{month_index:02d}-'},
                'price': {'$gte': price_range['min'], '$lt': price_range['max']}
            })
            result.append({"range": price_range["range"], "count": count})

        return jsonify(result), 200
    except Exception as e:
        return str(e), 500

@app.route('/pie-chart', methods=['GET'])
def pie_chart():
    month = request.args.get('month')

    try:
        month_index = datetime.strptime(month, "%B").month

        categories = collection.aggregate([
            {'$match': {'dateOfSale': {'$regex': f'-{month_index:02d}-'}}},
            {'$group': {'_id': '$category', 'count': {'$sum': 1}}}
        ])

        result = [{"category": category['_id'], "count": category['count']} for category in categories]

        return jsonify(result), 200
    except Exception as e:
        return str(e), 500

@app.route('/combined-data', methods=['GET'])
def combined_data():
    month = request.args.get('month')

    try:
        statistics = requests.get(f'http://localhost:5000/statistics?month={month}').json()
        bar_chart = requests.get(f'http://localhost:5000/bar-chart?month={month}').json()
        pie_chart = requests.get(f'http://localhost:5000/pie-chart?month={month}').json()

        combined = {
            'statistics': statistics,
            'barChart': bar_chart,
            'pieChart': pie_chart
        }

        return jsonify(combined), 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
