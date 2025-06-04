import re
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())

async def scrape_wikipedia_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.find('h1', id='firstHeading').text.strip()

    infobox_info = {}
    infobox = soup.find('table', class_='infobox')
    if infobox:
        rows = infobox.find_all('tr')
        for row in rows:
            header = row.find('th')
            data = row.find('td')
            if header and data:
                label = clean_text(header.text)
                info = clean_text(data.text)
                if label and info:
                    infobox_info[label] = info
                        
    see_also_links = []
    div_col = soup.find('div', class_='div-col')
    if div_col:
        ul_element = div_col.find('ul')
        if ul_element:
            links = ul_element.find_all('a', href=True)
            for link in links:
                link_text = clean_text(link.text)
                if link_text:
                    see_also_links.append(link_text)
                    
    # Get first three top-level paragraphs
    key_paragraphs = []
    content_div = soup.find('div', id='mw-content-text')
    article_content = content_div.find('div', class_='mw-parser-output')
    if content_div and article_content:
        paragraphs = article_content.find_all('p', recursive=False)[:3]
        for p in paragraphs:
            text = clean_text(p.get_text())
            if len(text) > 50:
                key_paragraphs.append(text)
                        
    categories = []
    category_div = soup.find('div', id='mw-normal-catlinks')
    if category_div:
        category_links = category_div.find_all('a')[1:]
        for link in category_links:
            category_name = clean_text(link.text)
            if category_name:
                categories.append(category_name)

    return {
        'title': title,
        'url': url,
        'basic_info': infobox_info,
        'categories': categories,
        'see_also': see_also_links,
        'key_paragraphs': key_paragraphs
    }
