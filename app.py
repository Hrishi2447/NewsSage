import streamlit as st
import time
import re
from utils.article_extractor import extract_article
from utils.nlp_processor import process_article

# Set page configuration
st.set_page_config(
    page_title="News Summarizer",
    page_icon="📰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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

def display_article_info(article_data, nlp_result):
    """Display the extracted and processed article information"""
    # Article metadata
    st.header(article_data.get("title", "Article Summary"))
    
    # Display article category and source link
    col1, col2 = st.columns([1, 1])
    with col1:
        st.info(f"Category: {nlp_result.get('category', 'Uncategorized')}")
    with col2:
        st.markdown(f"[Read Original Article]({article_data.get('url', '#')})")
    
    # Summary section
    st.subheader("Summary")
    st.write(nlp_result.get("summary", "Summary not available"))
    
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

def main():
    # App Header
    st.title("📰 News Article Summarizer")
    st.markdown("""
    Enter a news article URL below to get a concise summary, key people mentioned, 
    important dates, and article categorization.
    """)
    
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
                    display_article_info(article_data, nlp_result)
    
    # App Footer
    st.divider()
    st.caption("This tool uses newspaper3k for article extraction and OpenAI for text analysis.")

if __name__ == "__main__":
    main()
