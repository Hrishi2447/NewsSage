import streamlit as st
import time
import re
from utils.article_extractor import extract_article
from utils.nlp_processor import process_article
from utils.export_utils import add_export_section
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

def display_article_info(article_data, nlp_result, show_mascot=True):
    """Display the extracted and processed article information"""
    # Article metadata
    st.header(article_data.get("title", "Article Summary"))
    
    # Display article category and source link
    col1, col2 = st.columns([1, 1])
    with col1:
        category = nlp_result.get('category', 'Uncategorized')
        st.info(f"Category: {category}")
    with col2:
        st.markdown(f"[Read Original Article]({article_data.get('url', '#')})")
    
    # Summary section
    st.subheader("Summary")
    st.write(nlp_result.get("summary", "Summary not available"))
    
    # Mascot insights - place after summary for best context
    if show_mascot:
        # Initialize our mascot based on article category
        mascot = NewsBotMascot(category)
        mascot.render(nlp_result, article_data)
    
    # Keywords section
    if nlp_result.get("keywords") and len(nlp_result["keywords"]) > 0:
        st.subheader("Keywords")
        
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
        st.subheader("Main Topics")
        
        for topic in nlp_result["topics"]:
            with st.expander(topic["name"]):
                if topic.get("keywords"):
                    st.write("Related terms: " + ", ".join(topic["keywords"]))
    
    # People mentioned
    if nlp_result.get("people") and len(nlp_result["people"]) > 0:
        st.subheader("Key People Mentioned")
        for person in nlp_result["people"]:
            st.markdown(f"• {person}")
    
    # Dates and events
    if nlp_result.get("dates_events") and len(nlp_result["dates_events"]) > 0:
        st.subheader("Important Dates & Events")
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
    
    # Add export options
    add_export_section(article_data, nlp_result)

def main():
    # App Header
    st.title("📰 News Article Summarizer")
    st.markdown("""
    Enter a news article URL below to get a concise summary, extracted keywords, identified topics,
    key people mentioned, important dates, and article categorization. You can export the analysis 
    as PDF or Markdown for sharing or offline reading.
    """)
    
    # Create sidebar for settings
    with st.sidebar:
        st.header("Settings")
        # Add a toggle for the mascot
        show_mascot = st.toggle("Show NewsBot Mascot", value=True, 
                                help="Enable or disable the friendly NewsBot mascot that provides insights")
    
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
                    # Display results
                    display_article_info(article_data, nlp_result, show_mascot)
    
    # App Footer
    st.divider()
    st.caption("This tool uses newspaper3k for article extraction, spaCy for text analysis, and includes a friendly mascot guide to explain insights. Export functionality provided with FPDF and Markdown.")

if __name__ == "__main__":
    main()
