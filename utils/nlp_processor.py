import os
import json
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def process_article(article_text, article_title=""):
    """
    Process the article text using OpenAI API to generate summary, extract entities, and categorize
    
    Args:
        article_text (str): The text content of the article
        article_title (str, optional): The title of the article
        
    Returns:
        dict: Dictionary containing summary, entities, and category
    """
    # Truncate if article is too long (OpenAI has token limits)
    max_chars = 15000  # Approximate token limit conversion to characters
    truncated_text = article_text[:max_chars] if len(article_text) > max_chars else article_text
    
    # Create prompt for OpenAI
    prompt = f"""
    Analyze the following news article{' titled: "' + article_title + '"' if article_title else ''}.
    
    Article text:
    {truncated_text}
    
    Provide a response in JSON format with the following information:
    1. A concise summary of the article (around 3-5 sentences)
    2. Key people mentioned in the article (list of names)
    3. Important dates and events mentioned (list with brief descriptions)
    4. The category of the article (e.g., politics, technology, business, sports, entertainment, health, science, etc.)
    
    Format your response as a valid JSON object with the following structure:
    {{
        "summary": "The concise summary here...",
        "people": ["Person 1", "Person 2", ...],
        "dates_events": [
            {{"date": "Date description or actual date", "event": "Event description"}}
        ],
        "category": "The most appropriate category"
    }}
    """
    
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
        return {
            "success": True,
            "summary": result.get("summary", ""),
            "people": result.get("people", []),
            "dates_events": result.get("dates_events", []),
            "category": result.get("category", "Uncategorized")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
