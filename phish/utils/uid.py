import base64
import json


def encode_uid(user_id):
    user_id_bytes = json.dumps(user_id).encode('utf-8')
    return base64.urlsafe_b64encode(user_id_bytes).decode('utf-8')


def decode_uid(encoded_uid):
    user_id_bytes = base64.urlsafe_b64decode(encoded_uid.encode('utf-8'))
    return json.loads(user_id_bytes)
