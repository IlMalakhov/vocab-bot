# What is it?

This is a Telegram bot designed to help users look up **word definitions** in English, save them, and manage a personal **vocabulary list**. It connects to a PostgreSQL database and fetches word definitions from [Dictionary API](https://dictionaryapi.dev/). It also fetches images from [Unsplash API](https://unsplash.com) and scrapes synonyms from [thesaurus.com](https://thesaurus.com).

## Usage

- **Start the Bot**: Send `/start` to the bot to introduce itself.

- **Look Up Definitions**: Type any word, and the bot will return its definition.
  - **Save Words**: Click “Add Word” button to save it.
  - **Get Synonyms**: Click "Synonyms" button to show synonyms from [thesaurus.com](https://thesaurus.com)
  - **View pictures**: Click "Picture" button to fetch a picture using [Unsplash](https://unsplash.com) API
  - **Practice Pronunciation**: Click "Pronunciation" button to listen to the pronunciation of the word.

- **View Saved Words**: Use `/mywords` to see your saved vocabulary list.

- **View learning progress**: Use `/stats` to see a graph of how many words you added.

- **Word Stream**: Use `/word_stream` to learn random words.
  - **By Level**: Use `/word_stream <list>` to get words from specific language levels (e.g., c1, c2).

- **Chat**: You can chat with the bot using `/chat <message>` and it will respond with a custom [Ollama](https://ollama.com) model designed to make understanding new vocabulary easy.

## Dependencies

- **Telegram**: python-telegram-bot v21.9 for bot functionality
- **Dictionary API**: for fetching word definitions
- **Web Scraping**:
  - requests v2.32.3
  - BeautifulSoup4 v4.12.3
- **Image Fetching**:
  - Unsplash API for fetching images
- **Chatting**:
  - A custom ollama model
- **Database**:
  - PostgreSQL 16
  - psycopg2-binary v2.9.10
- **Data Analysis**:
  - pandas v2.2.3
  - matplotlib v3.10.0
  - numpy v2.2.1
- **Environment**:
  - python-dotenv v1.0.1
- **HTTP Client**:
  - httpx v0.28.1
  - httpcore v1.0.7

## Build you own Vocab Bot

### Credentials

You will have to create a `.env` file with the following:

```env
# PostgreSQL database credentials
DB_HOST=<your_server>
DB_NAME=<your_db_name>
DB_USER=<your_db_user_name>
DB_PASSWORD=<your_db_user_password>

# Bot token
TELEGRAM_TOKEN=<your_telegram_token>

# Unsplash API access key
UNSPLASH_API_KEY=<your_unsplash_access_key>
```

`TELEGRAM_TOKEN` is from [Bot Father](https://t.me/BotFather)

### Database Schema

#### Tables

##### 1. `users`

This table stores information about the users interacting with the bot.

| Column       | Type        | Constraints     | Description                         |
| ------------ | ----------- | --------------- | ----------------------------------- |
| `user_id`    | `BIGINT`    | `PRIMARY KEY`   | Unique identifier for the user.     |
| `created_at` | `TIMESTAMP` | `DEFAULT NOW()` | The timestamp when the user joined. |

---

##### 2. `words`

This table stores all unique words across users. This is cool for all kinds of analysis.

| Column       | Type        | Constraints       | Description                            |
| ------------ | ----------- | ----------------- | -------------------------------------- |
| `word_id`    | `SERIAL`    | `PRIMARY KEY`     | Unique identifier for each word.       |
| `word`       | `TEXT`      | `UNIQUE NOT NULL` | The word itself.                       |
| `created_at` | `TIMESTAMP` | `DEFAULT NOW()`   | The timestamp when the word was added. |

---

##### 3. `user_words`

This table describes a **relationship** between users and the words they have saved.

| Column     | Type        | Constraints                                   | Description                            |
| ---------- | ----------- | --------------------------------------------- | -------------------------------------- |
| `user_id`  | `BIGINT`    | `REFERENCES users(user_id) ON DELETE CASCADE` | The user who saved the word.           |
| `word_id`  | `INT`       | `REFERENCES words(word_id) ON DELETE CASCADE` | The word saved by the user.            |
| `added_at` | `TIMESTAMP` | `DEFAULT NOW()`                               | The timestamp when the word was saved. |

---
