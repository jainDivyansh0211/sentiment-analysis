# sentiment.py - ML-based sentiment analysis for CV showcase
import re
from typing import Dict, List
import warnings
warnings.filterwarnings("ignore")

# Try to import ML libraries
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
    print("✅ Using TextBlob ML model")
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("⚠️ TextBlob not available")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
    print("✅ Using VADER sentiment model")
except ImportError:
    VADER_AVAILABLE = False
    print("⚠️ VADER not available")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
    print("✅ Transformers available for advanced models")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available")

class MLSentimentAnalyzer:
    """
    ML-based sentiment analyzer using multiple models
    Shows ML skills while being interview-friendly
    """
    
    def __init__(self, model_type="auto"):
        self.model_type = model_type
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the best available ML model"""
        if self.model_type == "auto":
            # Auto-select best available model
            if VADER_AVAILABLE:
                self.model_type = "vader"
                self.model = SentimentIntensityAnalyzer()
                print("🤖 Initialized VADER sentiment model")
            elif TEXTBLOB_AVAILABLE:
                self.model_type = "textblob"
                print("🤖 Initialized TextBlob ML model")
            else:
                self.model_type = "rule_based"
                print("🤖 Using rule-based fallback")
        
        elif self.model_type == "vader" and VADER_AVAILABLE:
            self.model = SentimentIntensityAnalyzer()
            print("🤖 Initialized VADER sentiment model")
        
        elif self.model_type == "textblob" and TEXTBLOB_AVAILABLE:
            print("🤖 Initialized TextBlob ML model")
        
        elif self.model_type == "transformers" and TRANSFORMERS_AVAILABLE:
            try:
                self.model = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=False
                )
                print("🤖 Initialized RoBERTa transformer model")
            except Exception as e:
                print(f"⚠️ Transformer failed: {e}, falling back to VADER")
                if VADER_AVAILABLE:
                    self.model_type = "vader"
                    self.model = SentimentIntensityAnalyzer()
                else:
                    self.model_type = "rule_based"
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment using ML models
        
        Returns:
            Dict with label, score, confidence, and model_used
        """
        if not text or len(text.strip()) < 3:
            return {
                "label": "NEUTRAL", 
                "score": 0.5, 
                "confidence": "low",
                "model_used": self.model_type
            }
        
        try:
            if self.model_type == "vader":
                return self._analyze_with_vader(text)
            elif self.model_type == "textblob":
                return self._analyze_with_textblob(text)
            elif self.model_type == "transformers":
                return self._analyze_with_transformers(text)
            else:
                return self._analyze_rule_based(text)
        except Exception as e:
            print(f"ML model error: {e}, falling back to rule-based")
            return self._analyze_rule_based(text)
    
    def _analyze_with_vader(self, text: str) -> Dict:
        """
        VADER (Valence Aware Dictionary and sEntiment Reasoner)
        - Specifically designed for social media text
        - Handles negations, intensifiers, and punctuation
        - Good for product reviews
        """
        scores = self.model.polarity_scores(text)
        compound = scores['compound']
        
        # VADER returns compound score from -1 to 1
        if compound >= 0.05:
            label = "POSITIVE"
            score = (compound + 1) / 2  # Convert to 0-1 scale
        elif compound <= -0.05:
            label = "NEGATIVE"
            score = 1 - ((compound + 1) / 2)  # Convert to 0-1 scale
        else:
            label = "NEUTRAL"
            score = 0.5
        
        # Confidence based on absolute compound score
        confidence = "high" if abs(compound) > 0.5 else "medium" if abs(compound) > 0.1 else "low"
        
        return {
            "label": label,
            "score": float(score),
            "confidence": confidence,
            "model_used": "VADER (ML)",
            "raw_scores": scores
        }
    
    def _analyze_with_textblob(self, text: str) -> Dict:
        """
        TextBlob sentiment analysis
        - Uses Naive Bayes classifier trained on movie reviews
        - Simple but effective ML approach
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        
        # Convert polarity to label and score
        if polarity > 0.1:
            label = "POSITIVE"
            score = (polarity + 1) / 2
        elif polarity < -0.1:
            label = "NEGATIVE"
            score = 1 - ((polarity + 1) / 2)
        else:
            label = "NEUTRAL"
            score = 0.5
        
        confidence = "high" if abs(polarity) > 0.5 else "medium" if abs(polarity) > 0.2 else "low"
        
        return {
            "label": label,
            "score": float(score),
            "confidence": confidence,
            "model_used": "TextBlob (Naive Bayes)",
            "polarity": polarity,
            "subjectivity": blob.sentiment.subjectivity
        }
    
    def _analyze_with_transformers(self, text: str) -> Dict:
        """
        Transformer-based analysis (RoBERTa)
        - State-of-the-art deep learning model
        - Pre-trained on large Twitter dataset
        """
        # Truncate text for transformer limits
        text = text[:512]
        result = self.model(text)[0]
        
        # Map transformer labels
        label_mapping = {
            'LABEL_0': 'NEGATIVE',
            'LABEL_1': 'NEUTRAL', 
            'LABEL_2': 'POSITIVE',
            'NEGATIVE': 'NEGATIVE',
            'POSITIVE': 'POSITIVE',
            'NEUTRAL': 'NEUTRAL'
        }
        
        label = label_mapping.get(result['label'], result['label'])
        score = result['score']
        confidence = "high" if score > 0.8 else "medium" if score > 0.6 else "low"
        
        return {
            "label": label,
            "score": float(score),
            "confidence": confidence,
            "model_used": "RoBERTa (Transformer)",
            "raw_prediction": result
        }
    
    def _analyze_rule_based(self, text: str) -> Dict:
        """Fallback rule-based analysis"""
        text_lower = text.lower()
        
        positive_words = {
            'excellent', 'great', 'good', 'amazing', 'fantastic', 'wonderful',
            'perfect', 'love', 'like', 'best', 'awesome', 'outstanding',
            'recommend', 'satisfied', 'happy', 'pleased', 'fast', 'quick'
        }
        
        negative_words = {
            'terrible', 'awful', 'bad', 'horrible', 'worst', 'hate',
            'disappointing', 'poor', 'useless', 'broken', 'slow',
            'expensive', 'overpriced', 'waste', 'regret', 'avoid'
        }
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            label = "POSITIVE"
            score = min(0.6 + (pos_count * 0.1), 0.95)
        elif neg_count > pos_count:
            label = "NEGATIVE"
            score = min(0.6 + (neg_count * 0.1), 0.95)
        else:
            label = "NEUTRAL"
            score = 0.5
        
        difference = abs(pos_count - neg_count)
        confidence = "high" if difference >= 2 else "medium" if difference >= 1 else "low"
        
        return {
            "label": label,
            "score": score,
            "confidence": confidence,
            "model_used": "Rule-based (Fallback)"
        }

# Global analyzer instance
analyzer = None

def get_analyzer():
    """Get global ML analyzer instance"""
    global analyzer
    if analyzer is None:
        analyzer = MLSentimentAnalyzer()
    return analyzer

def analyze_sentiment(text: str) -> Dict:
    """
    Main sentiment analysis function
    Uses the best available ML model
    """
    return get_analyzer().analyze_sentiment(text)

def get_model_info() -> Dict:
    """Get information about the current model"""
    current_analyzer = get_analyzer()
    return {
        "model_type": current_analyzer.model_type,
        "available_models": {
            "VADER": VADER_AVAILABLE,
            "TextBlob": TEXTBLOB_AVAILABLE, 
            "Transformers": TRANSFORMERS_AVAILABLE
        }
    }

# Test the implementation
if __name__ == "__main__":
    # Test with different models
    test_texts = [
        "This product is absolutely amazing! Great quality and fast delivery.",
        "Terrible quality, waste of money. Very disappointed.",
        "It's okay, nothing special but does the job."
    ]
    
    print("=== ML Sentiment Analysis Test ===")
    
    for text in test_texts:
        result = analyze_sentiment(text)
        print(f"\nText: {text}")
        print(f"Result: {result['label']} ({result['score']:.3f})")
        print(f"Confidence: {result['confidence']}")
        print(f"Model: {result['model_used']}")
    
    print(f"\nModel Info: {get_model_info()}")