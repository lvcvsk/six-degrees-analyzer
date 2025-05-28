from google import genai
from google.genai import types
from dotenv import load_dotenv

def analyze_page_relationship(page1, page2, summary1, summary2, verbose=False):    
    load_dotenv()
    client = genai.Client()
    model = "gemini-2.5-flash-preview-05-20"

    prompt = f"""
        Analyze the relationship between these two Wikipedia pages:

        Page 1: {page1}
        Summary: {summary1}

        Page 2: {page2}
        Summary: {summary2}

        Describe in one short paragraph how these topics are connected or related. Focus on the most direct and meaningful connection. 
        If you were able to find the relationships in the summary you were given, tell us where.
        If you can't find an explicit relationship in the summaries, deduce one based on logical connections, shared categories, historical context, 
        geographical proximity, or conceptual similarities. If you have deduced this without the help of the summaries, please state it too.

        Relationship:
        """

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )
    ]

    config = types.GenerateContentConfig(
        temperature=1,
        top_p=1,
        seed=0,
        max_output_tokens=1024,
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ]
    )
    
    if verbose:
        model_info = client.models.get(model=model)
        print(f"{model_info.input_token_limit=}")
        # Count tokens using the new client method.
        total_tokens = client.models.count_tokens(model=model, contents=prompt)
        print("total_tokens: ", total_tokens)

    # Collect the streamed output into a string
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )

    return response.text

