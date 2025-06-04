from fastapi import FastAPI, Query
import json
from path_finder import get_path_between_articles
from relationship_analyzer import analyze_page_relationship
from wiki_scraper import scrape_wikipedia_page
from textwrap import fill

app = FastAPI()

@app.get("/")
def root():
    return "It works!"

@app.get("/six_degrees")
async def get_relationships(start: str = Query(...), end: str = Query(...)):
    results = []
    summaries = []
    names, links = await get_path_between_articles(start, end)
    
    # Get summary for every wikipedia page
    for i in range(len(links)):
        summary = await scrape_wikipedia_page(links[i])
        with open(f"summaries/wikipage_{i}", "w") as file:
            file.write(json.dumps(summary, indent=2))
        summaries.append(summary)
        
    
    for i in range(len(names)-1):
        current_relationship = {}
        current_relationship["first_name"] = names[i]
        current_relationship["second_name"] = names[i+1]
        
        print(f"Analyzing relationship between {names[i]} and {names[i+1]}")
        current_relationship["relationship"] = fill(analyze_page_relationship(names[i], names[i+1], summaries[i], summaries[i+1]), width=80)
        results.append(current_relationship)
        
    with open(f"summaries/llm_output.txt", "w") as file:
        file.write(json.dumps(results, indent=2))
        
    return results
    
