#Propone nuevos locators basados en atributos similares, texto visible, o posición.

from bs4 import BeautifulSoup

def suggest_locator(html, broken_selector):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all():
        if tag.name in ['button', 'a', 'input'] and tag.text.strip():
            return f"{tag.name}:has-text('{tag.text.strip()}')"
    return None