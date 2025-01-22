import requests
from bs4 import BeautifulSoup

def get_definition(word):
    url = f"https://www.thefreedictionary.com/{word}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"definitions.py: Unable to fetch data for {word}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for the definition section in the HTML
    definition_sections = soup.find('div', {'class': 'ds-list'})
    if not definition_sections:
        print(f"definitions.py: No definition found for {word}.")
        return None

    # Collect all definitions
    definition_list = [definition.get_text().strip() for definition in definition_sections]

    return '\n'.join(definition_list)

def get_random_word():
    url = "https://www.thefreedictionary.com/dictionary.htm"
    response = requests.get(url)

    if response.status_code != 200:
        return f"definitions.py: Unable to fetch data for random words"
    
    soup = BeautifulSoup(response.text, 'html.parser')

    random_section = soup.find('ul', {'class': 'lst'})
    random_list = [random_word.get_text().strip() for random_word in random_section]

    # The first list item is an empty string, so...
    return random_list[1]

def get_synonyms(word):
    url = f"https://www.thesaurus.com/browse/{word}"
    response = requests.get(url)
    text = response.text
    
    if response.status_code != 200:
        print(f"definitions.py: Unable to fetch synonyms for {word}")
        return None
    
    soup = BeautifulSoup(text, 'html.parser')
    
    synonyms_section = soup.find('div', {'class': 'QXhVD4zXdAnJKNytqXmK'})
    synonyms = synonyms_section.find_all('li')

    # Really don't ask about this
    if not synonyms:
        synonyms = synonyms_section.find_all('span')

    if not synonyms:
        print(f"definitions.py: No synonyms found for {word}")
        return None

    synonym_list = [synonym.get_text().strip() for synonym in synonyms]
    
    return synonym_list