import requests
from bs4 import BeautifulSoup

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

def get_random_word() -> str:
    url = "https://www.thefreedictionary.com/dictionary.htm"
    response = requests.get(url)

    if response.status_code != 200:
        return f"definitions.py: Unable to fetch data for random words"
    
    soup = BeautifulSoup(response.text, 'html.parser')

    random_section = soup.find('ul', {'class': 'lst'})
    random_list = [random_word.get_text().strip() for random_word in random_section]

    # The first list item is an empty string, so...
    return random_list[1]

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
    # Really don't ask about it
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