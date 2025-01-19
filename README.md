# What is it?

This is a Telegram bot designed to help users look up **word definitions** in English, save them, and manage a personal **vocabulary list**. It connects to a PostgreSQL database and fetches word definitions from [thefreedictionary.com](https://thefreedictionary.com)

## Usage

- **Start the Bot**: Send /start to the bot to initialize.
- **Look Up Definitions**: Send any word, and the bot will return its definition.
- **Save Words**: Click the “Add Word” button under a definition to save it.
- **View Saved Words**: Use /mywords to see your saved vocabulary list.

## Build you own Vocab Bot

### Credentials

You will have to create a `.env` file with the following:

```env
DB_HOST=<your_server>
DB_NAME=<your_db_name>
DB_USER=<your_db_user_name>
DB_PASSWORD=<your_db_user_password>
TELEGRAM_TOKEN=<your_telegram_token>
```

`TELEGRAM_TOKEN` is from [Bot Father](https://t.me/BotFather)

## Database Schema

### Tables

#### 1. `users`

This table stores information about the users interacting with the bot.

| Column       | Type        | Constraints     | Description                         |
| ------------ | ----------- | --------------- | ----------------------------------- |
| `user_id`    | `BIGINT`    | `PRIMARY KEY`   | Unique identifier for the user.     |
| `created_at` | `TIMESTAMP` | `DEFAULT NOW()` | The timestamp when the user joined. |

---

#### 2. `words`

This table stores all unique words across users. This is cool for all kinds of analysis.

| Column       | Type        | Constraints       | Description                            |
| ------------ | ----------- | ----------------- | -------------------------------------- |
| `word_id`    | `SERIAL`    | `PRIMARY KEY`     | Unique identifier for each word.       |
| `word`       | `TEXT`      | `UNIQUE NOT NULL` | The word itself.                       |
| `created_at` | `TIMESTAMP` | `DEFAULT NOW()`   | The timestamp when the word was added. |

---

#### 3. `user_words`

This table describes a **relationship** between users and the words they have saved.

| Column     | Type        | Constraints                                   | Description                            |
| ---------- | ----------- | --------------------------------------------- | -------------------------------------- |
| `user_id`  | `BIGINT`    | `REFERENCES users(user_id) ON DELETE CASCADE` | The user who saved the word.           |
| `word_id`  | `INT`       | `REFERENCES words(word_id) ON DELETE CASCADE` | The word saved by the user.            |
| `added_at` | `TIMESTAMP` | `DEFAULT NOW()`                               | The timestamp when the word was saved. |
