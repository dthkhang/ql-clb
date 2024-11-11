import jwt
import datetime
from bson import ObjectId
SECRET_KEY = "your_secret_key"

def create_jwt(data,user):
    # Chuyển đổi ObjectId thành chuỗi
    data = [
        {k: str(v) if isinstance(v, ObjectId) else v for k, v in item.items()}
        for item in data
    ]
    expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    payload = {
        'data_user': data,
        'login_time': str(datetime.datetime.now()),
        'exp': expiration_time,
        'user':user
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def check_jwt(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"valid": True, "data": decoded_token}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Invalid token"}
    

