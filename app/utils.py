# utils.py - Enhanced for ML integration
import re
import pandas as pd
from typing import List, Dict, Any
import streamlit as st

def colored_chip(sentiment: str, score: float) -> str:
    """Create a colored chip for sentiment display with enhanced ML styling"""
    # Enhanced color mapping with gradients based on ML confidence
    if sentiment == 'POSITIVE':
        if score > 0.8:
            color = '#00C851'  # Strong green for high confidence
            bg_color = '#E8F5E8'
        elif score > 0.6:
            color = '#2E7D32'  # Medium green
            bg_color = '#F1F8E9'
        else:
            color = '#4CAF50'  # Light green for lower confidence
            bg_color = '#F9FBE7'
        icon = '😊'
    elif sentiment == 'NEGATIVE':
        if score > 0.8:
            color = '#FF4444'  # Strong red for high confidence
            bg_color = '#FFEBEE'
        elif score > 0.6:
            color = '#D32F2F'  # Medium red
            bg_color = '#FFCDD2'
        else:
            color = '#F44336'  # Light red for lower confidence
            bg_color = '#FFEBEE'
        icon = '😞'
    else:  # NEUTRAL
        color = '#FF8F00'  # Orange
        bg_color = '#FFF8E1'
        icon = '😐'
    
    # Create styled chip with hover effect and ML confidence indicator
    chip_html = f"""
    <span style="
        background-color: {bg_color};
        color: {color};
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85em;
        font-weight: 600;
        border: 1px solid {color}40;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    " title="ML Confidence: {score:.3f}">
        {icon} {sentiment} ({score:.2f})
    </span>
    """
    return chip_html

def split_clauses(text: str) -> List[str]:
    """Enhanced clause splitting for better ML context extraction"""
    if not text or not isinstance(text, str):
        return []
    
    text = text.strip()
    if len(text) < 3:
        return []
    
    # Enhanced splitting with more sophisticated patterns
    delimiters = [
        r'\.\s+',  # Period followed by space
        r';\s+',   # Semicolon followed by space
        r',\s+(?:and|but|however|although|though|while|moreover|furthermore)\s+',  # Coordinating conjunctions
        r'!\s+',   # Exclamation followed by space
        r'\?\s+',  # Question followed by space
    ]
    
    # Create combined regex pattern
    pattern = '|'.join(f'({delimiter})' for delimiter in delimiters)
    
    # Split text
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    
    # Clean and filter clauses
    clauses = []
    for part in parts:
        if part and not re.match(r'^[.,;!?\s]+, part):  # Skip delimiter-only parts'):
            clause = part.strip()
            if len(clause) > 10:  # Only keep substantial clauses
                clauses.append(clause)
    
    return clauses if clauses else [text]

def preprocess_text_for_ml(text: str) -> str:
    """Enhanced text preprocessing specifically for ML models"""
    if not text or not isinstance(text, str):
        return ""
    
    # Basic cleaning
    text = text.strip()
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Handle contractions for better ML processing
    contractions = {
        "won't": "will not",
        "can't": "cannot",
        "don't": "do not",
        "doesn't": "does not",
        "isn't": "is not",
        "wasn't": "was not",
        "weren't": "were not",
        "haven't": "have not",
        "hasn't": "has not",
        "wouldn't": "would not",
        "couldn't": "could not",
        "shouldn't": "should not"
    }
    
    for contraction, expansion in contractions.items():
        text = re.sub(r'\b' + contraction + r'\b', expansion, text, flags=re.IGNORECASE)
    
    # Remove excessive punctuation but keep sentence structure
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    text = re.sub(r'[.]{3,}', '...', text)
    
    return text.strip()

def validate_review_text(text: str) -> tuple:
    """Enhanced validation with ML model considerations"""
    if not text or not isinstance(text, str):
        return False, "Text is empty or not a string"
    
    text = text.strip()
    
    if len(text) < 5:
        return False, "Text is too short for meaningful ML analysis (minimum 5 characters)"
    
    if len(text) > 5000:
        return False, "Text is too long for efficient ML processing (maximum 5000 characters)"
    
    # Check for meaningful content
    word_count = len(text.split())
    if word_count < 2:
        return False, "Text needs at least 2 words for aspect-based analysis"
    
    # Check for excessive repetition (potential spam)
    unique_words = len(set(text.lower().split()))
    if word_count > 10 and unique_words / word_count < 0.3:
        return False, "Text appears to be repetitive or spam-like"
    
    return True, "Valid text for ML analysis"

def create_ml_summary_stats(results: List[Dict]) -> Dict:
    """Create enhanced summary statistics with ML model insights"""
    if not results:
        return {}
    
    df = pd.DataFrame(results)
    
    # Basic counts
    total_aspects = len(df)
    total_reviews = len(df['Review'].unique()) if 'Review' in df.columns else 0
    
    # Sentiment distribution
    sentiment_counts = df['Sentiment'].value_counts().to_dict() if 'Sentiment' in df.columns else {}
    
    # Calculate percentages
    total = len(df)
    sentiment_percentages = {
        sentiment: (count / total) * 100 
        for sentiment, count in sentiment_counts.items()
    } if total > 0 else {}
    
    # ML-specific statistics
    ml_stats = {}
    if 'ML_Model' in df.columns:
        ml_stats['model_usage'] = df['ML_Model'].value_counts().to_dict()
    
    if 'Score' in df.columns:
        ml_stats['avg_confidence'] = df['Score'].mean()
        ml_stats['confidence_std'] = df['Score'].std()
        ml_stats['high_confidence_count'] = len(df[df['Score'] > 0.8])
    
    if 'Confidence' in df.columns:
        ml_stats['confidence_distribution'] = df['Confidence'].value_counts().to_dict()
    
    return {
        'total_reviews': total_reviews,
        'total_aspects': total_aspects,
        'sentiment_counts': sentiment_counts,
        'sentiment_percentages': sentiment_percentages,
        'ml_statistics': ml_stats
    }

def display_ml_metrics(results: List[Dict]):
    """Display enhanced metrics with ML insights in Streamlit"""
    if not results:
        return
    
    stats = create_ml_summary_stats(results)
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Reviews", stats.get('total_reviews', 0))
    
    with col2:
        st.metric("🎯 Total Aspects", stats.get('total_aspects', 0))
    
    with col3:
        positive_count = stats.get('sentiment_counts', {}).get('POSITIVE', 0)
        st.metric("😊 Positive", positive_count)
    
    with col4:
        negative_count = stats.get('sentiment_counts', {}).get('NEGATIVE', 0)
        st.metric("😞 Negative", negative_count)
    
    # ML-specific metrics
    ml_stats = stats.get('ml_statistics', {})
    if ml_stats:
        st.subheader("🤖 ML Model Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'avg_confidence' in ml_stats:
                avg_conf = ml_stats['avg_confidence']
                st.metric("📊 Avg ML Confidence", f"{avg_conf:.3f}")
        
        with col2:
            if 'high_confidence_count' in ml_stats:
                high_conf = ml_stats['high_confidence_count']
                total = stats.get('total_aspects', 1)
                percentage = (high_conf / total) * 100
                st.metric("🎯 High Confidence", f"{high_conf} ({percentage:.1f}%)")

def format_time(seconds: float) -> str:
    """Format time in human readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:.0f}m {remaining_seconds:.0f}s"

def safe_get(dictionary: dict, key: str, default=None):
    """Safely get value from dictionary"""
    try:
        return dictionary.get(key, default)
    except (AttributeError, KeyError):
        return default

def create_ml_export_data(results: List[Dict], include_metadata: bool = True) -> pd.DataFrame:
    """Create DataFrame for export with ML model metadata"""
    if not results:
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    
    if include_metadata:
        # Add ML-specific metadata
        df['Analysis_Timestamp'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if 'Context' in df.columns:
            df['Context_Length'] = df['Context'].astype(str).str.len()
        
        if 'Score' in df.columns:
            df['Confidence_Category'] = df['Score'].apply(
                lambda x: 'High' if x > 0.8 else 'Medium' if x > 0.6 else 'Low'
            )
        
        # Add aspect categories
        if 'Aspect' in df.columns:
            from aspect_extractor import get_aspect_categories
            unique_aspects = df['Aspect'].unique().tolist()
            categories = get_aspect_categories(unique_aspects)
            
            aspect_to_category = {}
            for category, aspects in categories.items():
                for aspect in aspects:
                    aspect_to_category[aspect] = category
            
            df['Aspect_Category'] = df['Aspect'].map(aspect_to_category).fillna('Other')
    
    return df

def calculate_ml_performance_metrics(results: List[Dict]) -> Dict[str, Any]:
    """Calculate ML model performance metrics"""
    if not results:
        return {}
    
    df = pd.DataFrame(results)
    
    metrics = {}
    
    # Confidence distribution
    if 'Score' in df.columns:
        scores = df['Score']
        metrics['confidence_stats'] = {
            'mean': float(scores.mean()),
            'std': float(scores.std()),
            'min': float(scores.min()),
            'max': float(scores.max()),
            'high_confidence_ratio': len(scores[scores > 0.8]) / len(scores)
        }
    
    # Model usage if available
    if 'ML_Model' in df.columns:
        model_counts = df['ML_Model'].value_counts()
        metrics['model_distribution'] = model_counts.to_dict()
        metrics['primary_model'] = model_counts.index[0] if len(model_counts) > 0 else None
    
    # Sentiment distribution
    if 'Sentiment' in df.columns:
        sentiment_counts = df['Sentiment'].value_counts()
        total = len(df)
        metrics['sentiment_distribution'] = {
            sentiment: {
                'count': int(count),
                'percentage': float((count / total) * 100)
            }
            for sentiment, count in sentiment_counts.items()
        }
    
    return metrics

# Enhanced error handling for ML pipeline
class MLProcessingError(Exception):
    """Custom exception for ML processing errors"""
    pass

def safe_ml_process(func, *args, **kwargs):
    """Safely execute ML functions with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"ML processing error in {func.__name__}: {str(e)}")
        return None