"""
Export utilities for the News Summarizer app.

This module provides functions to export article summaries to different formats,
including PDF and Markdown.
"""
import os
import base64
from fpdf import FPDF
import markdown
import streamlit as st
from datetime import datetime

class SummaryExporter:
    """
    A class that handles exporting article summaries to different formats.
    """
    
    @staticmethod
    def to_markdown(article_data, nlp_result):
        """
        Convert article summary to Markdown format
        
        Args:
            article_data (dict): The article data
            nlp_result (dict): The NLP processing results
            
        Returns:
            str: Markdown formatted text
        """
        category = nlp_result.get('category', 'Uncategorized')
        title = article_data.get('title', 'Article Summary')
        url = article_data.get('url', '')
        summary = nlp_result.get('summary', 'Summary not available')
        
        # Start with title and metadata
        md_lines = [
            f"# {title}",
            f"**Category:** {category}",
            f"**Source:** [{url}]({url})",
            ""
        ]
        
        # Add publication date if available
        if article_data.get('publish_date'):
            md_lines.append(f"**Published:** {article_data['publish_date']}")
            md_lines.append("")
        
        # Add authors if available
        if article_data.get('authors'):
            authors = ", ".join(article_data['authors'])
            md_lines.append(f"**Authors:** {authors}")
            md_lines.append("")
        
        # Summary section
        md_lines.extend([
            "## Summary",
            summary,
            ""
        ])
        
        # Keywords section
        if nlp_result.get('keywords') and len(nlp_result['keywords']) > 0:
            md_lines.append("## Keywords")
            for keyword in nlp_result['keywords']:
                score_percent = int(keyword["relevance"] * 100)
                md_lines.append(f"- **{keyword['text']}** ({score_percent}%)")
            md_lines.append("")
        
        # Topics section
        if nlp_result.get('topics') and len(nlp_result['topics']) > 0:
            md_lines.append("## Main Topics")
            for topic in nlp_result['topics']:
                md_lines.append(f"### {topic['name']}")
                if topic.get('keywords'):
                    md_lines.append(f"Related terms: {', '.join(topic['keywords'])}")
                md_lines.append("")
        
        # People mentioned
        if nlp_result.get('people') and len(nlp_result['people']) > 0:
            md_lines.append("## Key People Mentioned")
            for person in nlp_result['people']:
                md_lines.append(f"- {person}")
            md_lines.append("")
        
        # Dates and events
        if nlp_result.get('dates_events') and len(nlp_result['dates_events']) > 0:
            md_lines.append("## Important Dates & Events")
            for date_event in nlp_result['dates_events']:
                md_lines.append(f"- **{date_event.get('date', 'Date not specified')}**: {date_event.get('event', '')}")
            md_lines.append("")
        
        # Add export timestamp
        md_lines.append(f"---")
        md_lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by News Summarizer*")
        
        return "\n".join(md_lines)
    
    @staticmethod
    def to_pdf(article_data, nlp_result):
        """
        Convert article summary to PDF format
        
        Args:
            article_data (dict): The article data
            nlp_result (dict): The NLP processing results
            
        Returns:
            bytes: PDF content as bytes
        """
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts
        pdf.set_font("Arial", "B", 16)
        
        # Title
        title = article_data.get('title', 'Article Summary')
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.ln(5)
        
        # Metadata
        pdf.set_font("Arial", "B", 12)
        category = nlp_result.get('category', 'Uncategorized')
        pdf.cell(0, 10, f"Category: {category}", 0, 1)
        
        # URL
        url = article_data.get('url', '')
        if url:
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 5, f"Source: {url}", 0, 1)
        
        # Publication date
        if article_data.get('publish_date'):
            pdf.cell(0, 5, f"Published: {article_data['publish_date']}", 0, 1)
        
        # Authors
        if article_data.get('authors'):
            authors = ", ".join(article_data['authors'])
            pdf.cell(0, 5, f"Authors: {authors}", 0, 1)
        
        pdf.ln(5)
        
        # Summary section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Summary", 0, 1)
        pdf.set_font("Arial", "", 11)
        
        summary = nlp_result.get('summary', 'Summary not available')
        # Split text to ensure it fits within the page width
        pdf.multi_cell(0, 6, summary)
        pdf.ln(5)
        
        # Keywords section
        if nlp_result.get('keywords') and len(nlp_result['keywords']) > 0:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Keywords", 0, 1)
            pdf.set_font("Arial", "", 11)
            
            for keyword in nlp_result['keywords']:
                score_percent = int(keyword["relevance"] * 100)
                pdf.cell(0, 6, f"• {keyword['text']} ({score_percent}%)", 0, 1)
            
            pdf.ln(5)
        
        # Topics section
        if nlp_result.get('topics') and len(nlp_result['topics']) > 0:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Main Topics", 0, 1)
            
            for topic in nlp_result['topics']:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 6, topic['name'], 0, 1)
                pdf.set_font("Arial", "", 11)
                
                if topic.get('keywords'):
                    pdf.multi_cell(0, 6, f"Related terms: {', '.join(topic['keywords'])}")
                
                pdf.ln(3)
        
        # People mentioned
        if nlp_result.get('people') and len(nlp_result['people']) > 0:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Key People Mentioned", 0, 1)
            
            pdf.set_font("Arial", "", 11)
            for person in nlp_result['people']:
                pdf.cell(0, 6, f"• {person}", 0, 1)
            
            pdf.ln(5)
        
        # Dates and events
        if nlp_result.get('dates_events') and len(nlp_result['dates_events']) > 0:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Important Dates & Events", 0, 1)
            
            pdf.set_font("Arial", "", 11)
            for date_event in nlp_result['dates_events']:
                date = date_event.get('date', 'Date not specified')
                event = date_event.get('event', '')
                
                pdf.set_font("Arial", "B", 11)
                pdf.cell(40, 6, date + ":", 0, 0)
                
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 6, event)
            
            pdf.ln(5)
        
        # Footer with generation timestamp
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by News Summarizer", 0, 1, 'C')
        
        # The output is already bytes in the newer versions of fpdf
        output = pdf.output(dest='S')
        # Handle string or bytes output depending on FPDF version
        if isinstance(output, str):
            return output.encode('latin1')
        return output
    
    @staticmethod
    def get_markdown_download_link(article_data, nlp_result, link_text="Download Markdown"):
        """
        Generate a download link for Markdown content
        
        Args:
            article_data (dict): The article data
            nlp_result (dict): The NLP processing results
            link_text (str): The text to display for the download link
            
        Returns:
            str: HTML download link
        """
        md_content = SummaryExporter.to_markdown(article_data, nlp_result)
        
        # Create safe filename from article title
        title = article_data.get('title', 'article_summary')
        safe_title = "".join([c if c.isalnum() else "_" for c in title]).lower()
        filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d')}.md"
        
        # Encode markdown content
        b64 = base64.b64encode(md_content.encode()).decode()
        
        # Generate download link with styling
        href = f'data:text/markdown;base64,{b64}'
        download_link = f'''
        <a href="{href}" download="{filename}" style="
            display: inline-block;
            padding: 8px 12px;
            color: #2e7d32;
            background-color: rgba(46, 125, 50, 0.1);
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            border: 1px solid rgba(46, 125, 50, 0.2);
            transition: all 0.2s ease;
            text-align: center;
            width: 100%;">
            {link_text}
        </a>'''
        
        return download_link
    
    @staticmethod
    def get_pdf_download_link(article_data, nlp_result, link_text="Download PDF"):
        """
        Generate a download link for PDF content
        
        Args:
            article_data (dict): The article data
            nlp_result (dict): The NLP processing results
            link_text (str): The text to display for the download link
            
        Returns:
            str: HTML download link
        """
        try:
            pdf_content = SummaryExporter.to_pdf(article_data, nlp_result)
            
            # Create safe filename from article title
            title = article_data.get('title', 'article_summary')
            safe_title = "".join([c if c.isalnum() else "_" for c in title]).lower()
            filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            # Encode PDF content
            b64 = base64.b64encode(pdf_content).decode()
            
            # Generate download link with styling
            href = f'data:application/pdf;base64,{b64}'
            download_link = f'''
            <a href="{href}" download="{filename}" style="
                display: inline-block;
                padding: 8px 12px;
                color: #d32f2f;
                background-color: rgba(211, 47, 47, 0.1);
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                border: 1px solid rgba(211, 47, 47, 0.2);
                transition: all 0.2s ease;
                text-align: center;
                width: 100%;">
                {link_text}
            </a>'''
            
            return download_link
        except Exception as e:
            return f"Error generating PDF: {str(e)}"

def add_export_section(article_data, nlp_result):
    """
    Add export options to the Streamlit app
    
    Args:
        article_data (dict): The article data
        nlp_result (dict): The NLP processing results
    """
    st.divider()
    
    # Create a container with a border and background for the export section
    with st.container():
        # Add custom CSS styling
        st.markdown("""
        <style>
        .export-container {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .export-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: #212529;
        }
        .export-description {
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 15px;
        }
        </style>
        
        <div class="export-container">
            <div class="export-title">📥 Export Your Article Analysis</div>
            <div class="export-description">Save this article analysis for later reference or share it with others.</div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                SummaryExporter.get_markdown_download_link(article_data, nlp_result, "📄 Download as Markdown"),
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                SummaryExporter.get_pdf_download_link(article_data, nlp_result, "📊 Download as PDF"),
                unsafe_allow_html=True
            )
            
        # Close the container div
        st.markdown("</div>", unsafe_allow_html=True)