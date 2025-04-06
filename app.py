import streamlit as st
import time
import re
from utils.article_extractor import extract_article
from utils.nlp_processor import process_article
from utils.translator import translate_nlp_result, translate_text, AVAILABLE_LANGUAGES
from assets.newsbot_mascot import NewsBotMascot

# Set page configuration
st.set_page_config(
    page_title="News Summarizer",
    page_icon="📰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Styling for the mascot container */
    div[data-testid="stExpander"] {
        border-radius: 8px;
        margin-bottom: 16px;
    }
    
    /* Make toggles look nicer */
    .stToggle {
        border-radius: 20px;
    }
    
    /* Make buttons more prominent */
    .stButton button {
        font-weight: 500;
        border-radius: 6px;
    }
    
    /* Better progress bars for keywords */
    .stProgress > div > div {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def is_valid_url(url):
    """Check if the provided string is a valid URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))

def display_article_info(article_data, nlp_result, show_mascot=True, language="English"):
    """
    Display the extracted and processed article information
    
    Args:
        article_data (dict): The article data from extraction
        nlp_result (dict): The NLP result data (potentially translated)
        show_mascot (bool): Whether to show the mascot
        language (str): The language to display content in
    """
    # Article metadata
    st.header(article_data.get("title", "Article Summary"))
    
    # Display article category and source link
    col1, col2 = st.columns([1, 1])
    with col1:
        category = nlp_result.get('category', 'Uncategorized')
        st.info(f"Category: {category}")
    with col2:
        st.markdown(f"[Read Original Article]({article_data.get('url', '#')})")
    
    # Get localized section headers if not in English
    if language != "English":
        summary_header = translate_text("Summary", language)
        keywords_header = translate_text("Keywords", language)
        topics_header = translate_text("Main Topics", language)
        people_header = translate_text("Key People Mentioned", language)
        dates_header = translate_text("Important Dates & Events", language)
    else:
        summary_header = "Summary"
        keywords_header = "Keywords"
        topics_header = "Main Topics"
        people_header = "Key People Mentioned"
        dates_header = "Important Dates & Events"
    
    # Summary section
    st.subheader(summary_header)
    st.write(nlp_result.get("summary", "Summary not available"))
    
    # Mascot insights - place after summary for best context
    if show_mascot:
        # Initialize our mascot based on article category
        mascot = NewsBotMascot(category)
        mascot.render(nlp_result, article_data, language)
    
    # Keywords section
    if nlp_result.get("keywords") and len(nlp_result["keywords"]) > 0:
        st.subheader(keywords_header)
        
        # Create columns for the keywords to display them in a grid
        keyword_cols = st.columns(3)
        
        for i, keyword in enumerate(nlp_result["keywords"]):
            col_idx = i % 3
            with keyword_cols[col_idx]:
                # Create a meter-like visualization with the relevance score
                score_percent = int(keyword["relevance"] * 100)
                st.write(f"**{keyword['text']}** ({score_percent}%)")
                st.progress(keyword["relevance"])
    
    # Topics section
    if nlp_result.get("topics") and len(nlp_result["topics"]) > 0:
        st.subheader(topics_header)
        
        # Potentially translate "Related terms" if not in English
        related_terms = "Related terms: " if language == "English" else f"{translate_text('Related terms', language)}: "
        
        for topic in nlp_result["topics"]:
            with st.expander(topic["name"]):
                if topic.get("keywords"):
                    st.write(related_terms + ", ".join(topic["keywords"]))
    
    # People mentioned
    if nlp_result.get("people") and len(nlp_result["people"]) > 0:
        st.subheader(people_header)
        for person in nlp_result["people"]:
            st.markdown(f"• {person}")
    
    # Dates and events
    if nlp_result.get("dates_events") and len(nlp_result["dates_events"]) > 0:
        st.subheader(dates_header)
        for date_event in nlp_result["dates_events"]:
            st.markdown(f"• **{date_event.get('date', 'Date not specified')}**: {date_event.get('event', '')}")
    
    # Article metadata if available
    metadata_items = []
    
    if article_data.get("authors"):
        authors_text = ", ".join(article_data["authors"])
        metadata_items.append(f"**Authors**: {authors_text}")
    
    if article_data.get("publish_date"):
        metadata_items.append(f"**Published**: {article_data['publish_date']}")
    
    if metadata_items:
        st.divider()
        st.caption(" | ".join(metadata_items))

def main():
    # App Header
    st.title("📰 News Article Summarizer")
    st.markdown("""
    Enter a news article URL below to get a concise summary, extracted keywords, identified topics,
    key people mentioned, important dates, and article categorization.
    """)
    
    # Create sidebar for settings
    with st.sidebar:
        st.header("Settings")
        
        # Add a toggle for the mascot
        show_mascot = st.toggle("Show NewsBot Mascot", value=True, 
                                help="Enable or disable the friendly NewsBot mascot that provides insights")
        
        st.divider()
        
        # Language selection dropdown
        st.subheader("Language Settings")
        selected_language = st.selectbox(
            "Summary Language",
            options=list(AVAILABLE_LANGUAGES.keys()),
            index=0,  # Default to English
            help="Choose the language for the article summary and insights"
        )
    
    # URL Input
    url = st.text_input("News Article URL", placeholder="https://example.com/news/article")
    
    # Process Button
    if st.button("Summarize Article", type="primary"):
        if not url:
            st.error("Please enter a URL")
        elif not is_valid_url(url):
            st.error("Please enter a valid URL")
        else:
            # Show progress
            with st.spinner("Extracting article content..."):
                article_data = extract_article(url)
            
            if not article_data["success"]:
                st.error(f"Failed to extract article: {article_data.get('error', 'Unknown error')}")
                st.markdown("""
                **Tips:**
                - Make sure the URL is correct and accessible
                - Ensure the URL points to a news article
                """)
            elif not article_data.get("text"):
                st.error("The article was found but no content could be extracted")
            else:
                # Process with NLP
                with st.spinner("Analyzing article content..."):
                    nlp_result = process_article(
                        article_data["text"], 
                        article_data.get("title", "")
                    )
                
                if not nlp_result["success"]:
                    st.error(f"Failed to analyze article: {nlp_result.get('error', 'Unknown error')}")
                else:
                    # If a non-English language is selected, translate the content
                    if selected_language != "English":
                        with st.spinner(f"Translating content to {selected_language}..."):
                            # Show that we're translating
                            translated_result = translate_nlp_result(nlp_result, selected_language)
                    else:
                        translated_result = nlp_result  # No translation needed
                    
                    # Display results with the translated content
                    display_article_info(article_data, translated_result, show_mascot, selected_language)
    
    # App Footer
    st.divider()
    st.caption("This tool uses newspaper3k for article extraction, spaCy for text analysis, and includes a friendly mascot guide to explain insights.")

if __name__ == "__main__":
    main()
