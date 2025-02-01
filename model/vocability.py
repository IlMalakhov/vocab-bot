from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(api_key=os.getenv("HF_TOKEN"))

conversation_history = {}
MAX_HISTORY = 10

async def chat(message: str, user_id: int) -> str:
    try:

        if user_id not in conversation_history:
            conversation_history[user_id] = []

        messages = [
            { "role": "system", 
            "content": """
        Your name is Vocab Bot. You are a friendly and concise English vocabulary tutor who:
        • Greets students casually
        • Defines the target word clearly
        • Provides multiple short usage examples
        • Shares fun or interesting facts related to the word
        • Uses relevant emojis to keep things fun
        Keep your responses short but insightful, and avoid going off-topic. Do not use markdown or code blocks.
        """ 
            }
        ]

        messages.extend(conversation_history[user_id])
        messages.append({ "role": "user", "content": message })

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct",
            messages=messages,
            temperature=0.8,
            max_tokens=150,
            top_p=0.7
        )

        # Update history
        conversation_history[user_id].append({"role": "user", "content": message})
        conversation_history[user_id].append({"role": "assistant", "content": response.choices[0].message.content})
        
        # Trim history
        if len(conversation_history[user_id]) > MAX_HISTORY * 2:
            conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY * 2:]

        return response.choices[0].message.content
    except Exception as e:
        print(f"vocability.py: error: {e}")

async def elaborate(word: str) -> str:
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct",
            messages=[
                { "role": "system", 
                "content": 
                f"""Please elaborate on the word '{word}'.
                The definition was already provided in the previous message. 
                Try to provide multiple short usage examples, share fun or interesting facts related to the word, 
                and use relevant emojis to keep things fun. Add a small section with useful mnemonics or tips to remember the word.
                Do not use markdown or code blocks.
                """
                }
            ],
            temperature=0.8,
            max_tokens=150,
            top_p=0.7
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"vocability.py: error: {e}")