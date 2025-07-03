# debug_scraper.py - Step-by-step debugger for Amazon scraping issues
import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import re
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

def step1_check_api_key():
    """Step 1: Verify ScraperAPI key and credits"""
    print("🔍 STEP 1: Checking ScraperAPI Key and Credits")
    print("-" * 50)
    
    api_key = os.getenv('SCRAPERAPI_KEY', '')
    
    if not api_key:
        print("❌ ERROR: No SCRAPERAPI_KEY found in .env file")
        print("💡 Solution: Add SCRAPERAPI_KEY=your_key_here to .env file")
        return False, None
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-5:]}")
    
    # Check account status
    try:
        print("📊 Checking account status...")
        response = requests.get(
            f"http://api.scraperapi.com/account?api_key={api_key}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            request_limit = data.get('requestLimit', 'Unknown')
            request_count = data.get('requestCount', 'Unknown')
            remaining = request_limit - request_count if isinstance(request_limit, int) and isinstance(request_count, int) else 'Unknown'
            
            print(f"✅ Account Status: ACTIVE")
            print(f"📈 Total Limit: {request_limit}")
            print(f"📊 Used: {request_count}")
            print(f"🟢 Remaining: {remaining}")
            
            if isinstance(remaining, int) and remaining <= 0:
                print("❌ ERROR: No credits remaining!")
                return False, api_key
            
            return True, api_key
            
        elif response.status_code == 401:
            print("❌ ERROR: Invalid API key")
            return False, api_key
        elif response.status_code == 403:
            print("❌ ERROR: API key blocked or suspended")
            return False, api_key
        else:
            print(f"⚠️ WARNING: Unexpected status code {response.status_code}")
            print(f"Response: {response.text}")
            return False, api_key
            
    except Exception as e:
        print(f"❌ ERROR: Failed to check account - {str(e)}")
        return False, api_key

def step2_test_simple_request(api_key):
    """Step 2: Test API with simple request"""
    print("\n🧪 STEP 2: Testing ScraperAPI with Simple Request")
    print("-" * 50)
    
    test_url = "https://httpbin.org/ip"
    
    params = {
        'api_key': api_key,
        'url': test_url
    }
    
    try:
        print(f"🌐 Testing with: {test_url}")
        response = requests.get(
            'http://api.scraperapi.com/',
            params=params,
            timeout=15
        )
        
        print(f"📋 Status Code: {response.status_code}")
        print(f"📏 Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            print("✅ SUCCESS: ScraperAPI basic request works")
            try:
                data = response.json()
                print(f"🌍 Your IP via ScraperAPI: {data.get('origin', 'Unknown')}")
            except:
                print("📄 Response (first 200 chars):", response.text[:200])
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def step3_test_amazon_access(api_key):
    """Step 3: Test accessing Amazon with ScraperAPI"""
    print("\n🛒 STEP 3: Testing Amazon Access")
    print("-" * 50)
    
    # Try simple Amazon homepage first
    test_url = "https://www.amazon.com"
    
    configs = [
        {
            'name': 'Basic',
            'params': {
                'api_key': api_key,
                'url': test_url
            }
        },
        {
            'name': 'With Rendering',
            'params': {
                'api_key': api_key,
                'url': test_url,
                'render': 'true',
                'wait': '3000'
            }
        }
    ]
    
    for config in configs:
        print(f"\n🔧 Testing {config['name']} configuration...")
        
        try:
            response = requests.get(
                'http://api.scraperapi.com/',
                params=config['params'],
                timeout=60
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Length: {len(response.text)} chars")
            
            if response.status_code == 200:
                # Check if we got Amazon content
                if 'amazon' in response.text.lower():
                    print(f"   ✅ {config['name']}: Got Amazon content")
                    return True
                else:
                    print(f"   ⚠️ {config['name']}: Got response but not Amazon content")
            else:
                print(f"   ❌ {config['name']}: Failed with {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {config['name']}: Error - {str(e)}")
    
    return False

def step4_test_review_url_conversion(test_product_url):
    """Step 4: Test converting product URL to review URL"""
    print(f"\n🔄 STEP 4: Testing URL Conversion")
    print("-" * 50)
    
    print(f"📥 Input URL: {test_product_url}")
    
    try:
        # Extract product ID using your existing logic
        product_id = None
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, test_product_url, re.IGNORECASE)
            if match:
                product_id = match.group(1).upper()
                print(f"✅ Product ID found: {product_id}")
                break
        
        if not product_id:
            print("❌ ERROR: Could not extract product ID")
            return None
        
        # Determine domain
        parsed = urlparse(test_product_url)
        domain = parsed.netloc.replace('www.', '')
        
        # Generate review URL
        review_url = f"https://www.{domain}/product-reviews/{product_id}/ref=cm_cr_arp_d_viewpnt_rgt?ie=UTF8&filterByStar=all_stars&pageNumber=1"
        
        print(f"🔗 Generated Review URL: {review_url}")
        
        return review_url
        
    except Exception as e:
        print(f"❌ ERROR in URL conversion: {str(e)}")
        return None

def step5_test_review_scraping(api_key, review_url):
    """Step 5: Test actual review scraping"""
    print(f"\n📚 STEP 5: Testing Review Scraping")
    print("-" * 50)
    
    print(f"🎯 Target URL: {review_url[:80]}...")
    
    # Test different ScraperAPI configurations
    configs = [
        {
            'name': 'Premium + Render',
            'params': {
                'api_key': api_key,
                'url': review_url,
                'render': 'true',
                'wait': '8000',
                'premium': 'true',
                'country_code': 'us',
            }
        },
        {
            'name': 'Standard + Render',
            'params': {
                'api_key': api_key,
                'url': review_url,
                'render': 'true',
                'wait': '5000',
            }
        },
        {
            'name': 'Basic',
            'params': {
                'api_key': api_key,
                'url': review_url,
            }
        }
    ]
    
    for config in configs:
        print(f"\n🧪 Testing {config['name']}...")
        
        try:
            response = requests.get(
                'http://api.scraperapi.com/',
                params=config['params'],
                timeout=120  # Longer timeout for reviews
            )
            
            print(f"   📊 Status: {response.status_code}")
            print(f"   📏 Length: {len(response.text)} chars")
            
            if response.status_code == 200:
                # Check for review content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Multiple selectors to try
                selectors = [
                    '[data-hook="review-body"] span',
                    '[data-hook="review-body"]',
                    '.cr-original-review-text',
                    '.review-text'
                ]
                
                total_reviews = 0
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        print(f"   🎯 Selector '{selector}': {len(elements)} elements")
                        total_reviews += len(elements)
                        
                        # Show sample review text
                        for i, elem in enumerate(elements[:2]):
                            text = elem.get_text(strip=True)
                            if text and len(text) > 20:
                                print(f"      📝 Sample {i+1}: {text[:100]}...")
                
                if total_reviews > 0:
                    print(f"   ✅ SUCCESS: Found {total_reviews} reviews with {config['name']}")
                    return True, response.text
                else:
                    print(f"   ⚠️ No reviews found with {config['name']}")
                    
                    # Check for blocking indicators
                    page_text = response.text.lower()
                    blocking_signs = ['robot', 'captcha', 'blocked', 'unusual traffic']
                    if any(sign in page_text for sign in blocking_signs):
                        print(f"   🚫 Possible blocking detected")
                    
            else:
                print(f"   ❌ Failed: {response.status_code}")
                if response.status_code == 403:
                    print(f"      💡 This might indicate API limits or blocking")
                    
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    return False, None

def step6_analyze_html(html_content):
    """Step 6: Analyze the HTML structure"""
    print(f"\n🔍 STEP 6: Analyzing HTML Structure")
    print("-" * 50)
    
    if not html_content:
        print("❌ No HTML content to analyze")
        return
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check page title
    title = soup.find('title')
    if title:
        print(f"📄 Page Title: {title.get_text()}")
    
    # Look for data-hook attributes
    data_hooks = soup.find_all(attrs={"data-hook": True})
    unique_hooks = list(set(elem.get('data-hook') for elem in data_hooks))
    print(f"🏷️ Found data-hook attributes: {unique_hooks[:10]}")
    
    # Check for review-related keywords
    page_text = soup.get_text().lower()
    review_keywords = ['customer review', 'verified purchase', 'helpful', 'star rating']
    found_keywords = [kw for kw in review_keywords if kw in page_text]
    print(f"🔑 Review keywords found: {found_keywords}")
    
    # Save HTML for manual inspection
    try:
        with open('debug_amazon_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"💾 HTML saved to 'debug_amazon_page.html' for manual inspection")
    except Exception as e:
        print(f"⚠️ Could not save HTML: {str(e)}")

def run_complete_debug(test_url):
    """Run all debugging steps"""
    print("🔧 AMAZON SCRAPING COMPLETE DEBUGGER")
    print("=" * 60)
    print(f"🎯 Testing URL: {test_url}")
    print("=" * 60)
    
    # Step 1: Check API key
    api_working, api_key = step1_check_api_key()
    if not api_working:
        print("\n❌ STOPPING: API key issues must be resolved first")
        return
    
    input("\n⏯️  Press ENTER to continue to Step 2...")
    
    # Step 2: Test simple request
    if not step2_test_simple_request(api_key):
        print("\n❌ STOPPING: Basic API requests not working")
        return
    
    input("\n⏯️  Press ENTER to continue to Step 3...")
    
    # Step 3: Test Amazon access
    if not step3_test_amazon_access(api_key):
        print("\n⚠️ WARNING: Amazon access issues detected, but continuing...")
    
    input("\n⏯️  Press ENTER to continue to Step 4...")
    
    # Step 4: Test URL conversion
    review_url = step4_test_review_url_conversion(test_url)
    if not review_url:
        print("\n❌ STOPPING: URL conversion failed")
        return
    
    input("\n⏯️  Press ENTER to continue to Step 5...")
    
    # Step 5: Test review scraping
    success, html_content = step5_test_review_scraping(api_key, review_url)
    
    if html_content:
        input("\n⏯️  Press ENTER to analyze HTML structure...")
        step6_analyze_html(html_content)
    
    # Final recommendations
    print(f"\n💡 FINAL DIAGNOSIS")
    print("=" * 30)
    
    if success:
        print("✅ SUCCESS: Your scraping should work!")
        print("💡 If it's still not working in your main app, check:")
        print("   - Make sure you're using the same configuration")
        print("   - Check for any code differences")
        print("   - Verify error handling is not hiding success")
    else:
        print("❌ ISSUES DETECTED:")
        if not api_working:
            print("   🔑 API key or credits problem")
        else:
            print("   🛒 Amazon blocking or review page structure changed")
            print("   💡 Try: Different wait times, premium endpoints, or other domains")

if __name__ == "__main__":
    # Test with a common Amazon URL
    test_url = "https://www.amazon.in/dp/B08N5WRWNW"
    run_complete_debug(test_url)