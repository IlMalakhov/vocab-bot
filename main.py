# Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# OS
import os
from dotenv import load_dotenv

# Logging
import logging

# Utilities
from utils import db, definitions, images, stats_stuff

# Chat
from model.vocability import chat

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data["conn"]
    user_id = update.message.from_user.id

    keyboard = [
        [
            InlineKeyboardButton("B1", callback_data="level_B1"),
            InlineKeyboardButton("B2", callback_data="level_B2")
        ],
        [
            InlineKeyboardButton("C1", callback_data="level_C1"),
            InlineKeyboardButton("C2", callback_data="level_C2")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

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
                    "Also, check out [our bot's GitHub](https://github.com/IlMalakhov/vocab-bot) to take a peek under the hood ⚙️\n\n"
                    "Change your language level below:", 
                    parse_mode="MarkdownV2", 
                    reply_markup=reply_markup, 
                    disable_web_page_preview=True)
            else:
                # User does not exist
                cursor.execute("INSERT INTO users (user_id) VALUES (%s);", (user_id,))
                conn.commit()
                await update.message.reply_text(
                    "Nice to meet you, I'm Vocab Bot\\! ☀️\n\n"                    
                    "I will help you define and remember new vocabulary 📖\n\n"
                    "1\\. Type any word to get its definition 💬\n"
                    "2\\. */mywords* to see your wordlist 📚\n\n"
                    "_I can do a lot more, just use_ */help* _and see for yourself_ 🎉\n\n\n" 
                    "Also, check out [our bot's GitHub](https://github.com/IlMalakhov/vocab-bot) to take a peek under the hood 🛠️\n\n"
                    "Now let's set your language level:", 
                    parse_mode="MarkdownV2",
                    reply_markup=reply_markup,
                    disable_web_page_preview=True)

    except Exception as e:
        logger.error(f"Error fetching or inserting info about the user: {e}")

async def level_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    conn = context.bot_data["conn"]
    user_id = query.from_user.id
    level = query.data.split('_', 1)[1]

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                           UPDATE users 
                           SET level = %s 
                           WHERE user_id = %s;""", (level, user_id))
            conn.commit()

    except Exception as e:
        logger.error(f"Error updating user's level: {e}")

    await query.answer(f"Your level is set to {level} 📚")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Here's what I can do for you: 🎉\n\n"
        "Simply type any word to see its definition\\! 🔍\n\n"
        "*Main Features:*\n"
        "• */word\\_stream* \\- Discover random vocabulary 🎲\n"
        "• */word\\_stream \\{b1, b2, c1, c2\\}* \\- Learn words by level 📚\n"
        "• */mywords* \\- View your saved collection 📖\n"
        "• */stats* \\- Track your learning progress 📈\n"
        "• */chat* \\- Ask *vocability* anything about English 💭\n"
        "To save words, just tap *Add word* below any definition\\! ✨",
        parse_mode="MarkdownV2")
    
async def word_stream_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    level = args[0] if args else None

    word = definitions.get_random_word(level=str(level))
    definition = definitions.get_definitions(word)

    if word and definition:
        keyboard = [
            [InlineKeyboardButton("📝 Add Word 📝", callback_data=f"add_{word}")],
            [InlineKeyboardButton("🔄 Synonyms 🔄", callback_data=f"syn_{word}")],
            [InlineKeyboardButton("➡️ Next ➡️", callback_data=f"next_{level}" if level else "next")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f"{word}\n\n{definition}", reply_markup=reply_markup)
    else:
        await update.message.reply_text("I couldn't find a good enough word for you...")

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

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data["conn"]
    user_id = update.message.from_user.id

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    plot_png = stats_stuff.get_word_progress_plot(conn=conn, user_id=user_id)
    summary = stats_stuff.get_stats_summary(conn=conn, user_id=user_id)

    # Send png
    if plot_png:
        await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=plot_png
        )
    else:
        await update.message.reply_text("Coundn't find data for stats...")

    if summary:
        formatted_summary = (
            f"📊 *Your Vocabulary Stats* 📊\n\n"
            f"📚 Total words saved: *{summary['total_words']}*\n"
            f"🌟 Days studying: *{summary['days_studying']}*\n"
            f"⭐ Daily average: *{summary['daily_average']:.1f}*\n\n"
            f"☀️ Words added today: *{summary['words_today']}*\n"
            f"📅 Words added this week: *{summary['words_this_week']}*\n\n"
            f"🏆 Best day: *{summary['best_day']['date']}* with *{summary['best_day']['count']}* words\n\n"
            f"Keep up the good work! 🌹"
        )
        await update.message.reply_text(formatted_summary, parse_mode="Markdown")
    
async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ' '.join(context.args) if context.args else None
    user_id = update.effective_user.id
    
    if not message:
        await update.message.reply_text(
            "Please include your message after /chat\n"
            "Example: /chat what's the difference between affect and effect?"
        )
        return

    try:
        await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
        )
        # Get response from model
        response = await chat(message, user_id)
        
        # Send response
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await update.message.reply_text(
            "Sorry, I'm having trouble with your request..."
        )

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text:
        word = text.lower()
        definition = definitions.get_definitions(word)

        if definition:
            # Create an inline button for adding the word
            keyboard = [
                [InlineKeyboardButton("📝 Add Word 📝", callback_data=f"add_{word}")],
                [InlineKeyboardButton("🔄 Synonyms 🔄", callback_data=f"syn_{word}")],
                [InlineKeyboardButton(f"🖼️ Pictire for {word} 🖼️", callback_data=f"pic_{word}")],
                [InlineKeyboardButton("🔊 Pronunciation 🎧", callback_data=f"pron_{word}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(definition, reply_markup=reply_markup)
        else:
            await update.message.reply_text("I coudn't find the definition for that...")
    else:
        await update.message.reply_text("Something seems wrong with the word you sent me...")

# Callbacks
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

async def synonyms_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    word = query.data.split('_', 1)[1]
    word = word.strip().lower()
    synonyms = definitions.get_synonyms(word)

    # Remove the "Synonyms" button from the keyboard
    keyboard = [
        [button for button in row if "syn_" not in button.callback_data]
        for row in query.message.reply_markup.inline_keyboard
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if synonyms:
        await query.edit_message_text(
            text=query.message.text + f"\n\nSynonyms for {word}:\n\n" + '\n'.join(synonyms),
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            text=query.message.text + f"\n\nCouldn't find synonyms for {word}...",
            reply_markup=reply_markup
        )

async def next_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Get level from callback data if it exists
    level = query.data.split('_', 1)[1] if '_' in query.data else None

    word = definitions.get_random_word(level=level)
    definition = definitions.get_definitions(word)

    if word and definition:
        keyboard = [
            [InlineKeyboardButton("📝 Add Word 📝", callback_data=f"add_{word}")],
            [InlineKeyboardButton("🔄 Synonyms 🔄", callback_data=f"syn_{word}")],
            [InlineKeyboardButton("➡️ Next ➡️", callback_data=f"next_{level}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Edit the original message
        await query.edit_message_text(
            text=f"{word}\n\n{definition}",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("I couldn't find a suitable word for you...")

async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    word = query.data.split('_', 1)[1]
    word = word.strip().lower()
    image_url = images.fetch_image_url(word)

    keyboard = [
    [button for button in row if "pic_" not in button.callback_data]
    for row in query.message.reply_markup.inline_keyboard
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if image_url:
        await context.bot.send_photo(
            chat_id=query.message.chat_id, 
            photo=image_url, 
            caption=f"Here is an image for {word} 🖼️",
            has_spoiler=True,
            )
        
        await query.edit_message_text(text=query.message.text, reply_markup=reply_markup)

    else:
        await query.edit_message_text(
            text=query.message.text + f"\n\nCouldn't find an image for {word}...",
            reply_markup=reply_markup
        )

async def send_pronunciation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    word = query.data.split('_', 1)[1]
    word = word.strip().lower()
    audio_url = definitions.get_pronunciation_url(word)

    keyboard = [
        [button for button in row if "pron_" not in button.callback_data]
        for row in query.message.reply_markup.inline_keyboard
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if audio_url:
        await context.bot.send_audio(
            chat_id=query.message.chat_id,
            audio=audio_url,
            caption=f"Here is the pronunciation for {word} 🎧"
        )
        await query.edit_message_text(text=query.message.text, reply_markup=reply_markup)
    else:
        await query.edit_message_text(
            text=query.message.text + f"\n\nCouldn't find a pronunciation for {word}...",
            reply_markup=reply_markup
        )

def main():
    application = Application.builder().token(TOKEN).build()
    conn = None

    try:
        conn = db.db_connect()
        application.bot_data["conn"] = conn

        # Command handlers
        start_handler = CommandHandler("start", start_command)
        help_handler = CommandHandler("help", help_command)
        mywords_handler = CommandHandler("mywords", mywords_command)
        word_stream_handler = CommandHandler("word_stream", word_stream_command)
        stats_handler = CommandHandler("stats", stats_command)
        chat_handler = CommandHandler("chat", chat_command)
        message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        add_word_callback_handler = CallbackQueryHandler(add_word_callback, pattern="^add_")
        next_word_callback_handler = CallbackQueryHandler(next_callback, pattern="^next_")
        next_no_level_word_callback_handler = CallbackQueryHandler(next_callback, pattern="next")
        synonyms_callback_handler = CallbackQueryHandler(synonyms_callback, pattern="^syn_")
        images_callback_handler = CallbackQueryHandler(send_image, pattern="^pic_")
        pronunciation_callback_handler = CallbackQueryHandler(send_pronunciation, pattern="^pron_")
        set_level_callback_handler = CallbackQueryHandler(level_callback, pattern="^level_")
        
    

        # Add handlers to application
        application.add_handler(start_handler)
        application.add_handler(help_handler)
        application.add_handler(mywords_handler)
        application.add_handler(word_stream_handler)
        application.add_handler(stats_handler)
        application.add_handler(message_handler)
        application.add_handler(add_word_callback_handler)
        application.add_handler(next_word_callback_handler)
        application.add_handler(next_no_level_word_callback_handler)
        application.add_handler(synonyms_callback_handler)
        application.add_handler(images_callback_handler)
        application.add_handler(pronunciation_callback_handler)
        application.add_handler(set_level_callback_handler)
        application.add_handler(chat_handler)

        application.run_polling()

    except Exception as e:
        logger.error(f"Error in main: {e}")

    finally:
        if conn:
            db.db_close(conn)

if __name__ == "__main__":
    main()