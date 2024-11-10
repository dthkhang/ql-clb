import certifi
from werkzeug.security import check_password_hash
from pymongo import MongoClient
ca = certifi.where()
url = f"mongodb+srv://khang:XGFfXtyekUExerWM@cluster0.nujj6h1.mongodb.net/"
connection = MongoClient(url,tlsCAFile=ca)
collection = connection['itskdvn']['user']
findS = list(collection.find({}))



def login_check(req_user,req_pwd):
    data_user = list(collection.find({'user': req_user}, {'pwd': 1}))
    if data_user:
        pwd = data_user[0].get('pwd')
        if req_pwd == pwd:
            return True
        else: return False
    else: 
        return False