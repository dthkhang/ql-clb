from flask import Flask, request, redirect, render_template, session, url_for, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from service.database.db_user import find_user,add_user, update_user, update_event_to_user, find_user_id
from service.database.db_event import update_event,find_event, add_event, get_user_join_event, get_event
from service.database.db_clb import update_clb,find_clb, add_clb,update_clb_to_user, get_user_join_clb, get_clb
from service.authen import login_check
from service.jwt.jwt_service import create_jwt,check_jwt
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.secret_key = 'secret_key_here'  # Đặt một khóa bí mật cho session

# Cấu hình MongoDB
app.config["MONGO_URI"] = "mongodb+srv://khang:XGFfXtyekUExerWM@cluster0.nujj6h1.mongodb.net/itskdvn"
mongo = PyMongo(app)

@app.route('/api/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data_request = request.json
        req_user = data_request.get('user')
        req_pwd = data_request.get('pwd')
        req_email = data_request.get('email')
        req_phone = data_request.get('phone')
        req_addr = data_request.get('addr')
        req_mssv = data_request.get('mssv')
        req_lop = data_request.get('lop')
        req_clb_id = data_request.get('clb_id')
        role = 0
        if find_user(req_user):
            return jsonify({"error": "username already exists!"}), 409
        add_user(req_user,req_pwd,req_email,req_phone,req_addr,role,req_mssv,req_lop,req_clb_id)
        return jsonify({"noti": "success!"}), 200
    return jsonify({"error": "Method not allowed"}), 405

@app.route('/api/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data_request = request.json
        req_user = data_request.get('user')
        req_pwd = data_request.get('pwd')
        if login_check(req_user,req_pwd):
            session['username'] = req_user
            data = find_user(req_user)
            jwt_token = create_jwt(data,req_user)
            return jsonify({"noti": "login success!","token":jwt_token}), 200
        return jsonify({"error": "incorrect username or password!"}), 401
    return jsonify({"error": "Method not allowed"}), 405
#########################################################################################################

@app.route('/api/update/user', methods=['POST'])
def api_update_user():
    if request.method == 'POST':
        data_request = request.json
        try:
            jwt_header = request.headers['Token']
            check_token = check_jwt(jwt_header)
            print(str(check_token))
            if check_token["valid"]:
                jwt_user = check_token["data"]["user"] # Lấy ra "user" từ "data"
                if find_user(jwt_user):
                    req_email = data_request.get('email')
                    req_phone = data_request.get('phone')
                    req_addr = data_request.get('addr')
                    req_event_id = data_request.get('event_id')
                    req_clb_id = data_request.get('clb_id')
                    req_image = data_request.get('img')
                    update_user(jwt_user,req_email,req_phone,req_addr,req_event_id,req_clb_id,req_image)
                    return jsonify({"noti": "update success!"}), 200
                else:
                    return jsonify({"error": "you need jwt token for do this-1!"}), 401
        except: return jsonify({"error": "you need jwt token for do this-2!"}), 401
    return jsonify({"error": "Method not allowed"}), 401

#######################################################################################################################################

@app.route('/api/add/event', methods=['POST']) ##DONE
def api_add_event():
    if request.method == 'POST':
        data_request = request.json
        try:
            jwt_header = request.headers['Token']
            check_token = check_jwt(jwt_header)
            if check_token["valid"]:
                    jwt_user = check_token["data"]["user"] # Lấy ra "user" từ "data"
                    if find_user(jwt_user):
                        req_event_name = data_request.get('name')
                        req_date = data_request.get('dateTime')
                        req_local = data_request.get('location')
                        req_des = data_request.get('description')
                        req_status = data_request.get('status')
                        req_participants = data_request.get('participants')
                        leader_id = find_user(jwt_user)
                        if leader_id:
                            leader_id_value = leader_id[0]['_id']
                        result_event_id = add_event(req_event_name,req_date,leader_id_value,req_local,req_des,req_status,req_participants) ## add event, lấy ra event id
                        if req_participants and len(req_participants) > 0:
                            for participant in req_participants:
                                member_id = participant.get('member_id')  # Lấy member_id của từng participant
                                update_event_to_user(member_id, [result_event_id])  # Cập nhật event_id cho từng member_id
                            return jsonify({"noti": "update success!"}), 200
                        else:
                            return jsonify({"error": "No participants found"}), 400
                    else: return jsonify({"error"}), 403
            else:
                return jsonify({"error": "you need jwt token for do thisx!"}), 401
        except: return jsonify({"error": "you need jwt token for do thisy!"}), 401
    return jsonify({"error": "Method not allowed"}), 405

@app.route('/api/update/event', methods=['POST'])
def api_update_event():
    if request.method == 'POST':
        data_request = request.json
        req_event_id = data_request.get('_id')
        req_event_name = data_request.get('event_name')
        req_leaderid = data_request.get('leaderid')
        req_date = data_request.get('date')
        req_club_id = data_request.get('club_id')
        req_des = data_request.get('des')
        jwt_header = request.headers['Token']
        check_token = check_jwt(jwt_header)
        if check_token["valid"]:
                jwt_user = check_token["data"]["user"] # Lấy ra "user" từ "data"
                if find_user(jwt_user):
                    ev_id = find_event(req_event_id)
                    if str(req_event_id) == str(ev_id['_id']):
                        update_event(ev_id['_id'],str(req_event_name),str(req_date),str(req_club_id),str(req_des))
                        return jsonify({"noti": "update success!"}), 200
                    else: return jsonify({"noti": "error!"}), 403
        else:
                return jsonify({"error": "you need jwt token for do thisx!"}), 401
    return jsonify({"error": "Method not allowed"}), 405

@app.route('/api/get/event/member', methods=['POST'])
def get_event_member():
    if request.method == 'POST':
        data_request = request.json
        req_event_id = data_request.get('_id')
        data = get_user_join_event(req_event_id)
        return jsonify(data),200
    return jsonify({"error": "Method not allowed"}), 405

@app.route('/api/get/event', methods=['GET'])
def api_get_event():
    if request.method == 'GET':
        data = get_event()
        return jsonify(data),200
    return jsonify({"error": "Method not allowed"}), 405

#############################################################################################################################
@app.route('/api/add/clb', methods=['POST'])
def api_add_clb():
    if request.method == 'POST':
        data_request = request.json
        try:
            jwt_header = request.headers['Token']
            check_token = check_jwt(jwt_header)
            if check_token["valid"]:
                jwt_user = check_token["data"]["user"] # Lấy ra "user" từ "data"
                if find_user(jwt_user):
                    req_clb_name = data_request.get('clb_name')
                    req_des = data_request.get('des')
                    req_date = data_request.get('date')
                    leader_id = find_user(jwt_user)
                    if leader_id:
                        leader_id = leader_id[0]['_id']
                    add_clb(req_clb_name,leader_id,req_date,req_des)
                    return jsonify({"noti": "update success!"}), 200
                else: return jsonify({"noti": "error!"}), 403
            else:
                return jsonify({"error": "you need jwt token for do thisx!"}), 401
        except: return jsonify({"error": "you need jwt token for do thisy!"}), 401
    return jsonify({"error": "Method not allowed"}), 405

@app.route('/api/add/clb/member', methods=['POST'])
def api_add_member_clb():
    if request.method == 'POST':
        data_request = request.json
        try:
            jwt_header = request.headers['Token']
            check_token = check_jwt(jwt_header)
            if check_token["valid"]:
                jwt_user = check_token["data"]["user"] # Lấy ra "user" từ "data"
                if find_user(jwt_user):
                    req_mssv = data_request.get('mssv')
                    req_clb_id = data_request.get('clb_id')
                    update_clb_to_user(req_mssv,req_clb_id)
                    return jsonify({"noti": "update success!"}), 200
                else: return jsonify({"noti": "error!"}), 403
            else:
                return jsonify({"error": "you need jwt token for do thisx!"}), 401
        except: return jsonify({"error": "you need jwt token for do thisy!"}), 401
    return jsonify({"error": "Method not allowed"}), 405

@app.route('/api/get/clb/member', methods=['POST'])
def get_clb_member():
    if request.method == 'POST':
        data_request = request.json
        req_clb_id = data_request.get('clb_id')
        data = get_user_join_clb(req_clb_id)
        return jsonify(data),200
    return jsonify({"error": "Method not allowed"}), 405

@app.route('/api/get/clb', methods=['GET'])
def api_get_clb():
    if request.method == 'GET':
        data = get_clb()
        print(data)
        return jsonify(data),200
    return jsonify({"error": "Method not allowed"}), 405


# @app.route('/api/update/clb', methods=['POST'])
# def api_update_clb():
#     print(request.method)
#     if request.method == 'POST':
#         data_request = request.json
#         req_clb_id = data_request.get('_id')
#         req_clb_name = data_request.get('event_name')
#         leader_id = data_request.get('leader_id')
#         req_member_id = data_request.get('member_id')
#         req_des = data_request.get('des')
#         jwt_header = request.headers['Token']
#         check_token = check_jwt(jwt_header)
#         if check_token["valid"]:
#                 jwt_user = check_token["data"]["user"] # Lấy ra "user" từ "data"
#                 if find_user(jwt_user):
#                     ev_id = find_clb(req_clb_id)
#                     if str(req_clb_id) == str(ev_id['_id']):
#                         update_clb(ev_id['_id'],str(req_clb_name),str(leader_id),str(req_member_id),str(req_des))
#                         return jsonify({"noti": "update success!"}), 200
#                     else: return jsonify({"error"}), 200
#         else:
#                 return jsonify({"error": "you need jwt token for do thisx!"}), 401
#     return jsonify({"error": "Method not allowed"}), 405





if __name__ == '__main__':
    app.run(host="127.0.0.1", port=1337, debug=True)
