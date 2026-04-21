def get_memory():
    return []

def update_memory(memory, query, response):
    memory.append({
        "user": query,
        "assistant": response
    })
    return memory