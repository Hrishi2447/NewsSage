import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import datetime

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')

def create_summary(text, sentences_count=5):
    """
    Create a summary using a simple frequency-based approach
    
    Args:
        text (str): The text to summarize
        sentences_count (int): Number of sentences for the summary
        
    Returns:
        str: A summary of the text
    """
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Skip summarization if text is too short
    if len(sentences) <= sentences_count:
        return text
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    
    # Calculate word frequencies
    word_frequencies = {}
    for word in word_tokenize(text.lower()):
        if word not in stop_words and word.isalnum():
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    
    # Normalize word frequencies
    max_frequency = max(word_frequencies.values(), default=1)
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency
    
    # Score sentences based on word frequencies
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if i not in sentence_scores:
                    sentence_scores[i] = word_frequencies[word]
                else:
                    sentence_scores[i] += word_frequencies[word]
    
    # Get the top-scoring sentences
    summary_sentence_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:sentences_count]
    summary_sentence_indices = sorted(summary_sentence_indices)  # Reorder by original position
    
    # Create summary
    summary = ' '.join([sentences[i] for i in summary_sentence_indices])
    return summary

def process_article(article_text, article_title=""):
    """
    Process the article text using NLTK for summarization, NER, and categorization
    
    Args:
        article_text (str): The text content of the article
        article_title (str, optional): The title of the article
        
    Returns:
        dict: Dictionary containing summary, entities, and category
    """
    try:
        # Create summary using NLTK
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
    """Extract people's names from the text using NLTK's named entity recognition"""
    people = []
    try:
        # Tokenize and tag
        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            words = nltk.word_tokenize(sentence)
            tagged = nltk.pos_tag(words)
            # Use named entity chunker
            entities = nltk.chunk.ne_chunk(tagged)
            
            # Extract person names
            person_names = []
            for entity in entities:
                if isinstance(entity, nltk.tree.Tree) and entity.label() == 'PERSON':
                    name = ' '.join([leaf[0] for leaf in entity.leaves()])
                    if name not in person_names:
                        person_names.append(name)
            
            # Add names from this sentence
            for name in person_names:
                if name not in people:
                    people.append(name)
                    
        # Take only the top 10 people if there are many
        return people[:10]
    except Exception:
        return []

def extract_dates_events(text):
    """Extract dates and associated events from the text"""
    dates_events = []
    
    # Simple regex patterns for date matching
    date_patterns = [
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}\b',
        r'\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b',
        r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}\b'
    ]
    
    sentences = sent_tokenize(text)
    
    for sentence in sentences:
        has_date = False
        date_str = ""
        
        # Check for date patterns
        for pattern in date_patterns:
            match = re.search(pattern, sentence)
            if match:
                date_str = match.group(0)
                has_date = True
                break
        
        # Today, yesterday, etc.
        time_indicators = ["today", "yesterday", "last week", "last month", "last year", 
                          "this week", "this month", "this year", "next week"]
        
        for indicator in time_indicators:
            if indicator in sentence.lower() and not has_date:
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
    
    # Tokenize and remove stop words
    stop_words = set(stopwords.words('english'))
    words = [w.lower() for w in word_tokenize(text) if w.isalpha() and w.lower() not in stop_words]
    
    # Count category matches
    category_scores = {category: 0 for category in category_keywords}
    
    for word in words:
        for category, keywords in category_keywords.items():
            if word in keywords:
                category_scores[category] += 1
    
    # Return the category with the highest score
    if all(score == 0 for score in category_scores.values()):
        return "General"
    
    return max(category_scores, key=category_scores.get)
