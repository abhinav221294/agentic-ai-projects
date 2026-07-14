import redis
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True)

def append_message(
        session_id : str,
        role: str,
        content: str
    ):
    
    key = f"session:{session_id}"

    message = {
        "role":role,
        "content":content
    }

    redis_client.rpush(key,
    json.dumps(message))

    redis_client.expire(
        key,
        60*60*24
    )
    
def get_messages(session_id: str):

    key = f"session:{session_id}"
    messages = redis_client.lrange(
        key,
        0,
        -1
    )

    return [
        json.loads(message)
        for message in messages
    ]

def clear_session(session_id: str):
    key = f"session:{session_id}"
    redis_client.delete(key)
