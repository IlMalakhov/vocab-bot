# Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# OS
import os
from dotenv import load_dotenv

# Utilities
from utils import db, definitions, stats_stuff

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_USERNAME = '@ElijahEnglishBot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data["conn"]
    user_id = update.message.from_user.id
    try:
        with conn.cursor() as cursor:
            # Check if the user already exists in db
            cursor.execute("""
                           SELECT user_id 
                           FROM users 
                           WHERE user_id = %s;""", (user_id,))

            result = cursor.fetchone()

            if result:
                # User exists
                await update.message.reply_text(
                    "*Welcome back\\!* ☀️\n\n"
                    "I will help you define and remember new vocabulary 📖\n\n"
                    "1\\. Type any word to get its definition 💬\n"
                    "2\\. /mywords to see your wordlist 📚\n\n"
                    "_I can do a lot more, just use_ */help* _and see for yourself_ 🎉\n\n\n"
                    "Also, check out [our bot's GitHub](https://github.com/IlMalakhov/vocab-bot) to take a peek under the hood ⚙️", 
                    parse_mode="MarkdownV2")
            else:
                # User does not exist
                cursor.execute("INSERT INTO users (user_id) VALUES (%s);", (user_id,))
                conn.commit()
                await update.message.reply_text(
                    "Nice to meet you, I'm Vocab Bot\\! ☀️\n\n"                    
                    "I will help you define and remember new vocabulary 📖\n\n"
                    "1\\. Type any word to get its definition 💬\n"
                    "2\\. /mywords to see your wordlist 📚\n\n"
                    "_I can do a lot more, just use_ */help* _and see for yourself_ 🎉\n\n\n" 
                    "Also, check out [our bot's GitHub](https://github.com/IlMalakhov/vocab-bot) to take a peek under the hood 🛠️", 
                    parse_mode="MarkdownV2",
                    disable_web_page_preview=True)

    except Exception as e:
        print(f"Error fetching or inserting info about the user: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Type any word to get its definition 📖\n\n"
        "Save words by tapping *Add word* under the definition\n\n"
        "• */word\\_stream* to learn random new words 🎲\n"
        "• */mywords* to see your saved words 📚\n"
        "• */stats* to see your progress 📊",
        parse_mode="MarkdownV2")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text:
        word = text.lower()
        definition = definitions.get_definition(word)

        if definition:
            # Create an inline button for adding the word
            keyboard = [[InlineKeyboardButton("Add Word", callback_data=f"add_{word}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(definition, reply_markup=reply_markup)
        else:
            await update.message.reply_text("I coudnt't find the definition for that...")
    else:
        await update.message.reply_text("Something seems wrong with the word you sent me...")

async def add_word_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data["conn"]
    query = update.callback_query
    user_id = query.from_user.id

    # Extract the word from the callback data
    word = query.data.split('_', 1)[1]
    word = word.strip().lower()

    try:
        with conn.cursor() as cursor:
            # Ensure the word exists in the words table
            cursor.execute("INSERT INTO words (word) VALUES (%s) ON CONFLICT (word) DO NOTHING;", (word,))

            cursor.execute("SELECT word_id FROM words WHERE word = %s;", (word,))

            word_id = cursor.fetchone()[0]

            # Check if the user already has this word in their list
            cursor.execute("""SELECT 1 
                           FROM user_words 
                           WHERE user_id = %s AND word_id = %s;""", (user_id, word_id))

            result = cursor.fetchone()

            if result:
                await query.answer(f'"{word}" is already in your word list.')
            else:
                # Add the word to the user's word list
                cursor.execute("""
                               INSERT INTO user_words (user_id, word_id) 
                               VALUES (%s, %s);""", (user_id, word_id))
                conn.commit()
                await query.answer(f'Added "{word}" to your word list.')
    except Exception as e:
        await query.answer(f"Error trying to add a word to the list: {e}")

async def mywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data["conn"]
    user_id = update.message.from_user.id

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                           SELECT w.word 
                           FROM user_words uw 
                           JOIN words w 
                           ON uw.word_id = w.word_id 
                           WHERE uw.user_id = %s;""", (user_id,))
            
            results = cursor.fetchall()

            if results:
                words = [row[0] for row in results]
                await update.message.reply_text("Your saved words:\n" + '\n'.join(words))
            else:
                await update.message.reply_text("You have no saved words.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def word_stream_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = definitions.get_random_word()
    definition = definitions.get_definition(word)

    if word and definition:
        keyboard = [[InlineKeyboardButton("Add Word", callback_data=f"add_{word}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f"{word}\n\n{definition}", reply_markup=reply_markup)
    else:
        await update.message.reply_text("I coudnt't find a suitable word for you..")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data["conn"]
    user_id = update.message.from_user.id

    plot_png = stats_stuff.get_word_progress_plot(conn=conn, user_id=user_id)

    # Send png
    if plot_png:
        await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=plot_png,
        caption="Here is a graph of how many words you added over time\n\n*Great job\\!*", parse_mode="MarkdownV2"
        )
    else:
        await update.message.reply_text("Coundn't find data for stats...")

def main():
    application = Application.builder().token(TOKEN).build()
    conn = None

    try:
        conn = db.db_connect()
        application.bot_data["conn"] = conn

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("mywords", mywords_command))
        application.add_handler(CommandHandler("word_stream", word_stream_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(add_word_callback, pattern="^add_"))

        print("Bot started")
        application.run_polling()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if conn:
            db.db_close(conn)

if __name__ == "__main__":
    main()