# What is it?

This is a Telegram bot designed to help users look up **word definitions** in English, save them, and manage a personal **vocabulary list**. It connects to a PostgreSQL database and fetches word definitions from [thefreedictionary.com](https://thefreedictionary.com)

## Usage
- **Start the Bot**: Send /start to the bot to initialize.
- **Look Up Definitions**: Send any word, and the bot will return its definition.
- **Save Words**: Click the “Add Word” button under a definition to save it.
- **View Saved Words**: Use /mywords to see your saved vocabulary list.

## Build you own Vocab Bot

You will have to create a `.env` file with the following:
- DB_HOST=your_server
- DB_NAME=your_db_name
- DB_USER=your_db_user_name
- DB_PASSWORD=your_db_user_password
- TELEGRAM_TOKEN=your_telegram_token (from [Bot Father](https://t.me/BotFather))

As well as create a table `user_words` with `user_id` and `words`.

> [!note]
> The Database schema is soon going to be reworked to account for the new `/stats` command
