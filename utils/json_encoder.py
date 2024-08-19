from bson import ObjectId
import json

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def parse_json(data):
    return json.loads(json.dumps(data, cls=MongoJSONEncoder))