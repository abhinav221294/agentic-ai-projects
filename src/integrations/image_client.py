import openai

client = openai()

def generate_image(
        prompt: str,
        model: str = "gpt-image-1",
        size: str = "1024x1024"):
    
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size
    )

    return response.data[0].url
    


