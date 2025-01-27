import ollama

client = ollama.Client()
model = "vocability-lite"

async def chat(message: str) -> str:
    try:
        # Ollama chat is not async, so we use direct call
        response = client.chat(model=model, messages=[{
            'role': 'user',
            'content': message
        }])
        return response['message']['content']
    except Exception as e:
        raise Exception(f"Chat model error: {str(e)}")