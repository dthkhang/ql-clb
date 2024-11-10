import jwt
import datetime
SECRET_KEY = "your_secret_key"
def create_jwt(user):
    expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    payload = {
        'user': user,
        'login_time': str(datetime.datetime.now()),
        'exp': expiration_time 
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
    
token = create_jwt("admin")
result = check_jwt(token)
if result["valid"]:
    print(result["data"]["user"])  # Lấy ra "user" từ "data"
else:
    print("Error:", result["error"])
