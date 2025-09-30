#Compara el DOM actual con el esperado. Detecta cambios en estructura, atributos, etc

from bs4 import BeautifulSoup

def analyze_dom(html_content, expected_selector):
    soup = BeautifulSoup(html_content, 'html.parser')
    candidates = soup.select(expected_selector)
    return len(candidates) > 0