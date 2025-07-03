import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_scraperapi_simple():
    """Simple test to check if ScraperAPI is working"""
    api_key = os.getenv('SCRAPERAPI_KEY', '')
    
    if not api_key:
        print("❌ No API key found!")
        print("Add SCRAPERAPI_KEY=your_key_here to your .env file")
        return False
    
    print(f"🔑 Testing API key: {api_key[:10]}...")
    
    # Test with a very simple URL
    test_url = "https://httpbin.org/status/200"
    params = {
        'api_key': api_key,
        'url': test_url
    }
    
    try:
        print("🚀 Making test request...")
        response = requests.get(
            'http://api.scraperapi.com/', 
            params=params, 
            timeout=10
        )
        
        print(f"📊 Response code: {response.status_code}")
        print(f"📝 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ ScraperAPI is working!")
            return True
        elif response.status_code == 401:
            print("❌ Invalid API key")
        elif response.status_code == 403:
            print("❌ API key blocked or out of credits")
        elif response.status_code == 429:
            print("❌ Rate limit exceeded")
        else:
            print(f"❌ Unknown error: {response.status_code}")
            print(f"Response text: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - ScraperAPI is slow or overloaded")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check internet")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return False

if __name__ == "__main__":
    test_scraperapi_simple()