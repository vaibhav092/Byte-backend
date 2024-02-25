from flask import Flask, request
from flask_restful import Api, Resource
import jwt

app = Flask(__name__)
api = Api(app)

users = []
poems = []

app.config['SECRET_KEY'] = 'your_secret_key'

class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if any(user['email'] == email for user in users):
            return {'message': 'User with this email already exists'}, 400

        new_user = {'name': name, 'email': email, 'password': password}
        users.append(new_user)

        return {'message': 'User registered successfully'}, 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = next((user for user in users if user['email'] == email), None)
        if user and user['password'] == password:
            access_token = jwt.encode({'email': email}, app.config['SECRET_KEY'], algorithm='HS256')
            refresh_token = jwt.encode({'email': email}, app.config['SECRET_KEY'], algorithm='HS256')
            return {'access': access_token, 'refresh': refresh_token}, 200
        else:
            return {'message': 'Invalid email or password'}, 401

class UserDetails(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Token is missing'}, 401

        try:
            decoded_token = jwt.decode(token.split()[1], app.config['SECRET_KEY'], algorithms=['HS256'])
            email = decoded_token.get('email')
            user = next((user for user in users if user['email'] == email), None)
            if user:
                return {'id': user.get('id'), 'email': user.get('email'), 'name': user.get('name'), 'number': user.get('number', ''), 'role': user.get('role', '')}, 200
            else:
                return {'message': 'User not found'}, 404
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

class PoemList(Resource):
    def get(self):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Token is missing'}, 401

        try:
            decoded_token = jwt.decode(token.split()[1], app.config['SECRET_KEY'], algorithms=['HS256'])
            email = decoded_token.get('email')
            user_poems = [poem for poem in poems if poem['user_email'] == email]
            return user_poems, 200
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

class CreatePoem(Resource):
    def post(self):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Token is missing'}, 401

        try:
            decoded_token = jwt.decode(token.split()[1], app.config['SECRET_KEY'], algorithms=['HS256'])
            email = decoded_token.get('email')

            data = request.get_json()
            poem_text = data.get('poem')
            author = data.get('author')

            new_poem = {'poem': poem_text, 'author': author, 'user_email': email}
            poems.append(new_poem)

            return {'message': 'Poem created successfully'}, 201
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

api.add_resource(UserRegistration, '/auth/register/')
api.add_resource(UserLogin, '/auth/login/')
api.add_resource(UserDetails, '/auth/user-details/')
api.add_resource(PoemList, '/poem/get/')
api.add_resource(CreatePoem, '/poem/create/')

if __name__ == '__main__':
    app.run(debug=True)
