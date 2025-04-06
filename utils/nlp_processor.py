import re
import numpy as np
import spacy
import datetime

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    # In case the model is not installed
    import sys
    print("spaCy model not found. Please install it using: python -m spacy download en_core_web_sm")
    sys.exit(1)

def create_summary(text, sentences_count=5):
    """
    Create a summary using spaCy and TextRank-inspired algorithm
    
    Args:
        text (str): The text to summarize
        sentences_count (int): Number of sentences for the summary
        
    Returns:
        str: A summary of the text
    """
    # Process the text with spaCy
    doc = nlp(text)
    
    # Get sentences
    sentences = [sent.text.strip() for sent in doc.sents]
    
    # Skip summarization if text is too short
    if len(sentences) <= sentences_count:
        return text
    
    # Implement a simplified TextRank-like algorithm
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    
    # Calculate similarity between all sentence pairs
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                # Get spaCy docs for both sentences
                doc_i = nlp(sentences[i])
                doc_j = nlp(sentences[j])
                
                # Calculate similarity
                if doc_i.vector_norm and doc_j.vector_norm:  # Check if vectors exist
                    similarity_matrix[i][j] = doc_i.similarity(doc_j)
    
    # Calculate sentence scores using the sum of similarities
    sentence_scores = np.sum(similarity_matrix, axis=1)
    
    # Get indices of top sentences
    ranked_indices = np.argsort(sentence_scores)[::-1]  # Sort in descending order
    top_indices = ranked_indices[:sentences_count]
    
    # Sort indices to maintain original order
    top_indices = sorted(top_indices)
    
    # Create summary
    summary = ' '.join([sentences[i] for i in top_indices])
    return summary

def process_article(article_text, article_title=""):
    """
    Process the article text using spaCy for summarization, NER, and categorization
    
    Args:
        article_text (str): The text content of the article
        article_title (str, optional): The title of the article
        
    Returns:
        dict: Dictionary containing summary, entities, and category
    """
    try:
        # Create summary using spaCy
        summary = create_summary(article_text)
        
        # Extract people names (basic NER)
        people = extract_people(article_text)
        
        # Extract dates and events
        dates_events = extract_dates_events(article_text)
        
        # Determine category based on keyword frequency
        category = determine_category(article_text)
        
        return {
            "success": True,
            "summary": summary,
            "people": people,
            "dates_events": dates_events,
            "category": category
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def extract_people(text):
    """Extract people's names from the text using spaCy's named entity recognition"""
    people = []
    try:
        # Process text with spaCy
        doc = nlp(text)
        
        # Extract person entities
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                if ent.text not in people:
                    people.append(ent.text)
                    
        # Take only the top 10 people if there are many
        return people[:10]
    except Exception:
        return []

def extract_dates_events(text):
    """Extract dates and associated events from the text using spaCy and regex"""
    dates_events = []
    
    # Process text with spaCy
    doc = nlp(text)
    
    # Simple regex patterns for date matching
    date_patterns = [
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}\b',
        r'\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b',
        r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}\b'
    ]
    
    # Get sentences
    sentences = [sent.text.strip() for sent in doc.sents]
    
    for sentence in sentences:
        has_date = False
        date_str = ""
        
        # First check for spaCy DATE entities
        sent_doc = nlp(sentence)
        for ent in sent_doc.ents:
            if ent.label_ == 'DATE':
                date_str = ent.text
                has_date = True
                break
                
        # If no spaCy date was found, check regex patterns
        if not has_date:
            for pattern in date_patterns:
                match = re.search(pattern, sentence)
                if match:
                    date_str = match.group(0)
                    has_date = True
                    break
        
        # Today, yesterday, etc.
        time_indicators = ["today", "yesterday", "last week", "last month", "last year", 
                          "this week", "this month", "this year", "next week"]
        
        if not has_date:
            for indicator in time_indicators:
                if indicator in sentence.lower():
                    date_str = indicator.capitalize()
                    has_date = True
                    break
        
        # If we found a date and the sentence is not too long, add it
        if has_date and len(sentence) < 300:
            # Clean up the sentence a bit
            event = sentence.replace(date_str, "").strip()
            if len(event) > 10:  # Make sure we have meaningful content
                dates_events.append({
                    "date": date_str,
                    "event": event
                })
    
    # Take only the top 5 date-events if there are many
    return dates_events[:5]

def determine_category(text):
    """Determine the article category based on keyword frequency"""
    # Dictionary of category keywords
    category_keywords = {
        "Politics": ["government", "president", "election", "vote", "party", "senator", "congress", 
                     "democrat", "republican", "policy", "political", "bill", "law", "court", "justice"],
        "Business": ["market", "stock", "company", "economy", "economic", "finance", "financial", "trade",
                     "investment", "investor", "profit", "bank", "industry", "corporate", "ceo"],
        "Technology": ["tech", "technology", "software", "hardware", "digital", "internet", "computer", "app",
                       "device", "startup", "innovation", "developer", "programming", "ai", "artificial intelligence"],
        "Health": ["health", "medical", "doctor", "patient", "hospital", "disease", "treatment", "drug",
                   "medicine", "vaccine", "virus", "pandemic", "care", "healthcare", "covid"],
        "Sports": ["game", "team", "player", "season", "match", "win", "score", "championship", "coach",
                   "league", "tournament", "athlete", "sport", "football", "soccer", "basketball", "baseball"],
        "Entertainment": ["movie", "film", "show", "music", "actor", "actress", "celebrity", "star", "director",
                          "release", "award", "performance", "entertainment", "hollywood", "tv", "television"],
        "Science": ["science", "research", "study", "scientist", "discovery", "space", "physics", "biology",
                    "chemistry", "experiment", "theory", "academic", "climate", "environment", "earth"]
    }
    
    # Process with spaCy
    doc = nlp(text)
    
    # Count category matches
    category_scores = {category: 0 for category in category_keywords}
    
    # Get all tokens that aren't stop words or punctuation
    words = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    
    for word in words:
        for category, keywords in category_keywords.items():
            if word in keywords:
                category_scores[category] += 1
    
    # Return the category with the highest score
    if all(score == 0 for score in category_scores.values()):
        return "General"
    
    # Find category with max score
    max_score = 0
    max_category = "General"
    for category, score in category_scores.items():
        if score > max_score:
            max_score = score
            max_category = category
    
    return max_category
