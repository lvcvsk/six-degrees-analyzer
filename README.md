# 🌐 Six Degrees of Wikipedia

This app finds the shortest link path between two Wikipedia pages and analyzes the relationship between each adjacent pair using AI. It leverages modern web scraping tools and LLMs to explore how topics are connected across Wikipedia — inspired by the "six degrees of separation" concept.


## 🚀 How It Works
1. **Input**: User submits a source and target Wikipedia page.
2. **Pathfinding**: Async Playwright finds the shortest link path.
3. **Scraping**: For each article in the path, it scrapes:
   - Title
   - Infobox data
   - Key summary paragraphs
   - See also links
   - Categories
4. **Relationship Analysis**: Adjacent article pairs are passed to Gemini for relationship explanation.
5. **Output**: A step-by-step path and explanation of how each topic is connected.

## 📦 Setup
```bash
# Clone the repo
git clone https://github.com/lvcvsk/six-degrees-analyzer
cd six-degrees-analyzer

# Install dependencies
pip install -r requirements.txt

# Install Playwright dependencies
playwright install

# Set up environment variables
cp .env.example .env
# Add your Google API Key and any other settings to `.env`
```

# Start the server
```zsh
uvicorn main:app --reload
```

# Example endpoint call
```zsh
GET /path?from=https://en.wikipedia.org/wiki/Turing_machine&to=https://en.wikipedia.org/wiki/Artificial_intelligence
```
