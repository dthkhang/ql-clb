import certifi,json
from bson import ObjectId
from pymongo import MongoClient
from bson import ObjectId  # Đảm bảo đã import ObjectId

ca = certifi.where()
url = f"mongodb+srv://khang:XGFfXtyekUExerWM@cluster0.nujj6h1.mongodb.net/"
connection = MongoClient(url,tlsCAFile=ca)
collection_user = connection['itskdvn']['user']
collection_clb = connection['itskdvn']['clb']

def get_clb():
    # Lấy dữ liệu từ MongoDB và chuyển đổi ObjectId thành chuỗi
    data = list(collection_clb.find({}))
    for item in data:
        if '_id' in item and isinstance(item['_id'], ObjectId):
            item['_id'] = str(item['_id'])
        if 'leader_id' in item and isinstance(item['leader_id'], ObjectId):
            item['leader_id'] = str(item['leader_id'])
    return data


def delete_clb_by_id(clb_id):
    # Kiểm tra nếu event_id là một ObjectId hợp lệ
    if not ObjectId.is_valid(clb_id):
        return {"error": "Invalid ID format"}
    
    # Kiểm tra xem event có tồn tại hay không
    clb_object_id = ObjectId(clb_id)
    clb = collection_clb.find_one({"_id": clb_object_id})
    print(clb)
    result = collection_clb.delete_one({"_id": clb_object_id})
    if clb is None:
        return {"error": "CLB not found"}
    
    # Kiểm tra nếu có participants và xử lý trường hợp participants là None hoặc danh sách rỗng
    participants = clb.get("participants", None)
    if participants is None:
        return {"error": "No participants found"}
    elif len(participants) == 0:
        return {"error": "No participants found"}
    
    # Xóa sự kiện khỏi MongoDB
    result = collection_clb.delete_one({"_id": clb_object_id})
    
    if result.deleted_count > 0:
        return {"message": "Event deleted successfully"}
    else:
        return {"error": "Event could not be deleted"}
    

def find_clb(clb_id):
    try:
        clb = collection_clb.find_one({'_id': ObjectId(clb_id)})
        if clb:
            return clb
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None  # Nếu có lỗi xảy ra
    


def get_user_join_clb(clb_id):
    try:
        # Tìm tất cả các user có clb_id chứa chuỗi clb_id
        users = collection_user.find({'clb_id': clb_id}, {'user': 1, 'email': 1, 'phone': 1, 'mssv': 1, 'lop': 1})
        
        # Chuyển đổi kết quả thành danh sách và thay đổi ObjectId thành chuỗi nếu cần
        user_list = []
        for user in users:
            user['_id'] = str(user['_id'])  # Chuyển đổi ObjectId của _id thành chuỗi nếu muốn giữ _id
            user_list.append(user)
        return user_list  # Trả về danh sách các user với trường cần thiết
    except Exception as e:
        print(f"Error: {e}")
        return None



def add_clb(clb_name,leader_id,date,des):
    data_clb = {"name": clb_name, "leader_id":leader_id, "date":date,"des": des}
    collection_clb.insert_one(data_clb)



def update_clb(clb_id, clb_name, leader_id,member_id, des):
    # Kiểm tra xem event_id có phải là chuỗi hợp lệ hay không
    if isinstance(clb_id, str) and len(clb_id) == 24:  # Kiểm tra chiều dài chuỗi
        try:
            object_id = ObjectId(clb_id)
        except Exception as e:
            print(f"Invalid ObjectId format: {e}")
            return None  # Trả về None nếu ObjectId không hợp lệ
    else:
        print(f"Invalid event_id: {clb_id}")
        return None  # Trả về None nếu event_id không hợp lệ

    # Tạo dữ liệu cần cập nhật
    update_data = {
        "clb_name": clb_name,
        "leader_id": leader_id,
        "member_id": member_id,
        "des": des
    }
    if update_data:
        clb = collection_clb.find_one({"_id": object_id})
        if clb:
            print("Current data:", clb)
            # Kiểm tra sự thay đổi của dữ liệu
            if clb["clb_name"] != clb_name or clb["leader_id"] != leader_id or clb["member_id"] != member_id or clb["des"] != des:
                result = collection_clb.update_one(
                    {'_id': object_id},  # Tìm sự kiện theo _id
                    {'$set': update_data}  # Cập nhật các trường có giá trị
                )
                print(f"Matched count: {result.matched_count}")
                print(f"Modified count: {result.modified_count}")
                if result.modified_count > 0:
                    print("Successfully updated event.")
                else:
                    print("No changes made to the event.")
            else:
                print("No changes detected.")
        else:
            print(f"Event with _id {clb_id} not found.")
        return result
    else:
        return None  # Trả về None nếu không có tham số nào để update



def update_clb_to_user(mssv, clb_id):
    try:
        # Kiểm tra nếu clb_id là chuỗi, nếu không, không làm gì
        if isinstance(clb_id, str):
            # Tìm người dùng theo mssv
            user = collection_user.find_one({'mssv': mssv})

            if user:
                # Kiểm tra nếu clb_id hiện tại là chuỗi
                current_clb_id = user.get('clb_id', "")

                # Nối chuỗi mới vào clb_id hiện tại (nếu có) với dấu phân cách
                if current_clb_id:
                    updated_clb_id = current_clb_id + "," + clb_id  # Nối với dấu ',' giữa các ID
                else:
                    updated_clb_id = clb_id  # Nếu không có clb_id trước đó, chỉ thêm clb_id mới

                # Cập nhật clb_id mới vào user
                result = collection_user.update_one(
                    {'mssv': mssv},  # Điều kiện tìm kiếm: user với mssv
                    {'$set': {'clb_id': updated_clb_id}}  # Cập nhật lại clb_id với giá trị nối mới
                )

                if result.modified_count > 0:
                    return {"status": "success", "message": "CLB ID added successfully."}
                else:
                    return {"status": "error", "message": "No updates made."}
            else:
                return {"status": "error", "message": "User not found."}
        else:
            return {"status": "error", "message": "CLB ID must be a string."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_clb_to_user(mssv, clb_id):
    try:
        # Kiểm tra nếu clb_id là chuỗi, nếu không, không làm gì
        if isinstance(clb_id, str):
            # Tìm người dùng theo mssv
            user = collection_user.find_one({'mssv': mssv})

            if user:
                # Cập nhật clb_id thành chuỗi rỗng
                result = collection_user.update_one(
                    {'mssv': mssv},  # Điều kiện tìm kiếm: user với mssv
                    {'$set': {'clb_id': ''}}  # Cập nhật clb_id thành chuỗi rỗng
                )

                if result.modified_count > 0:
                    return {"status": "success", "message": "CLB ID updated successfully."}
                else:
                    return {"status": "error", "message": "No updates made."}
            else:
                return {"status": "error", "message": "User not found."}
        else:
            return {"status": "error", "message": "CLB ID must be a string."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    


