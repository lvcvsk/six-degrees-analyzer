from fastapi import FastAPI, Query
from path_finder import get_path_between_articles
from relationship_analyzer import analyze_page_relationship
from wiki_scraper import scrape_wikipedia_page
import json

app = FastAPI()

@app.get("/")
def root():
    return "It works!"

@app.get("/six_degrees")
async def get_relationships(start: str = Query(...), end: str = Query(...)):
    results = []
    names, links = await get_path_between_articles(start, end)
    for i in range(len(names)-1):
        
        current_relationship = {}
        print(f"Scraping {names[i]} with link: {links[i]}")
        print(f"Scraping {names[i+1]} with link: {links[i+1]}")

        summary_1, summary_2 = await scrape_wikipedia_page(links[i]), await scrape_wikipedia_page(links[i+1])
        
        with open(f"summaries/output{i}.txt", "w") as file:
            file.write(json.dumps(summary_1, indent=2))
        if i == len(names) - 2:
            with open(f"summaries/output{i + 1}.txt", "w") as file:
                file.write(json.dumps(summary_2, indent=2))

        current_relationship["first_name"] = names[i]
        current_relationship["second_name"] = names[i+1]
        current_relationship["first_link"] = links[i]
        current_relationship["second_link"] = links[i+1]
        
        print("Prompting the LLM..")
        current_relationship["relationship"] = analyze_page_relationship(names[i], names[i+1],summary_1, summary_2)
        results.append(current_relationship)
    return results
    