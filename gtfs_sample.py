import requests
from google.transit import gtfs_realtime_pb2
def GTFS_info():
    information = {}
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get('http://api.511.org/Transit/VehiclePositions/?api_key=9e3a621e-a037-46a3-a13c-d1894dc9d339&agency=AC')
    feed.ParseFromString(response.content)
    print(feed.entity)
    for entity in feed.entity:
        temp = []
        temp.append(entity.vehicle.position.latitude)
        temp.append(entity.vehicle.position.longitude)
        information[entity.id] = temp
    return information
