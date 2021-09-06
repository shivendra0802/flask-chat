from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient('mongodb+srv://admin:admin@chatapp.6jryt.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

chat_db = client.get_database('ChatDB')
users_collection = chat_db.get_collection('users')



def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})

# save_user("shivendra", "a@a.com", "test")

def get_user(username):
    user_data = users_collection.find_one({'_id': username})
    return User(user_data['id'], user_data['email'], user_data['password']) if user_data else None
    