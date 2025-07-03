# amazon_scraper.py - FIXED VERSION for your main Streamlit app
import requests
import re
import time
import random
from typing import List, Tuple, Optional, Dict
from urllib.parse import urlparse, parse_qs, unquote
import os
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

def get_scraperapi_key():
    """Get API key from environment or Streamlit secrets"""
    try:
        import streamlit as st
        return st.secrets["SCRAPERAPI_KEY"]
    except:
        return os.getenv('SCRAPERAPI_KEY', '')
    
def check_scraperapi_status():
    """Check ScraperAPI account status"""
    api_key = get_scraperapi_key()
    if not api_key:
        return "No API key found"
    
    try:
        response = requests.get(
            f"http://api.scraperapi.com/account?api_key={api_key}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            remaining = data.get('requestLimit', 0) - data.get('requestCount', 0)
            return f"Credits remaining: {remaining}"
        else:
            return f"Status check failed: {response.status_code}"
    except Exception as e:
        return f"Error checking status: {str(e)}"

def test_scraperapi_key() -> Tuple[bool, str]:
    """Test if ScraperAPI key is working"""
    api_key = get_scraperapi_key()
    
    if not api_key:
        return False, "No API key found in environment variables"
    
    try:
        test_url = "https://httpbin.org/ip"
        params = {
            'api_key': api_key,
            'url': test_url
        }
        
        response = requests.get(
            'http://api.scraperapi.com/', 
            params=params, 
            timeout=15
        )
        
        if response.status_code == 200:
            return True, "API key is working - Real scraping enabled"
        elif response.status_code == 401:
            return False, "Invalid API key"
        elif response.status_code == 403:
            return False, "API key blocked or insufficient credits"
        else:
            return False, f"API returned status code: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, "Request timeout - API might be slow"
    except requests.exceptions.ConnectionError:
        return False, "Connection error - check internet connection"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def convert_to_review_url(url: str) -> Tuple[str, str]:
    """Convert Amazon product URL to WORKING review URL format"""
    if not url or not isinstance(url, str):
        raise ValueError("Invalid URL provided")
    
    url = url.strip()
    
    if 'amazon' not in url.lower():
        raise ValueError("Not an Amazon URL")
    
    url = unquote(url)
    print(f"🔍 Processing URL: {url}")
    
    # Extract product ID using multiple patterns
    product_id = None
    
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/product-reviews/([A-Z0-9]{10})',
        r'/([A-Z0-9]{10})(?:/|$)',
        r'asin=([A-Z0-9]{10})',
        r'productId=([A-Z0-9]{10})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            product_id = match.group(1).upper()
            print(f"✅ Found product ID: {product_id}")
            break
    
    if not product_id:
        # Try to extract from URL path segments
        parsed_url = urlparse(url)
        path_segments = [seg for seg in parsed_url.path.split('/') if seg]
        
        for segment in path_segments:
            if len(segment) == 10 and re.match(r'^[A-Z0-9]{10}$', segment, re.IGNORECASE):
                product_id = segment.upper()
                print(f"✅ Found product ID in path: {product_id}")
                break
    
    if not product_id:
        raise ValueError(f"Could not extract product ID from URL: {url}")
    
    # Determine domain
    domain = 'amazon.com'
    if 'amazon.in' in url.lower():
        domain = 'amazon.in'
    elif 'amazon.co.uk' in url.lower():
        domain = 'amazon.co.uk'
    elif 'amazon.de' in url.lower():
        domain = 'amazon.de'
    
    # ✅ USE THE WORKING FORMAT: Simple product URL + #customerReviews
    review_url = f"https://www.{domain}/dp/{product_id}#customerReviews"
    
    print(f"🔗 Working Review URL: {review_url}")
    
    return review_url, product_id

def get_reviews_from_amazon(url: str, max_reviews: int = 10) -> List[str]:
    """
    Get reviews from Amazon using the WORKING method
    """
    # Check if API is available
    api_working, api_message = test_scraperapi_key()
    
    if not api_working:
        print(f"🧪 Using demo mode: {api_message}")
        return get_sample_reviews()[:max_reviews]
    
    print("🚀 Using real scraping mode with WORKING configuration")
    
    try:
        # Validate and convert URL
        if not url or not isinstance(url, str):
            return ["Error: Invalid URL provided"]
        
        print(f"📡 Starting real scraping for: {url}")
        
        # Convert URL to working review URL
        try:
            review_url, product_id = convert_to_review_url(url)
            print(f"📦 Product ID: {product_id}")
        except ValueError as e:
            return [f"Error: URL conversion failed - {str(e)}"]
        
        # Use the WORKING scraping method
        reviews = _scrape_with_working_config(review_url, max_reviews)
        
        if reviews and len(reviews) > 0:
            # Check if we got actual reviews (not error messages)
            valid_reviews = [r for r in reviews if not _is_error_message(r) and len(r) > 50]
            if valid_reviews:
                print(f"✅ Successfully scraped {len(valid_reviews)} real reviews")
                return valid_reviews
        
        # If scraping failed, return sample data with clear indication
        print("⚠️ Scraping failed, returning sample reviews")
        return [f"Note: Could not scrape real reviews. Showing sample data instead."] + get_sample_reviews()[:max_reviews-1]
        
    except Exception as e:
        print(f"💥 Error in get_reviews_from_amazon: {str(e)}")
        return [f"Error: {str(e)}"]

def _scrape_with_working_config(review_url: str, max_reviews: int) -> List[str]:
    """Use the PROVEN WORKING configuration"""
    api_key = get_scraperapi_key()
    
    if not api_key:
        raise Exception("No ScraperAPI key available")
    
    # ✅ EXACT WORKING CONFIGURATION FROM OUR SUCCESSFUL TEST
    params = {
        'api_key': api_key,
        'url': review_url,
        'render': 'true',        # ESSENTIAL for Amazon reviews
        'wait': '8000',          # 8 second wait for reviews to load
        'premium': 'true'        # Use premium endpoints if available
    }
    
    print(f"🔑 Using PROVEN working ScraperAPI configuration")
    print(f"   URL: {review_url}")
    print(f"   Settings: render=true, wait=8000, premium=true")
    
    try:
        response = requests.get(
            'http://api.scraperapi.com/',
            params=params,
            timeout=120  # Allow time for rendering and loading
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📏 Response length: {len(response.text)} characters")
        
        if response.status_code == 200:
            print("✅ ScraperAPI request successful!")
            reviews = _extract_reviews_from_html(response.text, max_reviews)
            if reviews:
                return reviews
            else:
                print("⚠️ No reviews extracted from HTML")
                raise Exception("Page loaded but no reviews found")
        else:
            raise Exception(f"ScraperAPI: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ ScraperAPI failed: {str(e)}")
        raise e

def _extract_reviews_from_html(html: str, max_reviews: int) -> List[str]:
    """Extract reviews using the PROVEN WORKING selectors"""
    soup = BeautifulSoup(html, 'html.parser')
    reviews = []
    
    print("🔍 Extracting reviews with PROVEN working selectors...")
    
    # ✅ PROVEN WORKING SELECTORS (from our successful test)
    working_selectors = [
        '[data-hook="review-body"] span',  # Primary working selector
        '[data-hook="review-body"]',       # Alternative working selector  
        '.review-text',                    # Backup working selector
    ]
    
    for i, selector in enumerate(working_selectors):
        if len(reviews) >= max_reviews:
            break
            
        print(f"🔍 Trying proven selector {i+1}/{len(working_selectors)}: {selector}")
        review_elements = soup.select(selector)
        print(f"📊 Found {len(review_elements)} elements")
        
        for element in review_elements:
            if len(reviews) >= max_reviews:
                break
            
            review_text = element.get_text(strip=True)
            
            if review_text and len(review_text) > 50:
                cleaned_review = _clean_review_text(review_text)
                if cleaned_review and len(cleaned_review) > 30:
                    # Avoid duplicates
                    if not any(cleaned_review[:100] in existing[:100] for existing in reviews):
                        reviews.append(cleaned_review)
                        print(f"✅ Extracted review {len(reviews)}: {cleaned_review[:80]}...")
        
        if len(reviews) > 0:
            print(f"✅ Successfully found reviews with selector: {selector}")
            break
    
    print(f"🎉 Total reviews extracted: {len(reviews)}")
    return reviews[:max_reviews] if reviews else []

def _clean_review_text(text: str) -> str:
    """Clean review text from Amazon artifacts"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common Amazon artifacts
    artifacts = [
        r'Read more.*$',
        r'Was this review helpful.*$',
        r'\d+ people found this helpful',
        r'Verified Purchase',
        r'Vine Customer Review',
        r'Top \d+ Reviewer',
        r'By .* on .*',
        r'Color:.*?Size:.*?(?=\s|$)',
        r'Style:.*?(?=\s|$)',
        r'Pattern Name:.*?(?=\s|$)',
        r'Size:.*?(?=\s|$)',
        r'Color:.*?(?=\s|$)',
        r'The media could not be loaded.',
        r'See all photos',
        r'Videos for this product',
        r'Click to expand',
        r'Images in this review',
        r'Helpful.*Report.*$',
        r'Report abuse',
        r'Translate review to English',
        r'Show more',
        r'Show less',
        r'…Read more',
        r'Read full review',
    ]
    
    for artifact in artifacts:
        text = re.sub(artifact, '', text, flags=re.IGNORECASE)
    
    # Remove extra spaces and return
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text if len(text) > 20 else ""

def _is_error_message(text: str) -> bool:
    """Check if text is an error message"""
    if not text:
        return True
    
    error_indicators = [
        'error', 'failed', 'blocked', 'unauthorized', 'forbidden',
        'not found', '404', '403', '503', 'timeout', 'connection',
        'invalid', 'denied', 'unavailable'
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in error_indicators)

def get_sample_reviews() -> List[str]:
    """Enhanced sample reviews for demo/fallback"""
    return [
        "The product quality is excellent and exceeded my expectations. The delivery was fast and packaging was secure. Great value for money and I would definitely recommend this to others. The design is modern and fits perfectly with my requirements.",
        
        "Poor build quality and terrible customer service. The item arrived damaged and the replacement process was a nightmare. Not worth the price at all. The material feels cheap and the performance is below average. Very disappointed with this purchase.",
        
        "Good product overall but has some minor issues. The delivery was on time and packaging was good. The price is reasonable for what you get. Some features work well while others could be improved. Customer service was helpful when I contacted them.",
        
        "Amazing product! The quality is top-notch and the design is beautiful. Fast shipping and excellent packaging. The performance exceeds expectations and the value for money is outstanding. Highly recommended for anyone looking for this type of product.",
        
        "Average product with mixed results. The build quality is decent but not exceptional. Delivery was delayed by a few days but packaging was fine. The price is fair but you can find better alternatives. Some features are useful while others are not.",
        
        "Excellent purchase! The product works exactly as described and the quality is superb. Fast delivery and great packaging. The design is sleek and modern. Customer service was responsive when I had questions. Great value for the price.",
        
        "The product is okay but has some limitations. The build quality is acceptable and delivery was on time. The price is slightly high for what you get. Some features are good but the overall performance could be better. Average experience.",
        
        "Outstanding value for money! The build quality is solid and the performance is impressive. Delivery was quick and packaging was professional. The customer service team was very helpful. Would definitely buy again and recommend to others."
    ]

# Test function to verify it works
if __name__ == "__main__":
    print("=== Testing WORKING Amazon Scraper for Main App ===")
    working, message = test_scraperapi_key()
    print(f"API Status: {working}")
    print(f"Message: {message}")
    
    if working:
        print("\n=== Testing Real Scraping ===")
        test_url = "https://www.amazon.in/dp/B08N5WRWNW"
        reviews = get_reviews_from_amazon(test_url, max_reviews=3)
        print(f"Got {len(reviews)} reviews")
        for i, review in enumerate(reviews[:2], 1):
            print(f"Review {i}: {review[:200]}...")
    else:
        print("\n=== Demo Mode Active ===")
        print("Real scraping not available, using sample data")