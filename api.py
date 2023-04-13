from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from flask_restx import Api, Namespace, Resource
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


user = "root"
passw = "123456"
host = "34.175.219.229"
database = "capstone_db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = host

#API key
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != 'capstone':
            print("API key missing or invalid") 
            return jsonify({'error': 'API key is missing or invalid'}), 403
        return f(*args, **kwargs)
    return decorated


#Create the connection
def connect():
    db = create_engine(
    'mysql+pymysql://{0}:{1}@{2}/{3}' \
        .format(user, passw, host, database), \
    connect_args = {'connect_timeout': 10})
    conn = db.connect()
    return conn

def disconnect(conn):
    conn.close()



# Creating the api V1
api = Api(app, version = '1.0',
    title = 'customers articile and transaction API',
    description = """
        API endpoints used to communicate data customers, articles 
        and  transaction sample
        between MySQL database and streamlit
        """,
    contact = "",
    endpoint = "/api/v1"
)


customers = Namespace(
    'customers',
    description = 'All the customers',
    path='/api/v1')
api.add_namespace(customers)

articles  = Namespace(
    'articles ',
    description = 'All the articles',
    path='/api/v2')
api.add_namespace(articles )

transactions = Namespace(
    'transactions_sample',
    description = 'All the transactions_sample',
    path='/api/v3')
api.add_namespace(transactions)

users = Namespace(
    'users',
    description='User authentication',
    path='/api/v4')
api.add_namespace(users)



#Authentication
@users.route("/register")
class Register(Resource):
    @require_api_key
    def post(self):
        try:
            conn = connect()
            data = request.get_json()
            hashed_password = generate_password_hash(data['password'], method='sha256')
            insert = f"""
                INSERT INTO users (username, password)
                VALUES ('{data['username']}', '{hashed_password}')
            """
            print("Executing INSERT statement:", insert)  # Add a print statement here
            conn.execute(insert)
            disconnect(conn)
            return {'message': 'User registered successfully'}, 201
        except Exception as e:
            print("Error during registration:", e)  # Add a print statement here
            return {'error': str(e)}, 400



@users.route("/login")
class Login(Resource):
    @require_api_key
    def post(self):
        try:
            conn = connect()
            data = request.get_json()
            user = conn.execute(f"SELECT * FROM users WHERE username = '{data['username']}'").fetchone()
            if user and check_password_hash(user['password'], data['password']):
                return {'message': 'Logged in successfully'}, 200
            else:
                return {'error': 'Invalid credentials'}, 401
        except Exception as e:
            return {'error': str(e)}, 400



@customers.route("/customers")
class get_all_customers(Resource):
    @require_api_key
    def get(self):
        try:
            conn = connect()
            select = """
                SELECT *
                FROM customers
                LIMIT 10000;"""
            result = conn.execute(select).fetchall()
            disconnect(conn)
            return jsonify({'result': [dict(row) for row in result]})
            
        except Exception as e:
            return jsonify({'error': str(e)})


@articles.route("/articles")
class get_all_articiless(Resource):
    @require_api_key
    def get(self):
        try:
            conn = connect()
            select = """
                SELECT *
                FROM articles
                LIMIT 10000;"""
            result = conn.execute(select).fetchall()
            disconnect(conn)
            return jsonify({'result': [dict(row) for row in result]})
        
        except Exception as e:
            return jsonify({'error': str(e)})


@transactions.route("/transactions")
class get_all_transaction(Resource):
    @require_api_key
    def get(self):
        try:
            conn = connect()
            select = """
                SELECT *
                FROM transactions
                LIMIT 10000;"""
            result = conn.execute(select).fetchall()
            disconnect(conn)
            return jsonify({'result': [dict(row) for row in result]})
        
        except Exception as e:
            return jsonify({'error': str(e)})


@transactions.route("/transactions/ageandclub")
@transactions.doc("To filter transactions by club member status and age range")
class filtered_transactions(Resource):
    @require_api_key
    def get(self):
        try:
            conn = connect()
            select = """
                SELECT t.*, c.age, c.club_member_status
                FROM transactions AS t
                JOIN customers AS c ON t.customer_id = c.customer_id
                LIMIT 10000"""
            result = conn.execute(select).fetchall()
            disconnect(conn)
            return jsonify({'result': [dict(row) for row in result]})
        
        except Exception as e:
            return jsonify({'error': str(e)})


@transactions.route("/transactions/productcategory")
@transactions.doc("To filter transactions by product category")
class filtered_transactions(Resource):
    @require_api_key
    def get(self):
        try:
            conn = connect()
            select = """
                SELECT t.*, a.product_category
                FROM transactions AS t
                JOIN articles AS a ON t.article_id = a.article_id
                LIMIT 10000;"""
            result = conn.execute(select).fetchall()
            disconnect(conn)
            return jsonify({'result': [dict(row) for row in result]})
        
        except Exception as e:
            return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080, debug=True, use_reloader=False)