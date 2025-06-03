from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

def clean_text(text):
    """Remove extra spaces and newlines"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())


async def scrape_wikipedia_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        title = clean_text(await page.title())
        await browser.close()

    # Get basic info from the infobox
    basic_info = {}
    infobox = soup.find('table', class_='infobox')
    if infobox:
        rows = infobox.find_all('tr')
        for row in rows:
            header = row.find('th')
            data = row.find('td')
            if header and data:
                key = clean_text(header.text)
                value = clean_text(data.text)
                if key and value:
                    basic_info[key] = value
                        
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
                    
    notable_links = []
    content_div = soup.find('div', id='mw-content-text')
    if content_div:
        wiki_links = content_div.find_all('a', href=re.compile(r'/wiki/'))
        for link in wiki_links[:20]:  # Limit to most relevant links
            href = link.get('href', '')
            if not any(exclude in href for exclude in ['Category:', 'File:', 'Template:']):
                text = clean_text(link.get_text())
                if text and len(text) > 2:
                    notable_links.append({
                        'text': text,
                        'href': href
                    })

    key_paragraphs = []
    parser_output = content_div.find('div', class_='mw-parser-output')
    if content_div and parser_output:
        paragraphs = parser_output.find_all('p', recursive=False)[:3]
        for p in paragraphs:
            text = clean_text(p.get_text())
            if len(text) > 50:
                key_paragraphs.append(text)
                        
    # Get categories
    categories = []
    category_div = soup.find('div', id='mw-normal-catlinks')
    if category_div:
        category_links = category_div.find_all('a')
        for link in category_links:
            category_name = clean_text(link.text)
            if category_name:
                categories.append(category_name)

    return {
        'title': title,
        'url': url,
        'basic_info': basic_info,
        'categories': categories,
        'see_also': see_also_links,
        'key_paragraphs': key_paragraphs,
        'notable_links': notable_links
    }
