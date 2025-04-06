import newspaper
import trafilatura

def extract_article_with_newspaper(url):
    """
    Extract article content using newspaper3k
    
    Args:
        url (str): URL of the news article
        
    Returns:
        dict: Dictionary containing article metadata and content
    """
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()
        
        return {
            "success": True,
            "title": article.title,
            "text": article.text,
            "authors": article.authors,
            "publish_date": article.publish_date,
            "top_image": article.top_image,
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def extract_article_with_trafilatura(url):
    """
    Extract article content using trafilatura as a fallback method
    
    Args:
        url (str): URL of the news article
        
    Returns:
        dict: Dictionary containing article content
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        
        if text:
            return {
                "success": True,
                "text": text,
                "url": url
            }
        else:
            return {
                "success": False,
                "error": "Could not extract content from the URL"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def extract_article(url):
    """
    Extract article content using newspaper3k, with trafilatura as fallback
    
    Args:
        url (str): URL of the news article
        
    Returns:
        dict: Dictionary containing article metadata and content
    """
    # Try with newspaper3k first
    result = extract_article_with_newspaper(url)
    
    # If newspaper3k fails, try with trafilatura
    if not result["success"] or not result.get("text"):
        trafilatura_result = extract_article_with_trafilatura(url)
        
        if trafilatura_result["success"]:
            # If we have newspaper3k metadata but no text, combine with trafilatura text
            if "title" in result:
                result["text"] = trafilatura_result["text"]
                result["success"] = True
            else:
                return trafilatura_result
    
    return result
