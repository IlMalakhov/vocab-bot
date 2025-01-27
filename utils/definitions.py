import requests
import random
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

def get_definitions(word) -> str:
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
    
    if response.status_code == 200:
        data = response.json()

        if data:
            meanings = data[0]['meanings']
            definitions_dict = {
                meaning['partOfSpeech']: [definition['definition'] for definition in meaning['definitions']]
                for meaning in meanings
            }
            
            # Format the output string
            formatted_output = "Here are some definitions for the word you requested 📖\n"
            for part_of_speech, definitions in definitions_dict.items():
                formatted_output += f"\n{part_of_speech.capitalize()}:\n"
                for index, definition in enumerate(definitions, 1):
                    formatted_output += f"{index}. {definition}\n"
            
            return formatted_output

    print(f"definitions.py: No definitions found for '{word}'")
    return None

def get_example(word) -> str:
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
    
    if response.status_code == 200:
        data = response.json()

        if data:
            meanings = data[0]['meanings']
            examples_dict = {
                meaning['partOfSpeech']: [example['example'] for example in meaning['examples']]
                for meaning in meanings
            }
            
            # Format the output string
            formatted_output = "Here are some examples for the word you requested 📖\n"
            for part_of_speech, examples in examples_dict.items():
                formatted_output += f"\n{part_of_speech.capitalize()}:\n"
                for index, example in enumerate(examples, 1):
                    formatted_output += f"{index}. {example}\n"
            
            return formatted_output

    print(f"definitions.py: No examples found for '{word}'")
    return None

def get_random_word(level=None) -> str:
    level_paths = {
        'c2': os.getenv("C2_WORDLIST_PATH"),
        'c1': os.getenv("C1_WORDLIST_PATH"),
        'b2': os.getenv("B2_WORDLIST_PATH"),
        'b1': os.getenv("B1_WORDLIST_PATH")
    }

    if level and level.lower() in level_paths:
        with open(level_paths[level.lower()], 'r') as file:
            words = file.read().split(',')
            random_word = random.choice(words).strip()
            return random_word
    
    # Default case - random word from general list
    with open(os.getenv("RANDOM_WORDLIST_PATH"), 'r') as file:
        words = file.readlines()
        random_word = random.choice(words).strip()
    
    return random_word

def get_synonyms(word) -> list:
    url = f"https://www.thesaurus.com/browse/{word}"
    response = requests.get(url)
    text = response.text
    
    if response.status_code != 200:
        print(f"definitions.py: Unable to fetch synonyms for {word}")
        return None
    
    soup = BeautifulSoup(text, 'html.parser')
    
    synonyms_section = soup.find('div', {'class': 'QXhVD4zXdAnJKNytqXmK'})

    # Try this
    synonyms = synonyms_section.find_all('li')

    # Then try this
    # and really don't ask about it
    if not synonyms:
        synonyms = synonyms_section.find_all('span')

    if not synonyms:
        print(f"definitions.py: No synonyms found for {word}")
        return None

    synonym_list = [synonym.get_text().strip() for synonym in synonyms]
    
    return synonym_list

def get_pronunciation_url(word) -> str:
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
    
    if response.status_code == 200:
        data = response.json()

        if data:
            phonetics = data[0]['phonetics']
            for phonetic in phonetics:
                if 'audio' in phonetic and phonetic['audio']:
                    return phonetic['audio']
            
    print(f"definitions.py: No pronunciation URL found for '{word}'")
    return None