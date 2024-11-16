import json
from tracking import TrackRequest


def load_request_list() -> list[TrackRequest]:
    try:
        with open("/var/data/saved_requests.json", 'r') as file:
            data = json.load(file)
            trackList = []
            for item in data:
                trackList.append(TrackRequest(item['crn'],item['term'],item['userId'],item['channelId']))
            return trackList
    except:
        return []

def save_request_list(trackList: list[TrackRequest]):
    json_obj = []
    for request in trackList:
        json_obj.append({
            'crn': request.crn,
            'term': request.term,
            'userId': request.userId,
            'channelId': request.channelId
        })
    json_encoded = json.dumps(json_obj)
    with open('/var/data/saved_requests.json', 'w') as file:
        file.write(json_encoded)