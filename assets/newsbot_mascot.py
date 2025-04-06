"""
NewsBot Mascot Module

This module contains the NewsBot mascot class that provides friendly explanations
about news article insights.
"""
import random
import streamlit as st
from utils.translator import translate_text

class NewsBotMascot:
    """
    A playful mascot that provides explanations and insights about news articles,
    with different personalities based on the article's content category.
    """
    
    # Different mascot personalities based on news categories
    PERSONALITIES = {
        "Politics": {
            "name": "PoliBot",
            "emoji": "🧐",
            "color": "#B45309",  # Amber
            "traits": ["analytical", "balanced", "diplomatic"],
            "phrases": [
                "Let me break down the political landscape for you...",
                "The political implications here are fascinating!",
                "This policy development is worth understanding...",
                "Between the political lines, we can see...",
            ]
        },
        "Business": {
            "name": "BizBot",
            "emoji": "💼",
            "color": "#065F46",  # Emerald
            "traits": ["practical", "strategic", "data-driven"],
            "phrases": [
                "Here's the business breakdown...",
                "Let's analyze these market trends...",
                "From a business perspective, this means...",
                "The financial implications are significant...",
            ]
        },
        "Technology": {
            "name": "TechBot",
            "emoji": "🤖",
            "color": "#1E40AF",  # Blue
            "traits": ["innovative", "forward-thinking", "enthusiastic"],
            "phrases": [
                "Here's the tech scoop...",
                "Let me decode this tech development...",
                "The innovation here is remarkable...",
                "From a technical standpoint, this means...",
            ]
        },
        "Science": {
            "name": "SciBot",
            "emoji": "🔬",
            "color": "#4338CA",  # Indigo
            "traits": ["curious", "precise", "methodical"],
            "phrases": [
                "The science here is fascinating...",
                "Let me explain this scientific breakthrough...",
                "From a scientific perspective, this means...",
                "The research implications are significant...",
            ]
        },
        "Health": {
            "name": "HealthBot",
            "emoji": "⚕️",
            "color": "#059669",  # Green
            "traits": ["caring", "informative", "supportive"],
            "phrases": [
                "Here's what this means for your health...",
                "The health implications are important...",
                "From a wellness perspective, understand that...",
                "This health development is worth noting...",
            ]
        },
        "Sports": {
            "name": "SportBot",
            "emoji": "🏆",
            "color": "#B91C1C",  # Red
            "traits": ["energetic", "competitive", "team-oriented"],
            "phrases": [
                "Here's the play-by-play...",
                "The game strategy here is fascinating...",
                "From a sports perspective, this means...",
                "This athletic performance is remarkable...",
            ]
        },
        "Entertainment": {
            "name": "EntBot",
            "emoji": "🎭",
            "color": "#7C3AED",  # Purple
            "traits": ["creative", "expressive", "trendy"],
            "phrases": [
                "Here's the entertainment scoop...",
                "The cultural impact here is significant...",
                "From a creative standpoint, this means...",
                "This artistic development is fascinating...",
            ]
        },
        "Uncategorized": {
            "name": "NewsBot",
            "emoji": "📰",
            "color": "#2563EB",  # Blue
            "traits": ["helpful", "informative", "friendly"],
            "phrases": [
                "Let me explain what's happening here...",
                "Here's what you need to know...",
                "The key points to understand are...",
                "Looking at this news, I can tell you...",
            ]
        }
    }
    
    def __init__(self, article_category="Uncategorized"):
        """
        Initialize the NewsBot mascot with the appropriate personality
        based on the article category.
        
        Args:
            article_category (str): The category of the article
        """
        # Default to Uncategorized if the category doesn't match
        self.personality = self.PERSONALITIES.get(
            article_category, 
            self.PERSONALITIES["Uncategorized"]
        )
        
        self.name = self.personality["name"]
        self.emoji = self.personality["emoji"]
        self.color = self.personality["color"]
        self.traits = self.personality["traits"]
    
    def get_greeting(self):
        """Return a random greeting from the mascot"""
        greetings = [
            f"Hi there! I'm {self.name} {self.emoji}, your news guide.",
            f"Hello! {self.name} {self.emoji} here to help you understand this article.",
            f"Greetings! I'm {self.name} {self.emoji}, ready to break down this news for you.",
            f"{self.emoji} {self.name} at your service! Let's explore this article together."
        ]
        return random.choice(greetings)
    
    def get_random_phrase(self):
        """Return a random characteristic phrase for this mascot personality"""
        return random.choice(self.personality["phrases"])
    
    def explain_summary(self, word_count, reading_time):
        """
        Provide a playful explanation about the article summary statistics
        
        Args:
            word_count (int): Number of words in the article
            reading_time (int): Estimated reading time in minutes
            
        Returns:
            str: A friendly explanation of the article stats
        """
        saved_time = reading_time - (reading_time // 4)
        
        explanations = [
            f"This article is about {word_count} words, which would take around {reading_time} minutes to read. "
            f"With my summary, you'll save about {saved_time} minutes! {self.emoji}",
            
            f"The original article is {word_count} words long (about {reading_time} min read). "
            f"My summary helps you get the key points in just {reading_time // 4} minutes! {self.emoji}",
            
            f"I've condensed a {reading_time}-minute article ({word_count} words) into a quick summary "
            f"that saves you {saved_time} minutes of reading time! {self.emoji}"
        ]
        
        return random.choice(explanations)
    
    def explain_keywords(self, top_keywords):
        """
        Provide insights about the top keywords in the article
        
        Args:
            top_keywords (list): List of the top keywords from the article
            
        Returns:
            str: An explanation about what the keywords reveal
        """
        keyword_texts = [kw["text"] for kw in top_keywords[:3]]
        keywords_str = ", ".join([f"'{k}'" for k in keyword_texts])
        
        explanations = [
            f"The keywords {keywords_str} tell me this article focuses on "
            f"specific concepts you might want to explore further. {self.emoji}",
            
            f"I notice {keywords_str} are key terms in this article. "
            f"These concepts are central to understanding the main points. {self.emoji}",
            
            f"Pay special attention to {keywords_str} as you read. "
            f"These terms highlight the article's core focus. {self.emoji}"
        ]
        
        return random.choice(explanations)
    
    def explain_entities(self, people_count, dates_count):
        """
        Provide insights about the entities (people, dates) mentioned in the article
        
        Args:
            people_count (int): Number of people mentioned
            dates_count (int): Number of dates/events mentioned
            
        Returns:
            str: An explanation about what the entities reveal
        """
        if people_count == 0 and dates_count == 0:
            return f"This article doesn't focus on specific people or events, " \
                   f"but rather on broader concepts and ideas. {self.emoji}"
                   
        if people_count > 0 and dates_count == 0:
            people_text = "person" if people_count == 1 else "people"
            return f"This article mentions {people_count} key {people_text} but doesn't focus on " \
                   f"specific dates or events, suggesting it's about individuals rather than a timeline. {self.emoji}"
                   
        if people_count == 0 and dates_count > 0:
            dates_text = "date/event" if dates_count == 1 else "dates/events"
            return f"This article focuses on {dates_count} important {dates_text} " \
                   f"without emphasizing specific individuals, suggesting it's more about events than people. {self.emoji}"
        
        # Both people and dates are mentioned
        people_text = "person" if people_count == 1 else "people"
        dates_text = "date/event" if dates_count == 1 else "dates/events"
        return f"With {people_count} key {people_text} and {dates_count} important {dates_text}, " \
               f"this article connects individuals to specific occurrences or timeframes. {self.emoji}"
    
    def render(self, nlp_result, article_data, language="English"):
        """
        Render the mascot and its explanations in the Streamlit app
        
        Args:
            nlp_result (dict): The NLP processing results
            article_data (dict): The article data
            language (str): The language for mascot messages (default is English)
        """
        # Calculate some statistics
        word_count = len(article_data.get("text", "").split())
        # Average reading speed is about 200-250 words per minute
        reading_time = max(1, word_count // 230)
        
        # Count entities
        people_count = len(nlp_result.get("people", []))
        dates_count = len(nlp_result.get("dates_events", []))
        
        # Get top keywords if available
        top_keywords = nlp_result.get("keywords", [])[:3] if nlp_result.get("keywords") else []
        
        # Generate all mascot messages
        greeting = self.get_greeting()
        phrase = self.get_random_phrase()
        stats_msg = self.explain_summary(word_count, reading_time)
        keywords_msg = self.explain_keywords(top_keywords) if top_keywords else ""
        entities_msg = self.explain_entities(people_count, dates_count)
        trait = random.choice(self.traits)
        tip_msg = f"Being {trait} as I am, I'd suggest focusing on how this news relates to broader trends in this field."
        
        # Translate messages if not in English
        if language != "English":
            greeting = translate_text(greeting, language)
            phrase = translate_text(phrase, language)
            stats_msg = translate_text(stats_msg, language)
            if keywords_msg:
                keywords_msg = translate_text(keywords_msg, language)
            entities_msg = translate_text(entities_msg, language)
            tip_msg = translate_text(tip_msg, language)
            
            # Also translate the section titles
            article_stats_title = translate_text("Article Stats", language)
            keywords_title = translate_text("Keywords", language)
            people_events_title = translate_text("People & Events", language)
            insights_title = translate_text(f"{self.name}'s Insights", language)
        else:
            article_stats_title = "Article Stats"
            keywords_title = "Keywords"
            people_events_title = "People & Events"
            insights_title = f"{self.name}'s Insights"
        
        # Create a stylish container for the mascot
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background-color: {self.color}15; 
                    border-left: 4px solid {self.color}; 
                    border-radius: 4px; 
                    padding: 15px; 
                    margin-bottom: 20px;
                ">
                    <h3 style="color: {self.color}; margin-top: 0;">{self.emoji} {insights_title}</h3>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Greeting and introduction
            st.markdown(f"**{greeting}** {phrase}")
            
            # Article statistics
            st.markdown(f"**{article_stats_title}**: {stats_msg}")
            
            # Only show keywords explanation if we have keywords
            if top_keywords:
                st.markdown(f"**{keywords_title}**: {keywords_msg}")
            
            # Show entities explanation
            st.markdown(f"**{people_events_title}**: {entities_msg}")
            
            # Wrap-up with a tip based on the mascot's personality
            st.markdown(f"_{tip_msg}_")