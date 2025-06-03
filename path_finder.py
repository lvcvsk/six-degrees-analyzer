from playwright.async_api import async_playwright
import random

async def get_path_between_articles(start, end):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)      
        page = await browser.new_page()          
        await page.goto("https://www.sixdegreesofwikipedia.com/") 
        
        first_input = page.locator('input.react-autosuggest__input').first
        await first_input.fill(start)
        second_input = page.locator('input.react-autosuggest__input').nth(1)
        await second_input.fill(end)
        
        await page.get_by_role("button", name="Go!").click()    

        await page.wait_for_selector("div.sc-ffSBbn")
        path_divs = await page.query_selector_all("div.sc-ffSBbn")
        if not path_divs:
            print("No path containers found.")
            await browser.close()
            return [], []

        selected_path = random.choice(path_divs)
        links = await selected_path.query_selector_all("a")

        names, urls = [], []

        for link in links:
            url = await link.get_attribute("href")
            # Updated selector for the name paragraph inside the card
            name_elem = await link.query_selector("div.sc-cTIdZS > p:nth-child(1)")
            # Optionally check if it's a disambiguation entry using the second paragraph
            # subtitle_elem = await link.query_selector("div.sc-cTIdZS > p:nth-child(2)")
            name = await name_elem.inner_text() if name_elem else "Unnamed"
            names.append(name.strip())
            urls.append(url.strip())

        await browser.close()

    return names, urls

