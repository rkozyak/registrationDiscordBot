import json
from tracking import TrackRequest

from datetime import datetime
import threading

def load_request_list() -> list[TrackRequest]:
    try:
        with open("/var/data/saved_requests.json", 'r') as file:
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
                trackList.append(TrackRequest(item['crn'],item['term'],userIds,channelIds))
            threads = [threading.Thread(target=load_request,args=(item,)) for item in data]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            tend = datetime.now()
            tdelta = tend - tstart
            print(f"Loaded {len(trackList)} requests in {tdelta.total_seconds()}s")
            return trackList
    except:
        return []

def construct_request_dict(requests: list[TrackRequest]) -> dict[str, TrackRequest]:
    mapping = {}
    for request in requests:
        mapping[request.crn] = request
    return mapping

def construct_user_dict(requests: list[TrackRequest]) -> dict[str, list[str]]:
    mapping = {}
    for request in requests:
        for userId in request.userIds:
            if userId in mapping:
                mapping[userId].append(request.crn)
            else:
                mapping[userId] = [request.crn]
    return mapping

def save_request_list(trackList: list[TrackRequest]):
    json_obj = []
    for request in trackList:
        json_obj.append({
            'crn': request.crn,
            'term': request.term,
            'userIds': request.userIds,
            'channelIds': request.channelIds
        })
    json_encoded = json.dumps(json_obj)
    with open('/var/data/saved_requests.json', 'w') as file:
        file.write(json_encoded)