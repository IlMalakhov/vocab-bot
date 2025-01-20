import requests
from bs4 import BeautifulSoup

def get_definition(word):
    url = f"https://www.thefreedictionary.com/{word}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"definitions.py: Unable to fetch data for {word}"

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for the definition section in the HTML
    definition_sections = soup.find('div', {'class': 'ds-list'})
    if not definition_sections:
        return f"definitions.py: No definition found for {word}."

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
