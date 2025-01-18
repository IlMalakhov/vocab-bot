import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import psycopg2
from typing import Final
import os
from dotenv import load_dotenv
from utils import db, stats_stuff

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_USERNAME: Final = '@ElijahEnglishBot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data["conn"]
    user_id = update.message.from_user.id
    try:
        with conn.cursor() as cursor:
            # Check if the user already exists in db
            cursor.execute(f"""
                           SELECT user_id
                           FROM user_words
                           WHERE user_id = {user_id};
                           """)
            result = cursor.fetchone()

            if result:
                # User exists
                await update.message.reply_text(
                    "*Welcome back\\!*\n"
                    "I will help you define and remember new vocabulary:\n\n"
                    "1\\. Type any word to get its definition\n"
                    "2\\. /mywords to see your wordlist\n\n"
                    "[Visit our bot's GitHub](https://github.com/IlMalakhov/vocab-bot)", 
                    parse_mode="MarkdownV2"
                    )
            else:
                # User does not exist
                cursor.execute("INSERT INTO user_words (user_id, words) VALUES (%s, %s);", (user_id, []))
                conn.commit()
                await update.message.reply_text(
                    "Nice to meet you, I'm Vocab Bot\\!\n"                    
                    "I will help you define and remember new vocabulary:\n\n"
                    "1\\. Type any word to get its definition\n"
                    "2\\. /mywords to see your wordlist\n\n"
                    "[Visit our bot's GitHub](https://github.com/IlMalakhov/vocab-bot)", 
                    parse_mode="MarkdownV2",
                    disable_web_page_preview=True
                    )
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Type any word to get its definition.\nUse /mywords to see your saved words.')

def get_definition(word):
    url = f"https://www.thefreedictionary.com/{word}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Error: Unable to fetch data for {word}"

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for the definition section in the HTML
    definition_sections = soup.find('div', {'class': 'ds-list'})
    if not definition_sections:
        return f"No definition found for {word}."

    # Collect all definitions
    definition_list = [definition.get_text().strip() for definition in definition_sections]

    return '\n'.join(definition_list)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if text:
        word = text.lower()
        definition = get_definition(word)
        if definition:
            # Create an inline button for adding the word
            keyboard = [
                [InlineKeyboardButton("Add Word", callback_data=f"add_{word}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(definition, reply_markup=reply_markup)
        else:
            await update.message.reply_text("Definition not found.")
    else:
        await update.message.reply_text("Please enter a valid word.")

async def add_word_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data["conn"]
    query = update.callback_query
    user_id = query.from_user.id

    # Extract the word from the callback data
    word = query.data.split('_', 1)[1]

    try:
        with conn.cursor() as cursor:
            # Check if the user already has an entry in the database
            cursor.execute(f"""
                           SELECT words 
                           FROM user_words 
                           WHERE user_id = {user_id};
                           """)
            result = cursor.fetchone()

            if result:
                words = result[0]
                if word not in words:
                    words.append(word)
                    cursor.execute("UPDATE user_words SET words = %s WHERE user_id = %s;", (words, user_id))
                    conn.commit()
                    await query.answer(f'Added "{word}" to your word list.')
                else:
                    await query.answer(f'"{word}" is already in your word list.')
            else:
                cursor.execute("INSERT INTO user_words (user_id, words) VALUES (%s, %s);", (user_id, [word]))
                conn.commit()
                await query.answer(f'Added "{word}" to your word list.')
    except Exception as e:
        await query.answer(f"An error occurred: {str(e)}")

async def mywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data["conn"]
    user_id = update.message.from_user.id

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT words FROM user_words WHERE user_id = %s;", (user_id,))
            result = cursor.fetchone()

            if result and result[0]:
                words = result[0]
                await update.message.reply_text("Your saved words:\n" + '\n'.join(words))
            else:
                await update.message.reply_text("You have no saved words.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ...

def main():
    application = Application.builder().token(TOKEN).build()
    conn = None

    try:
        conn = db.db_connect()
        application.bot_data["conn"] = conn

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("mywords", mywords_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(add_word_callback, pattern="^add_"))
        application.add_handler(CommandHandler("stats", stats_command))

        print("Bot started")
        application.run_polling()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if conn:
            db.db_close(conn)

if __name__ == "__main__":
    main()