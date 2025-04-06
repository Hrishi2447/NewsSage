"""
Translator module for translating text to different languages.
"""
import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# List of available languages with their language codes
AVAILABLE_LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Russian": "ru",
    "Japanese": "ja",
    "Chinese": "zh",
    "Korean": "ko",
    "Arabic": "ar",
    "Hindi": "hi",
}

def translate_text(text, target_language="English"):
    """
    Translate the given text to the target language using OpenAI.
    
    Args:
        text (str): The text to translate
        target_language (str): The language to translate to (from AVAILABLE_LANGUAGES)
        
    Returns:
        str: The translated text
    """
    if target_language == "English" or not text:
        return text  # No translation needed if target is English or text is empty
    
    try:
        # Use GPT-4o model for translation
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a professional translator. Translate the following text to {target_language}. "
                              f"Preserve formatting, maintain the original meaning, and ensure the translation sounds natural."
                },
                {"role": "user", "content": text}
            ],
            temperature=0.3,  # Lower temperature for more consistent translations
        )
        
        # Extract the translated text from the response
        translated_text = response.choices[0].message.content
        return translated_text
    
    except Exception as e:
        # Return original text with error message if translation fails
        return f"{text}\n\n[Translation Error: {str(e)}]"

def translate_nlp_result(nlp_result, target_language="English"):
    """
    Translate the relevant parts of the NLP result to the target language.
    
    Args:
        nlp_result (dict): The NLP result containing various text fields
        target_language (str): The language to translate to
        
    Returns:
        dict: The translated NLP result
    """
    if target_language == "English":
        return nlp_result  # No translation needed if target is English
    
    # Create a copy of the original result
    translated_result = nlp_result.copy()
    
    # Translate the summary
    if nlp_result.get("summary"):
        translated_result["summary"] = translate_text(nlp_result["summary"], target_language)
    
    # Translate the events in dates_events
    if nlp_result.get("dates_events"):
        translated_events = []
        for date_event in nlp_result["dates_events"]:
            translated_event = date_event.copy()
            if date_event.get("event"):
                translated_event["event"] = translate_text(date_event["event"], target_language)
            translated_events.append(translated_event)
        translated_result["dates_events"] = translated_events
    
    # Note: We don't translate keywords, people, or category as these are typically
    # proper nouns or short technical terms that may lose meaning in translation
    
    return translated_result