from playwright.async_api import async_playwright
import random

URL = "https://www.sixdegreesofwikipedia.com/"
random.seed(3)

async def get_path_between_articles(start, end):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)      
        page = await browser.new_page()          
        await page.goto(URL) 
        
        first_input = page.locator('input.react-autosuggest__input').first
        await first_input.fill(start)
        second_input = page.locator('input.react-autosuggest__input').nth(1)
        await second_input.fill(end)
        
        await page.get_by_role("button", name="Go!").click()

        # Scroll to bottom to trigger lazy-loaded content
        await page.wait_for_timeout(3000)  # Wait 5 seconds for the backend calc
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.locator("div.sc-eGjrzz").wait_for()
        path_divs = page.locator("div.sc-ffSBbn")
        path_count = await path_divs.count()
        if path_count == 0:
            print("No path containers found.")
            await browser.close()
            return [], []

        selected_path = path_divs.nth(random.randint(0, path_count-1))
        link_locator = selected_path.locator("a")
        link_count = await link_locator.count()

        names, urls = [], []

        for i in range(link_count):
            link = link_locator.nth(i)
            url = await link.get_attribute("href")
            name_locator = link.locator("div.sc-cTIdZS > p").first
            name = await name_locator.inner_text()
            # TODO: Check for disambiguation entry
            names.append(name.strip())
            urls.append(url.strip())

        await browser.close()

    return names, urls

