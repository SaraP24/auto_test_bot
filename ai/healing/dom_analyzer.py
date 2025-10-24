#Compara el DOM actual con el esperado. Detecta cambios en estructura, atributos, etc

from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

def analyze_dom(html_content, expected_selector):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        candidates = soup.select(expected_selector)
        logging.info(f"Found {len(candidates)} elements matching '{expected_selector}'")
        return len(candidates) > 0
    except Exception as e:
        logging.error(f"Error analyzing DOM: {e}")
        return False