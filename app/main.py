import streamlit as st
import pandas as pd
import time
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()

# Import our modules
from sentiment import analyze_sentiment, get_model_info
from aspect_extractor import extract_aspects, get_aspect_categories, analyze_aspect_sentiment_context
from amazon_scraper import get_reviews_from_amazon, test_scraperapi_key, get_sample_reviews
from utils import colored_chip, format_time, display_ml_metrics, create_ml_export_data


def ensure_secrets():
    try:
        # Test if secrets are accessible
        test_key = st.secrets.get("SCRAPERAPI_KEY", "")
        if test_key:
            os.environ['SCRAPERAPI_KEY'] = test_key
    except:
        pass

ensure_secrets()
# Configure Streamlit with better defaults
st.set_page_config(
    page_title="ReviewLyser : Smart Review Aspect Analyser", 
    page_icon="🎯", 
    layout="wide",  # Changed to wide for better layout
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .status-good { color: #28a745; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    .status-error { color: #dc3545; font-weight: bold; }
    .human-insight {
        background: linear-gradient(135deg, #ffeaa7, #fab1a0);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #e17055;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background-color: #f0f2f6;
        border-radius: 10px;
        border: 2px solid transparent;
        color: #333;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
        border-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎯 ReviewLyser </h1>
    <p>AI-Powered Review Analysis & Amazon Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced status
with st.sidebar:
    st.markdown("### 🎛️ System Dashboard")
    
    # ML Model Status
    try:
        model_info = get_model_info()
        current_model = model_info['model_type']
        available = model_info['available_models']
        
        st.markdown("#### 🧠 AI Models")
        if current_model == "vader":
            st.markdown('<p class="status-good">✅ VADER ML Active</p>', unsafe_allow_html=True)
            st.caption("🎯 Optimized for review sentiment")
        elif current_model == "textblob":
            st.markdown('<p class="status-good">✅ TextBlob ML Active</p>', unsafe_allow_html=True)
            st.caption("🎯 Naive Bayes classifier")
        else:
            st.markdown('<p class="status-warning">⚡ Rule-based Active</p>', unsafe_allow_html=True)
            st.caption("📊 Algorithmic analysis")
        
        # Model availability
        with st.expander("🔍 Available Models"):
            for model_name, is_available in available.items():
                icon = "✅" if is_available else "❌"
                st.write(f"{icon} {model_name}")
                
    except Exception as e:
        st.markdown('<p class="status-error">❌ Model Error</p>', unsafe_allow_html=True)
        st.caption(str(e))
    
    st.divider()
    
    # ScraperAPI Status
    st.markdown("#### 🌐 Amazon Scraper")
    try:
        api_working, api_message = test_scraperapi_key()
        if api_working:
            st.markdown('<p class="status-good">✅ ScraperAPI Ready</p>', unsafe_allow_html=True)
            st.caption("🚀 Can scrape Amazon reviews")
        else:
            st.markdown('<p class="status-warning">⚠️ Using Demo Mode</p>', unsafe_allow_html=True)
            st.caption("📝 Sample reviews available")
            
        with st.expander("ℹ️ Scraper Details"):
            st.caption(api_message)
            
    except Exception as e:
        st.markdown('<p class="status-error">❌ Scraper Error</p>', unsafe_allow_html=True)
        st.caption(str(e))
    
    st.divider()
    
    # Quick actions
    st.markdown("#### ⚡ Quick Actions")
    if st.button("🧪 Demo with Sample Data", use_container_width=True):
        st.session_state['use_samples'] = True
    
    if st.button("📊 View Results", use_container_width=True):
        if st.session_state.get('all_results'):
            st.session_state['show_results'] = True
        else:
            st.warning("No results yet! Analyze some reviews first.")

# Initialize session state
if 'all_results' not in st.session_state:
    st.session_state.all_results = []

# Main content with tabs for better organization
tab1, tab2, tab3 = st.tabs(["Single Review Analysis", "Amazon Product Review Analyzer", "Results & Insights"])

with tab1:
    st.subheader("Analyze Individual Product Reviews")
    st.write("Perfect for testing specific reviews or analyzing competitor feedback")
    st.write("")  # Add some spacing
    
    # Review input with better UX
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_review = st.text_area(
            "Paste your product review here:",
            height=120,
            placeholder="Example: The build quality is amazing and delivery was super fast! However, the customer service could be better. Overall, great value for money.",
            value="The build quality is amazing and delivery was super fast! However, the customer service could be better. Overall, great value for money.",
            help="Try pasting reviews from Amazon, Flipkart, or any e-commerce site"
        )
    
    with col2:
        st.markdown("### Pro Tips")
        st.markdown("""
        - Include specific aspects (quality, price, delivery)
        - Mention both positives and negatives
        - Use natural language
        - Longer reviews = better analysis
        """)
        
        if st.button("Use Random Sample", use_container_width=True):
            sample_reviews = [
                "Excellent product quality and fast delivery! The design is beautiful and performance is outstanding. Definitely worth the money.",
                "Poor build quality for the price. Delivery was delayed and packaging was damaged. Customer service was unhelpful. Not recommended.",
                "Good value for money. Quality is decent, delivery was on time. Some features work well, others could be improved.",
                "Amazing purchase! Everything exceeded expectations - quality, design, performance. Fast shipping and great packaging. Highly recommend!"
            ]
            import random
            user_review = random.choice(sample_reviews)
            st.rerun()

    if user_review:
        with st.spinner("🤖 AI is analyzing your review..."):
            start_time = time.time()
            
            # Extract aspects and analyze sentiment
            aspects = extract_aspects(user_review)
            overall_sentiment = analyze_sentiment(user_review)
            processing_time = time.time() - start_time
        
        # Results with better visual layout
        st.markdown("### Analysis Results")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>⏱️ {processing_time:.2f}s</h4>
                <p>Processing Time</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🎯 {len(aspects)}</h4>
                <p>Aspects Found</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            sentiment_color = "#28a745" if overall_sentiment['label'] == 'POSITIVE' else "#dc3545" if overall_sentiment['label'] == 'NEGATIVE' else "#ffc107"
            st.markdown(f"""
            <div class="metric-card" style="background: {sentiment_color};">
                <h4>{overall_sentiment['label']}</h4>
                <p>Overall Sentiment</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{overall_sentiment.get('model_used', 'AI')}</h4>
                <p>AI Model Used</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Human-like insights
        st.markdown("### Human-Like Insights")
        
        # Generate human insights based on results
        if overall_sentiment['label'] == 'POSITIVE':
            if overall_sentiment['score'] > 0.8:
                insight = "🌟 **Highly Satisfied Customer!** This reviewer seems genuinely happy with their purchase."
            else:
                insight = "😊 **Generally Positive Experience** - Customer likes the product but may have minor concerns."
        elif overall_sentiment['label'] == 'NEGATIVE':
            if overall_sentiment['score'] > 0.8:
                insight = "😞 **Clearly Disappointed** - This customer had significant issues with the product."
            else:
                insight = "😐 **Mixed Experience** - Customer has some complaints but not entirely negative."
        else:
            insight = "🤔 **Neutral Opinion** - Customer seems undecided or has balanced views."
        
        st.markdown(f"""
        <div class="human-insight">
            {insight}
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed sentiment analysis
        if aspects:
            st.markdown("### Detailed Aspect Analysis")
            
            # Business insights
            categories = get_aspect_categories(aspects)
            if len(categories) > 1:
                st.markdown("**Business Categories Mentioned:**")
                for category, cat_aspects in categories.items():
                    st.markdown(f"- **{category}**: {', '.join(cat_aspects)}")
                st.markdown("---")
            
            # Aspect-wise analysis
            for aspect in aspects:
                context = analyze_aspect_sentiment_context(user_review, aspect)
                aspect_sentiment = analyze_sentiment(context)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    chip = colored_chip(aspect_sentiment['label'], aspect_sentiment['score'])
                    st.markdown(f"**{aspect.title()}**: {chip}", unsafe_allow_html=True)
                    
                    if context != user_review:
                        st.caption(f"💬 Context: \"{context[:100]}{'...' if len(context) > 100 else ''}\"")
                
                with col2:
                    # Human-readable confidence
                    conf = aspect_sentiment['confidence']
                    if conf == 'high':
                        st.caption("🎯 Very Confident")
                    elif conf == 'medium':
                        st.caption("📊 Moderately Confident")
                    else:
                        st.caption("❓ Less Confident")
                
                # Store results
                st.session_state.all_results.append({
                    "Source": "Manual Input",
                    "Review": user_review,
                    "Aspect": aspect,
                    "Context": context,
                    "Sentiment": aspect_sentiment['label'],
                    "Score": aspect_sentiment['score'],
                    "Confidence": aspect_sentiment['confidence'],
                    "ML_Model": aspect_sentiment.get('model_used', 'Unknown')
                })
        else:
            st.info("💡 **Tip**: Try a review that mentions specific product features (quality, price, delivery, etc.) for better aspect analysis!")

with tab2:
    st.subheader("Amazon Review Scraper & Bulk Analyzer")
    st.write("Scrape real Amazon reviews and get instant business insights")
    st.write("")  # Add some spacing
    
    # URL input with examples
    col1, col2 = st.columns([2, 1])
    
    with col1:
        amazon_url = st.text_input(
            "Enter Amazon Product URL:",
            placeholder="https://www.amazon.in/dp/PRODUCT_ID",
            help="Paste any Amazon product URL - we'll automatically find the reviews"
        )
        
        # URL examples
        with st.expander("Example URLs (Click to use)"):
            example_urls = [
                "https://www.amazon.in/dp/B08N5WRWNW",
                "https://www.amazon.in/dp/B07HGJJ586",
                "https://www.amazon.in/dp/B0CRTW5Y79"
            ]
            for url in example_urls:
                if st.button(f"{url}", key=f"url_{url[-10:]}"):
                    amazon_url = url
                    st.rerun()
    
    with col2:
        st.markdown("### Quick Actions")
        use_samples = st.button("Demo with Sample Reviews", use_container_width=True)
        
        st.markdown("### Settings")
        max_reviews = st.slider("Max Reviews to Scrape", 3, 10, 5)
        
        st.markdown("### What You'll Get")
        st.markdown("""
        - Real customer reviews
        - Aspect-based analysis  
        - Sentiment breakdown
        - Business insights
        - Downloadable report
        """)

    # Process Amazon reviews
    if use_samples or st.session_state.get('use_samples', False):
        st.success("🧪 **Demo Mode**: Using sample Amazon reviews")
        reviews = get_sample_reviews()[:max_reviews]
        st.session_state['use_samples'] = False
        
    elif amazon_url:
        if not amazon_url.startswith('http'):
            st.error("❌ Please provide a complete URL starting with http:// or https://")
            reviews = []
        elif 'amazon' not in amazon_url.lower():
            st.error("❌ Please provide a valid Amazon URL")
            reviews = []
        else:
            with st.spinner("🕷️ Scraping Amazon reviews... This magic takes a moment!"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🔍 Finding product reviews...")
                    progress_bar.progress(33)
                    
                    reviews = get_reviews_from_amazon(amazon_url, max_reviews=max_reviews)
                    progress_bar.progress(100)
                    
                    if reviews and len(reviews) == 1 and 'Error:' in reviews[0]:
                        st.error(f"🚫 Scraping Issue: {reviews[0]}")
                        st.info("💡 **Don't worry!** Click 'Demo with Sample Reviews' to see how it works")
                        reviews = []
                        
                    status_text.empty()
                    progress_bar.empty()
                    
                except Exception as e:
                    st.error(f"🚫 Oops! Scraping failed: {str(e)}")
                    st.info("💡 **No problem!** Use the demo mode to see all features")
                    reviews = []
                    status_text.empty()
                    progress_bar.empty()
    else:
        reviews = []

    # Process and display results
    if reviews:
        st.success(f"🎉 **Success!** Found {len(reviews)} reviews to analyze")
        
        # Human insights for bulk analysis
        st.markdown("### Quick Business Insights")
        
        # Quick sentiment preview
        quick_sentiments = []
        for review in reviews[:3]:  # Quick analysis of first 3
            sentiment = analyze_sentiment(review)
            quick_sentiments.append(sentiment['label'])
        
        positive_count = quick_sentiments.count('POSITIVE')
        negative_count = quick_sentiments.count('NEGATIVE')
        
        if positive_count > negative_count:
            business_insight = f"🟢 **Looking Good!** {positive_count}/{len(quick_sentiments)} samples are positive. Customers seem happy!"
        elif negative_count > positive_count:
            business_insight = f"🟠 **Needs Attention!** {negative_count}/{len(quick_sentiments)} samples are negative. Check common complaints."
        else:
            business_insight = f"🟡 **Mixed Feedback** - Balanced opinions. Great opportunity for improvement!"
        
        st.markdown(f"""
        <div class="human-insight">
            {business_insight}
        </div>
        """, unsafe_allow_html=True)
        
        # Process each review
        all_review_results = []
        
        for i, review in enumerate(reviews, 1):
            with st.expander(f"📖 Review #{i} ({len(review)} characters)", expanded=i <= 2):
                st.markdown("**📝 Customer Says:**")
                st.write(f'"{review}"')
                
                # Analyze review
                review_aspects = extract_aspects(review)
                overall = analyze_sentiment(review)
                
                # Show results
                col1, col2 = st.columns([2, 1])
                with col1:
                    chip = colored_chip(overall['label'], overall['score'])
                    st.markdown(f"**Overall Feeling**: {chip}", unsafe_allow_html=True)
                with col2:
                    st.caption(f"🤖 Analyzed by {overall.get('model_used', 'AI')}")
                
                if review_aspects:
                    st.markdown(f"**🏷️ What they talked about**: {', '.join([f'`{a}`' for a in review_aspects])}")
                    
                    # Detailed aspect analysis
                    for aspect in review_aspects:
                        context = analyze_aspect_sentiment_context(review, aspect)
                        aspect_sentiment = analyze_sentiment(context)
                        aspect_chip = colored_chip(aspect_sentiment['label'], aspect_sentiment['score'])
                        
                        st.markdown(f"└─ **{aspect.title()}**: {aspect_chip}", unsafe_allow_html=True)
                        
                        # Store results
                        all_review_results.append({
                            "Source": f"Amazon Review #{i}",
                            "Review": review,
                            "Aspect": aspect,
                            "Context": context[:100] + "..." if len(context) > 100 else context,
                            "Sentiment": aspect_sentiment['label'],
                            "Score": aspect_sentiment['score'],
                            "Confidence": aspect_sentiment['confidence'],
                            "ML_Model": aspect_sentiment.get('model_used', 'Unknown')
                        })
                else:
                    st.info("💭 This review doesn't mention specific product features")
        
        # Add to session state
        st.session_state.all_results.extend(all_review_results)

with tab3:
    if st.session_state.all_results:
        st.subheader("Complete Analysis Results & Business Insights")
        st.write("Your analyzed data with actionable business intelligence")
        st.write("")  # Add some spacing
        
        df = pd.DataFrame(st.session_state.all_results)
        
        # Enhanced dashboard
        display_ml_metrics(st.session_state.all_results)
        
        # Business insights section
        st.markdown("### Business Intelligence")
        
        sentiment_counts = df['Sentiment'].value_counts()
        total = len(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Customer Satisfaction")
            positive_pct = (sentiment_counts.get('POSITIVE', 0) / total) * 100
            negative_pct = (sentiment_counts.get('NEGATIVE', 0) / total) * 100
            
            if positive_pct > 60:
                satisfaction_insight = f"🟢 **Strong Performance** ({positive_pct:.1f}% positive)"
            elif positive_pct > 40:
                satisfaction_insight = f"🟡 **Mixed Results** ({positive_pct:.1f}% positive)"
            else:
                satisfaction_insight = f"🔴 **Needs Improvement** ({positive_pct:.1f}% positive)"
            
            st.markdown(satisfaction_insight)
            st.bar_chart(sentiment_counts)
        
        with col2:
            st.markdown("#### Top Issues & Strengths")
            
            # Find most mentioned aspects
            if 'Aspect' in df.columns:
                top_aspects = df['Aspect'].value_counts().head(5)
                st.markdown("**Most Discussed Features:**")
                for aspect, count in top_aspects.items():
                    percentage = (count / total) * 100
                    st.write(f"• **{aspect.title()}**: {count} mentions ({percentage:.1f}%)")
        
        # Detailed results
        st.markdown("### Detailed Results")
        
        # Enhanced table
        if 'ML_Model' in df.columns:
            display_df = df[['Source', 'Aspect', 'Sentiment', 'Score', 'Confidence', 'ML_Model']].copy()
        else:
            display_df = df[['Source', 'Aspect', 'Sentiment', 'Score', 'Confidence']].copy()
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Export section
        st.markdown("### Export Your Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            export_df = create_ml_export_data(st.session_state.all_results, include_metadata=True)
            csv = export_df.to_csv(index=False)
            st.download_button(
                "Download Full Report (CSV)",
                csv,
                "product_review_analysis_report.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col2:
            # Summary report
            summary_data = {
                'Total_Reviews': [len(df['Review'].unique()) if 'Review' in df.columns else 0],
                'Total_Aspects': [len(df)],
                'Positive_Sentiment': [sentiment_counts.get('POSITIVE', 0)],
                'Negative_Sentiment': [sentiment_counts.get('NEGATIVE', 0)],
                'Analysis_Date': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')]
            }
            summary_csv = pd.DataFrame(summary_data).to_csv(index=False)
            st.download_button(
                "Download Summary Report",
                summary_csv,
                "analysis_summary.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col3:
            if st.button("Clear All Results", use_container_width=True):
                st.session_state.all_results = []
                st.success("✅ Results cleared!")
                st.rerun()
    
    else:
        st.subheader("No Results Yet")
        st.write("Start analyzing reviews to see your results here!")
        st.write("")
        
        st.write("**To get started:**")
        st.write("• Use the **Single Review** tab to analyze individual reviews")
        st.write("• Use the **Amazon Scraper** tab to analyze bulk reviews")
        st.write("• Click **'Demo with Sample Reviews'** for instant results")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
    <strong>AI-Powered Review Analyzer</strong> | Developed with ❤️ by <strong>Divyansh Jain</strong><br>
    <em>Transforming customer feedback into actionable business insights</em>
</div>
""", unsafe_allow_html=True)