import re
import numpy as np
import spacy
import datetime
from collections import Counter

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
        dict: Dictionary containing summary, entities, category, keywords, and topics
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
        
        # Extract keywords from the article
        keywords = extract_keywords(article_text)
        
        # Identify main topics in the article
        topics = identify_topics(article_text)
        
        return {
            "success": True,
            "summary": summary,
            "people": people,
            "dates_events": dates_events,
            "category": category,
            "keywords": keywords,
            "topics": topics
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

def extract_keywords(text, max_keywords=10):
    """
    Extract the most important keywords from the article using spaCy
    
    Args:
        text (str): The article text
        max_keywords (int): Maximum number of keywords to extract
        
    Returns:
        list: List of keyword dictionaries with text and relevance score
    """
    # Process text with spaCy
    doc = nlp(text)
    
    # We'll focus on nouns, proper nouns, and adjectives as potential keywords
    pos_tags = ['NOUN', 'PROPN', 'ADJ']
    
    # Collect keywords (with frequency)
    keywords = []
    word_freq = Counter()
    
    # First pass - collect candidate keywords and their frequencies
    for token in doc:
        # Check if the token is a potential keyword (right POS and not a stopword)
        if token.pos_ in pos_tags and not token.is_stop and not token.is_punct and len(token.text) > 2:
            # Lemmatize the token to get its base form
            lemma = token.lemma_.lower()
            word_freq[lemma] += 1
    
    # Get the frequency of the most common word for normalization
    max_freq = word_freq.most_common(1)[0][1] if word_freq else 1
    
    # Add normalized keywords with scores
    for word, freq in word_freq.most_common(max_keywords):
        # Calculate a normalized score (0-1)
        score = freq / max_freq
        keywords.append({
            "text": word,
            "relevance": round(score, 2)
        })
    
    return keywords


def identify_topics(text, max_topics=5):
    """
    Identify main topics in the article based on keyword co-occurrence
    
    Args:
        text (str): The article text
        max_topics (int): Maximum number of topics to identify
        
    Returns:
        list: List of topics with their associated keywords
    """
    # Process text with spaCy
    doc = nlp(text)
    
    # Break the document into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Dictionary to track keyword co-occurrences within paragraphs
    keyword_groups = {}
    
    # Preprocess category keywords into sets for faster exact match lookup
    category_keywords = {
        "Politics": set(["government", "president", "election", "vote", "party", "senator", "congress", 
                         "democrat", "republican", "policy", "political", "bill", "law", "court", "justice"]),
        "Business": set(["market", "stock", "company", "economy", "economic", "finance", "financial", "trade",
                         "investment", "investor", "profit", "bank", "industry", "corporate", "ceo"]),
        "Technology": set(["tech", "technology", "software", "hardware", "digital", "internet", "computer", "app",
                           "device", "startup", "innovation", "developer", "programming", "ai", "artificial intelligence"]),
        "Health": set(["health", "medical", "doctor", "patient", "hospital", "disease", "treatment", "drug",
                       "medicine", "vaccine", "virus", "pandemic", "care", "healthcare", "covid"]),
        "Sports": set(["game", "team", "player", "season", "match", "win", "score", "championship", "coach",
                       "league", "tournament", "athlete", "sport", "football", "soccer", "basketball", "baseball"]),
        "Entertainment": set(["movie", "film", "show", "music", "actor", "actress", "celebrity", "star", "director",
                              "release", "award", "performance", "entertainment", "hollywood", "tv", "television"]),
        "Science": set(["science", "research", "study", "scientist", "discovery", "space", "physics", "biology",
                        "chemistry", "experiment", "theory", "academic", "climate", "environment", "earth"])
    }
    
    # Process each paragraph as a potential topic unit
    for i, paragraph in enumerate(paragraphs):
        # Skip very short paragraphs
        if len(paragraph) < 100:
            continue
            
        para_doc = nlp(paragraph)
        
        # Extract key terms from this paragraph
        key_terms = []
        for token in para_doc:
            if (token.pos_ in ['NOUN', 'PROPN'] and 
                not token.is_stop and 
                len(token.text) > 2):
                key_terms.append(token.lemma_.lower())
        
        # If we found multiple key terms, record them as co-occurring
        if len(key_terms) > 1:
            keyword_groups[i] = key_terms
    
    # Create topics based on the keyword groups
    topics = []
    
    # Extract meaningful topics from keyword groups
    for group_id, terms in keyword_groups.items():
        # Find category matches for the terms
        category_matches = {}
        for term in terms:
            for category, keywords in category_keywords.items():
                if term in keywords:
                    category_matches[category] = category_matches.get(category, 0) + 1
        
        # Get the main category for this group
        main_category = max(category_matches.items(), key=lambda x: x[1])[0] if category_matches else "General"
        
        # Create a topic name based on the most frequent terms 
        term_counts = Counter(terms)
        main_terms = [term for term, count in term_counts.most_common(3)]
        
        # Only include meaningful topics with enough terms
        if main_terms:
            topic = {
                "name": f"{main_category}: {', '.join(main_terms)}",
                "keywords": list(set(terms))[:5]
            }
            topics.append(topic)
    
    # Take only top topics based on keyword richness
    sorted_topics = sorted(topics, key=lambda x: len(x["keywords"]), reverse=True)
    
    return sorted_topics[:max_topics]


def determine_category(text):
    """Determine the article category based on keyword frequency"""
    # Preprocess category keywords into sets
    category_keywords = {
        "Politics": set(["government", "president", "election", "vote", "party", "senator", "congress", 
                         "democrat", "republican", "policy", "political", "bill", "law", "court", "justice"]),
        "Business": set(["market", "stock", "company", "economy", "economic", "finance", "financial", "trade",
                         "investment", "investor", "profit", "bank", "industry", "corporate", "ceo"]),
        "Technology": set(["tech", "technology", "software", "hardware", "digital", "internet", "computer", "app",
                           "device", "startup", "innovation", "developer", "programming", "ai", "artificial intelligence"]),
        "Health": set(["health", "medical", "doctor", "patient", "hospital", "disease", "treatment", "drug",
                       "medicine", "vaccine", "virus", "pandemic", "care", "healthcare", "covid"]),
        "Sports": set(["game", "team", "player", "season", "match", "win", "score", "championship", "coach",
                       "league", "tournament", "athlete", "sport", "football", "soccer", "basketball", "baseball"]),
        "Entertainment": set(["movie", "film", "show", "music", "actor", "actress", "celebrity", "star", "director",
                              "release", "award", "performance", "entertainment", "hollywood", "tv", "television"]),
        "Science": set(["science", "research", "study", "scientist", "discovery", "space", "physics", "biology",
                        "chemistry", "experiment", "theory", "academic", "climate", "environment", "earth"])
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
    
    max_category = max(category_scores.items(), key=lambda x: x[1])[0]
    
    return max_category
