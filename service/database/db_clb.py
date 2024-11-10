import certifi
from bson import ObjectId
from pymongo import MongoClient
from bson import ObjectId  # Đảm bảo đã import ObjectId

ca = certifi.where()
url = f"mongodb+srv://khang:XGFfXtyekUExerWM@cluster0.nujj6h1.mongodb.net/"
connection = MongoClient(url,tlsCAFile=ca)
collection_user = connection['itskdvn']['user']
collection_clb = connection['itskdvn']['clb']

def get_event():
    data = list(collection_clb.find({}))
    return data

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



def update_event_to_user(mssv, clb_ids):
    # Kiểm tra event_ids có phải là danh sách không
    if isinstance(clb_ids, list):
        # Chuyển đổi tất cả các giá trị trong event_ids thành ObjectId nếu chưa phải ObjectId
        clb_ids = [ObjectId(clb_ids) if not isinstance(clb_ids, ObjectId) else clb_ids for clb_ids in clb_ids]
        # Cập nhật user với các event_id mới
        result = collection_user.update_one(
            {'mssv': mssv},  # Điều kiện tìm kiếm: user
            {'$addToSet': {'clb_id': {'$each': clb_ids}}}  # Thêm các event_id mà không trùng lặp
        )
        
        if result.modified_count > 0:
            return {"status": "success", "message": "Event IDs added successfully."}
        else:
            return {"status": "error", "message": "No updates made."}
    else:
        return {"status": "error", "message": "event_ids must be a list."}


