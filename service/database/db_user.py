import certifi
from bson import ObjectId

from pymongo import MongoClient
ca = certifi.where()
url = f"mongodb+srv://khang:XGFfXtyekUExerWM@cluster0.nujj6h1.mongodb.net/"
connection = MongoClient(url,tlsCAFile=ca)
collection = connection['itskdvn']['user']
findS = list(collection.find({}))

def find_user(user):
    data = list(collection.find({'user':user}))
    return data

def get_data_user():
    # Thêm điều kiện clb_id: "" và loại bỏ trường pwd
    data = list(collection.find(
        {'role': 0, 'clb_id': ""},  # Điều kiện lọc
        {'pwd': 0}  # Loại bỏ trường pwd
    ))

    # Chuyển đổi ObjectId sang chuỗi
    for item in data:
        if '_id' in item:
            item['_id'] = str(item['_id'])
    
    return data
def find_user_id(id):
    try:
        if isinstance(id, str):
            id = ObjectId(id)        
        data = collection.find_one({'_id': id})
        if data:
            return data  # Trả về kết quả nếu tìm thấy
        else:
            return None  # Trả về None nếu không tìm thấy user
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    

    
def add_user(user,pwd,role,email,phone,addr,mssv,lop,req_clb_id):
    data_user = {
        "user": user, 
        "pwd": pwd, 
        "phone":email, 
        "addr":phone, 
        "role": addr,
        "email":role,
        "mssv":mssv,
        "lop":lop,
        "clb_id":req_clb_id
    }
    collection.insert_one(data_user)

def update_user(user, email, phone, addr,event_id,clb_id,image):
    result = collection.update_one(
        {'user': user},  # Điều kiện tìm kiếm: user
        {'$set': {'email': email, 'phone': phone, 'addr': addr, 'event_id':event_id, 'clb_id':clb_id, 'image':image}}  # Cập nhật email, phone, addr
    )
    return result
 
def update_event_to_user(id, event_ids):
    # Kiểm tra event_ids có phải là danh sách không
    if isinstance(event_ids, list):
        # Chuyển đổi tất cả các giá trị trong event_ids thành ObjectId nếu chưa phải ObjectId
        event_ids = [ObjectId(event_id) if not isinstance(event_id, ObjectId) else event_id for event_id in event_ids]
        
        # Cập nhật user với các event_id mới
        result = collection.update_one(
            {'_id': ObjectId(id)},  # Điều kiện tìm kiếm: user
            {'$addToSet': {'event_id': {'$each': event_ids}}}  # Thêm các event_id mà không trùng lặp
        )
        
        if result.modified_count > 0:
            return {"status": "success", "message": "Event IDs added successfully."}
        else:
            return {"status": "error", "message": "No updates made."}
    else:
        return {"status": "error", "message": "event_ids must be a list."}