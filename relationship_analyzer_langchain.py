from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

model = OllamaLLM(model="llama3.2")

template = """
Analyze the relationship between these two Wikipedia pages:

Page 1: {page1_title}
Summary: {page1_summary}

Page 2: {page2_title}
Summary: {page2_summary}

Describe in one clear sentence how these topics are connected or related. Focus on the most direct and meaningful connection. 
If you can't find an explicit relationship in the summaries, deduce one based on logical connections, shared categories, historical context, 
geographical proximity, or conceptual similarities.

Relationship:"""

def analyze_page_relationship	(page1, page2, summary1, summary2):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    inputs = {
        "page1_title": page1,
        "page1_summary": summary1,
        "page2_title": page2,
        "page2_summary": summary2
    }

    response = chain.invoke(inputs)
    return response
