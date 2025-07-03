# aspect_extractor.py - Enhanced version (no additional dependencies)
import re
from typing import List, Dict
from collections import Counter

def extract_aspects(text: str) -> List[str]:
    """
    Enhanced aspect extraction for complex reviews
    Handles technical terms, acronyms, and contextual aspects
    """
    if not text or len(text) < 10:
        return []
    
    text_lower = text.lower()
    found_aspects = []
    
    # 1. ENHANCED DOMAIN-SPECIFIC ASPECTS
    domain_aspects = {
        # Audio/Electronics - Enhanced
        'anc': ['anc', 'active noise cancellation', 'noise cancelling', 'noise canceling', 'noise reduction'],
        'audio quality': ['audio', 'sound quality', 'bass', 'treble', 'audio quality', 'sound', 'music quality'],
        'connectivity': ['connectivity', 'connection', 'connecting', 'bluetooth', 'wifi', 'wireless', 'pairing'],
        'compatibility': ['compatible', 'compatibility', 'works with', 'support', 'macbook', 'iphone', 'android'],
        'battery': ['battery', 'battery life', 'charging', 'power', 'charge'],
        'build quality': ['build', 'construction', 'material', 'build quality', 'durability', 'solid', 'sturdy'],
        'design': ['design', 'look', 'appearance', 'aesthetic', 'style', 'color', 'size'],
        
        # Service aspects - Enhanced
        'warranty': ['warranty', 'guarantee', 'coverage', 'expired', 'coverage expired'],
        'seller': ['seller', 'vendor', 'amazon', 'fake seller', 'refurbished'],
        'delivery': ['delivery', 'shipping', 'arrived', 'packaging', 'box'],
        'customer service': ['customer service', 'support', 'help', 'response'],
        
        # Quality aspects - Enhanced
        'value': ['value', 'price', 'money', 'worth', 'cost', 'value for money'],
        'performance': ['performance', 'speed', 'fast', 'slow', 'working', 'functioning'],
        'features': ['feature', 'function', 'functionality', 'option', 'settings'],
        'usability': ['easy to use', 'user friendly', 'interface', 'setup', 'installation']
    }
    
    # Check domain-specific aspects
    for aspect, keywords in domain_aspects.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_aspects.append(aspect)
                break
    
    # 2. TECHNICAL TERMS AND ACRONYMS
    technical_aspects = _extract_technical_terms(text_lower)
    found_aspects.extend(technical_aspects)
    
    # 3. PATTERN-BASED EXTRACTION (Enhanced)
    pattern_aspects = _extract_pattern_aspects(text_lower)
    found_aspects.extend(pattern_aspects)
    
    # 4. CONTEXTUAL ASPECT EXTRACTION
    context_aspects = _extract_context_aspects(text_lower)
    found_aspects.extend(context_aspects)
    
    # 5. PRODUCT-SPECIFIC EXTRACTION
    product_aspects = _extract_product_specific(text_lower)
    found_aspects.extend(product_aspects)
    
    # Clean and deduplicate
    cleaned_aspects = _clean_and_prioritize(found_aspects, text_lower)
    
    return cleaned_aspects[:12]  # Return top 12 most relevant

def _extract_technical_terms(text: str) -> List[str]:
    """Extract technical terms, acronyms, and product features"""
    technical_terms = []
    
    # Common tech acronyms and terms
    tech_keywords = [
        'anc', 'bluetooth', 'wifi', 'usb', 'hdmi', 'aux', 'nfc', 'apt-x',
        'bass', 'treble', 'frequency', 'hz', 'db', 'watts', 'ohm',
        'led', 'lcd', 'oled', 'amoled', 'retina', 'hd', 'uhd', '4k',
        'cpu', 'gpu', 'ram', 'storage', 'ssd', 'hdd', 'gb', 'tb',
        'ios', 'android', 'windows', 'mac', 'linux'
    ]
    
    words = text.split()
    for word in words:
        # Clean word
        clean_word = re.sub(r'[^\w]', '', word.lower())
        
        # Check if it's a tech term
        if clean_word in tech_keywords:
            technical_terms.append(clean_word)
        
        # Check for acronyms (2-5 uppercase letters)
        if re.match(r'^[A-Z]{2,5}$', word):
            technical_terms.append(word.lower())
    
    return technical_terms

def _extract_pattern_aspects(text: str) -> List[str]:
    """Extract aspects using enhanced linguistic patterns"""
    patterns = [
        # "the X is/was Y" pattern
        (r'the\s+(\w+)\s+(?:is|was|seems|looks|feels)\s+(?:good|bad|great|terrible|excellent|poor|amazing|awful|not|very)', 1),
        
        # "X quality/problem/issue" pattern
        (r'(\w+)\s+(?:quality|problem|issue|trouble|performance|feature)', 1),
        
        # "poor/good/bad/excellent X" pattern  
        (r'(?:poor|good|bad|excellent|great|terrible|amazing|awful|no|zero)\s+(\w+)', 1),
        
        # "X is/was not working/functioning" pattern
        (r'(\w+)\s+(?:is|was)\s+(?:not\s+)?(?:working|functioning|good|bad|terrible|great)', 1),
        
        # "no X" or "lack of X" pattern
        (r'(?:no|lack\s+of|zero|missing)\s+(\w+)', 1),
        
        # "X settings/options" pattern
        (r'(\w+)\s+(?:settings|options|features|functions)', 1),
        
        # "connected to X" or "works with X" pattern
        (r'(?:connected\s+to|works\s+with|compatible\s+with)\s+(\w+)', 1),
        
        # Brand/Product patterns
        (r'(iphone|samsung|macbook|galaxy|note|boat|apple|sony|bose)\s*(\w+)?', 1),
    ]
    
    found_aspects = []
    
    for pattern, group_num in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            aspect = match.group(group_num)
            if len(aspect) > 2 and aspect not in {'this', 'that', 'they', 'very', 'really', 'much', 'with', 'from'}:
                found_aspects.append(aspect.lower())
    
    return found_aspects

def _extract_context_aspects(text: str) -> List[str]:
    """Extract aspects based on sentiment context and nearby words"""
    sentiment_indicators = [
        'good', 'bad', 'great', 'terrible', 'excellent', 'poor', 'amazing', 'awful',
        'love', 'hate', 'disappointed', 'satisfied', 'happy', 'unhappy', 'pleased',
        'impressed', 'shocked', 'surprised', 'expected', 'unexpected', 'works', 'broken'
    ]
    
    found_aspects = []
    words = text.split()
    
    for i, word in enumerate(words):
        clean_word = re.sub(r'[^\w]', '', word.lower())
        
        if clean_word in sentiment_indicators:
            # Look for nouns in the surrounding context (±4 words)
            start = max(0, i - 4)
            end = min(len(words), i + 5)
            context_words = words[start:end]
            
            for ctx_word in context_words:
                clean_ctx = re.sub(r'[^\w]', '', ctx_word.lower())
                
                # Check if it's a potential aspect (filter out common words)
                if (len(clean_ctx) > 3 and 
                    clean_ctx not in sentiment_indicators and
                    clean_ctx not in ['this', 'that', 'they', 'very', 'really', 'much', 'with', 'from', 'about', 'when', 'what', 'where', 'which']):
                    
                    # Boost likelihood if it contains aspect-related substrings
                    if any(indicator in clean_ctx for indicator in 
                          ['qual', 'serv', 'deliver', 'pack', 'connect', 'batter', 'audio', 'sound', 'price', 'valu', 'design', 'build']):
                        found_aspects.append(clean_ctx)
    
    return found_aspects

def _extract_product_specific(text: str) -> List[str]:
    """Extract product-specific aspects based on the review content"""
    product_aspects = []
    
    # Electronics-specific aspects
    if any(term in text for term in ['headphone', 'earphone', 'speaker', 'audio', 'music']):
        audio_aspects = ['bass', 'treble', 'volume', 'clarity', 'anc', 'noise', 'comfort']
        for aspect in audio_aspects:
            if aspect in text:
                product_aspects.append(aspect)
    
    # Phone/Device connectivity
    if any(term in text for term in ['iphone', 'samsung', 'macbook', 'phone', 'laptop']):
        connectivity_aspects = ['pairing', 'connection', 'compatibility', 'bluetooth']
        for aspect in connectivity_aspects:
            if aspect in text:
                product_aspects.append(aspect)
    
    # Service-related (Amazon, delivery, etc.)
    if any(term in text for term in ['amazon', 'seller', 'delivery', 'shipping']):
        service_aspects = ['authenticity', 'packaging', 'timing', 'condition']
        for aspect in service_aspects:
            if any(keyword in text for keyword in [aspect, f'{aspect[:4]}']):
                product_aspects.append(aspect)
    
    return product_aspects

def _clean_and_prioritize(aspects: List[str], original_text: str) -> List[str]:
    """Clean aspects and prioritize based on relevance and frequency"""
    if not aspects:
        return []
    
    # Clean aspects
    cleaned = []
    for aspect in aspects:
        if isinstance(aspect, str):
            clean_aspect = re.sub(r'[^\w\s]', '', aspect.lower().strip())
            if len(clean_aspect) > 2:
                cleaned.append(clean_aspect)
    
    # Count frequency
    aspect_counts = Counter(cleaned)
    
    # Stop words to filter out
    stop_words = {
        'product', 'item', 'thing', 'stuff', 'time', 'year', 'day', 'people', 
        'person', 'way', 'place', 'number', 'part', 'right', 'good', 'new',
        'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old',
        'much', 'many', 'most', 'such', 'even', 'back', 'only', 'come',
        'work', 'life', 'world', 'over', 'school', 'still', 'try', 'made',
        'also', 'after', 'use', 'two', 'how', 'our', 'out', 'said', 'what',
        'about', 'into', 'than', 'them', 'can', 'could', 'when', 'much',
        'get', 'through', 'back', 'from', 'about', 'now', 'way', 'may',
        'say', 'each', 'which', 'their', 'before', 'here', 'take', 'why',
        'well', 'call', 'just', 'where', 'most', 'know', 'get', 'has',
        'had', 'let', 'put', 'end', 'why', 'turn', 'start', 'show',
        'every', 'does', 'got', 'find', 'went', 'look', 'asked', 'later',
        'knew', 'around', 'once', 'came', 'want', 'used', 'make', 'need'
    }
    
    # Priority aspects (more important)
    priority_keywords = [
        'quality', 'anc', 'bass', 'audio', 'battery', 'connectivity', 'connection',
        'delivery', 'seller', 'warranty', 'compatibility', 'design', 'build',
        'value', 'price', 'service', 'performance', 'sound'
    ]
    
    # Score aspects based on relevance
    scored_aspects = []
    seen = set()
    
    for aspect, count in aspect_counts.items():
        if aspect not in stop_words and aspect not in seen and len(aspect) > 2:
            score = count  # Base score from frequency
            
            # Boost score for priority aspects
            if any(priority in aspect for priority in priority_keywords):
                score += 3
            
            # Boost score for technical terms
            if aspect in ['anc', 'bass', 'bluetooth', 'wifi', 'usb']:
                score += 2
            
            # Boost if mentioned multiple times in different contexts
            if count > 1:
                score += 1
            
            scored_aspects.append((aspect, score))
            seen.add(aspect)
    
    # Sort by score (descending) and return aspect names
    scored_aspects.sort(key=lambda x: x[1], reverse=True)
    
    return [aspect for aspect, score in scored_aspects]

def get_aspect_categories(aspects: List[str]) -> Dict[str, List[str]]:
    """
    Enhanced categorization with more specific categories
    """
    categories = {
        'Audio & Sound': ['anc', 'audio quality', 'bass', 'sound', 'audio', 'noise', 'volume', 'music', 'treble', 'clarity'],
        'Connectivity': ['connectivity', 'connection', 'bluetooth', 'wireless', 'pairing', 'compatible', 'compatibility', 'wifi', 'usb'],
        'Build & Design': ['build quality', 'build', 'material', 'durability', 'design', 'size', 'weight', 'comfort', 'construction'],
        'Performance': ['performance', 'speed', 'functionality', 'reliability', 'battery', 'battery life', 'working', 'functioning'],
        'Value & Pricing': ['price', 'value', 'value for money', 'money worth', 'good value', 'great value', 'cost', 'expensive', 'worth'],
        'Service & Support': ['service', 'support', 'customer service', 'customer support', 'seller', 'amazon', 'help', 'response'],
        'Delivery & Packaging': ['delivery', 'shipping', 'packaging', 'delivery time', 'fast delivery', 'slow delivery', 'box', 'arrived'],
        'Warranty & Authenticity': ['warranty', 'guarantee', 'coverage', 'expired', 'fake', 'refurbished', 'authentic', 'coverage expired'],
        'Device Compatibility': ['iphone', 'samsung', 'macbook', 'android', 'ios', 'windows', 'mac', 'galaxy', 'note', 'pro']
    }
    
    categorized = {category: [] for category in categories.keys()}
    categorized['Other'] = []
    
    for aspect in aspects:
        found_category = False
        for category, category_aspects in categories.items():
            if any(cat_aspect in aspect or aspect in cat_aspect for cat_aspect in category_aspects):
                categorized[category].append(aspect)
                found_category = True
                break
        
        if not found_category:
            categorized['Other'].append(aspect)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}

def analyze_aspect_sentiment_context(text: str, aspect: str) -> str:
    """
    Enhanced context extraction for aspects
    """
    sentences = re.split(r'[.!?]+', text)
    
    # Find sentences containing the aspect or related terms
    relevant_sentences = []
    aspect_keywords = _get_aspect_keywords(aspect)
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in aspect_keywords):
            relevant_sentences.append(sentence.strip())
    
    if relevant_sentences:
        # Return the most informative sentence (usually the longest)
        return max(relevant_sentences, key=len)
    
    # If no direct mention, look for contextual mentions
    words = text.lower().split()
    if aspect in words:
        aspect_index = words.index(aspect)
        # Get surrounding context (±10 words)
        start = max(0, aspect_index - 10)
        end = min(len(words), aspect_index + 11)
        context_words = words[start:end]
        return ' '.join(context_words)
    
    return text

def _get_aspect_keywords(aspect: str) -> List[str]:
    """Get related keywords for an aspect to improve context detection"""
    keyword_map = {
        'anc': ['anc', 'noise cancellation', 'noise cancelling', 'active noise'],
        'audio quality': ['audio', 'sound', 'music', 'quality'],
        'bass': ['bass', 'low frequency', 'deep sound'],
        'connectivity': ['connection', 'connect', 'pair', 'bluetooth'],
        'battery': ['battery', 'charge', 'power', 'lasting'],
        'warranty': ['warranty', 'guarantee', 'coverage', 'expired'],
        'seller': ['seller', 'vendor', 'fake', 'refurbished'],
        'delivery': ['delivery', 'shipping', 'arrived', 'package'],
        'compatibility': ['compatible', 'works with', 'support'],
        'build quality': ['build', 'construction', 'material', 'quality'],
        'design': ['design', 'look', 'appearance', 'style'],
        'value': ['value', 'price', 'money', 'worth', 'cost'],
        'performance': ['performance', 'speed', 'working', 'function']
    }
    
    return keyword_map.get(aspect, [aspect])

# Test function for the specific review
def test_with_sample_review():
    """Test with the problematic review from the user"""
    sample_review = """I received this product on 24, Jan 20231. when I checked the box the manufacture year was 2021.2. When I checked the warranty it was showing as "Coverage Expired".3. ANC is very bad. I connected with my friend on a call and when I turned on ANC there was no difference. He was still able to hear all the background noise [ used both Iphone 12 & Samsung Galaxy Note 20 ].4. I tried connecting it to MacBook Pro. It showed connected by it was not working at all.I checked the audio settings and it was not even listed there.5. There is NO BASS.. Not even 1%. Even my previous BOAT neckband had much more bass then this.***AMAZON *** should atleast verify the seller before allowing them to sell these type of products. This a fake seller which is either selling the refurbished product again and again to people or just selling the old products with expired warranties."""
    
    print("🧪 Testing Enhanced Aspect Extraction")
    print("=" * 60)
    print(f"Sample Review: {sample_review[:150]}...")
    print()
    
    aspects = extract_aspects(sample_review)
    print(f"✅ Found {len(aspects)} aspects:")
    for i, aspect in enumerate(aspects, 1):
        print(f"   {i:2d}. {aspect}")
    
    print(f"\n📊 Expected aspects that should be found:")
    expected = ['anc', 'bass', 'connectivity', 'warranty', 'seller', 'audio quality', 'compatibility']
    found_expected = [asp for asp in expected if any(asp in found or found in asp for found in aspects)]
    missing_expected = [asp for asp in expected if asp not in found_expected]
    
    print(f"   ✅ Found: {found_expected}")
    print(f"   ❌ Missing: {missing_expected}")
    
    # Test categorization
    categories = get_aspect_categories(aspects)
    print(f"\n🗂️ Categorized aspects:")
    for category, cat_aspects in categories.items():
        print(f"   📁 {category}: {', '.join(cat_aspects)}")
    
    # Test context extraction for key aspects
    print(f"\n🔍 Context extraction for key aspects:")
    key_aspects = ['anc', 'bass', 'warranty', 'connectivity']
    for aspect in key_aspects:
        if any(aspect in found or found in aspect for found in aspects):
            context = analyze_aspect_sentiment_context(sample_review, aspect)
            print(f"   🎯 {aspect}: \"{context[:100]}...\"")

if __name__ == "__main__":
    test_with_sample_review()