import os
from tracking import TrackRequest
from datetime import datetime
import threading
import json

# Define a directory to store the JSON file
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the directory exists
DATA_FILE = os.path.join(DATA_DIR, "saved_requests.json")

def load_request_list() -> list[TrackRequest]:
    try:
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            trackList = []
            tstart = datetime.now()
            def load_request(item):
                if 'userId' in item:
                    userIds = [item['userId']]
                    channelIds = [item['channelId']]
                else:
                    userIds = item['userIds']
                    channelIds = item['channelIds']
                trackList.append(TrackRequest(item['crn'], item['term'], userIds, channelIds))
            threads = [threading.Thread(target=load_request, args=(item,)) for item in data]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            tend = datetime.now()
            tdelta = tend - tstart
            print(f"Loaded {len(trackList)} requests in {tdelta.total_seconds()}s")
            return trackList
    except FileNotFoundError:
        print(f"{DATA_FILE} not found. Returning an empty request list.")
        return []

def save_request_list(trackList: list[TrackRequest]):
    json_obj = []
    for request in trackList:
        json_obj.append({
            'crn': request.crn,
            'term': request.term,
            'userIds': request.userIds,
            'channelIds': request.channelIds
        })
    json_encoded = json.dumps(json_obj, indent=4)
    with open(DATA_FILE, 'w') as file:
        file.write(json_encoded)

def construct_request_dict(requests: list[TrackRequest]) -> dict[str, TrackRequest]:
    """Construct a dictionary mapping CRNs to TrackRequest objects."""
    mapping = {}
    for request in requests:
        mapping[request.crn] = request
    return mapping

def construct_user_dict(requests: list[TrackRequest]) -> dict[str, list[TrackRequest]]:
    """Construct a dictionary mapping user IDs to lists of TrackRequest objects."""
    user_dict = {}
    for request in requests:
        for user_id in request.userIds:
            if user_id not in user_dict:
                user_dict[user_id] = []
            user_dict[user_id].append(request)
    return user_dict