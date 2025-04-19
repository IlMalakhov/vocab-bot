from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_TOKEN")
    )

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
        • Teaches casually
        • Defines the target word clearly
        • Provides multiple short usage examples
        • Shares fun or interesting facts related to the word
        • Adds a mnemonic to help the user explain the word
        • Uses relevant, but trendy emojis to keep things fun
        Keep your responses short but insightful, and avoid going off-topic.
        """ 
            }
        ]

        messages.extend(conversation_history[user_id])
        messages.append({ "role": "user", "content": message })

        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://t.me/ElijahEnglishBot", # Optional. Site URL for rankings on openrouter.ai.
                "X-Title": "Vocab Bot", # Optional. Site title for rankings on openrouter.ai.
            },
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=messages
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
            extra_headers={
            "HTTP-Referer": "https://t.me/ElijahEnglishBot", # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "Vocab Bot", # Optional. Site title for rankings on openrouter.ai.
            },
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                { "role": "system", 
                "content": 
                f"""Please elaborate on the word '{word}'.
                The definition was already provided in the previous message. Do not provide the definition again.
                Try to provide multiple short usage examples, share fun or interesting facts related to the word, 
                and use relevant emojis to keep things fun. Add a small section with useful mnemonics or tips to remember the word.
                Keep your responses short but insightful, and avoid going off-topic.
                """
                }
            ]
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"vocability.py: error: {e}")

async def explain_stats(summary: dict) -> str:
    """Generates an AI explanation for the user's stats summary."""
    try:
        # Format the summary dictionary into a readable string for the AI
        summary_text = (
            f"Total words saved: {summary['total_words']}\\n"
            f"Days studying: {summary['days_studying']}\\n"
            f"Daily average: {summary['daily_average']:.1f}\\n"
            f"Words added today: {summary['words_today']}\\n"
            f"Words added this week: {summary['words_this_week']}\\n"
            f"Best day: {summary['best_day']['date']} with {summary['best_day']['count']} words"
        )

        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://t.me/ElijahEnglishBot",
                "X-Title": "Vocab Bot",
            },
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are Vocab Bot, a friendly English vocabulary tutor.
                    Explain the user's vocabulary learning statistics provided below in a friendly, concise, and encouraging way.
                    Offer insights based on their progress (e.g., consistency, recent activity).
                    Keep it short and positive, using relevant emojis. Don't just list the numbers back to the user.
                    """,
                },
                {
                    "role": "user",
                    "content": f"Here are my vocabulary learning stats:\n\n{summary_text}\n\nPlease explain them to me!"
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"vocability.py: explain_stats error: {e}")
        return "Sorry, I couldn't analyze the stats right now."