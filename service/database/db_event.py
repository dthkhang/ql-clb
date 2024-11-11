import certifi,json
from bson import ObjectId
from pymongo import MongoClient
from bson import ObjectId  # Đảm bảo đã import ObjectId

ca = certifi.where()
url = f"mongodb+srv://khang:XGFfXtyekUExerWM@cluster0.nujj6h1.mongodb.net/"
connection = MongoClient(url,tlsCAFile=ca)
collection_user = connection['itskdvn']['user']
collection_event = connection['itskdvn']['event']



def get_event():
    # Lấy dữ liệu từ MongoDB
    data = list(collection_event.find({}))

    # Duyệt qua từng document trong data và chuyển ObjectId thành chuỗi
    for item in data:
        for key, value in item.items():
            # Nếu là ObjectId, chuyển sang chuỗi
            if isinstance(value, ObjectId):
                item[key] = str(value)
            # Nếu là danh sách, kiểm tra và chuyển từng phần tử nếu là ObjectId
            elif isinstance(value, list):
                item[key] = [str(v) if isinstance(v, ObjectId) else v for v in value]
            # Nếu là từ điển lồng nhau, duyệt và chuyển ObjectId thành chuỗi
            elif isinstance(value, dict):
                item[key] = {k: str(v) if isinstance(v, ObjectId) else v for k, v in value.items()}
    
    return data


def get_user_join_event(event_id):
    event = collection_event.find_one({'_id': ObjectId(event_id)})
    try:
        event = collection_event.find_one({'_id': ObjectId(event_id)})
        if event:
            return event['participants']
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None  # Nếu có lỗi xảy ra

def find_event(event_id):
    try:
        event = collection_event.find_one({'_id': ObjectId(event_id)})
        if event:
            return event
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None  # Nếu có lỗi xảy ra
    

def add_event(event_name,date,leader_id,location,des,status,participants):
    data_user = {
        "event_name": event_name,
        "leader_id":leader_id,
        "date":date,
        "location":location, 
        "des": des, 
        "status": status,
        "participants":participants}
    result_event_id = collection_event.insert_one(data_user)
    return result_event_id.inserted_id

def update_event(event_id, event_name, date, club_id, des):
    # Kiểm tra xem event_id có phải là chuỗi hợp lệ hay không
    if isinstance(event_id, str) and len(event_id) == 24:  # Kiểm tra chiều dài chuỗi
        try:
            object_id = ObjectId(event_id)
        except Exception as e:
            print(f"Invalid ObjectId format: {e}")
            return None  # Trả về None nếu ObjectId không hợp lệ
    else:
        print(f"Invalid event_id: {event_id}")
        return None  # Trả về None nếu event_id không hợp lệ

    # Tạo dữ liệu cần cập nhật
    update_data = {
        "event_name": event_name,
        "date": date,
        "club_id": club_id,
        "des": des
    }
    # Kiểm tra xem có dữ liệu để cập nhật không
    if update_data:
        # Tìm sự kiện hiện tại
        event = collection_event.find_one({"_id": object_id})
        if event:
            print("Current data:", event)
            # Kiểm tra sự thay đổi của dữ liệu
            if event["event_name"] != event_name or event["date"] != date or event["club_id"] != club_id or event["des"] != des:
                result = collection_event.update_one(
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
            print(f"Event with _id {event_id} not found.")
        return result
    else:
        return None  # Trả về None nếu không có tham số nào để update




