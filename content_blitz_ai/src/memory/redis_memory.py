import redis
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True)

def append_message(
        conversation_id : str,
        role: str,
        content: str
    ):
    
    key = f"session:{conversation_id}"

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
    
def get_messages(conversation_id: str):

    key = f"session:{conversation_id}"
    messages = redis_client.lrange(
        key,
        0,
        -1
    )

    return [
        json.loads(message)
        for message in messages
    ]

def clear_session(conversation_id: str):
    key = f"session:{conversation_id}"
    redis_client.delete(key)
