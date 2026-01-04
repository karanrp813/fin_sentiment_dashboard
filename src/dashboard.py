import streamlit as st
import plotly.graph_objects as go
from scraper import FinancialExtractor
from sentiment import SentimentAnalyzer
from database import init_db, save_results, get_recent_sentiment

# --- PAGE CONFIG ---
st.set_page_config(page_title="FinBERT Sentiment Dashboard", layout="wide")
init_db()
# --- LOAD AI MODEL (Cached) ---
@st.cache_resource
def load_ai_model():
    """
    Load the heavy AI model only once.
    This prevents the app from crashing/slowing down on every interaction.
    """
    return SentimentAnalyzer()

analyzer = load_ai_model()

# --- SIDEBAR ---
st.sidebar.title("Configuration")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL")
st.sidebar.info("Supported: US Stocks (AAPL, TSLA, NVDA, etc.)")

# --- MAIN APP ---
st.title(f"📈 {ticker} Market Sentiment Analysis")

if st.button("Run Analysis"):
    # 1. Initialize Extractor
    extractor = FinancialExtractor(ticker)
    
    # 2. Fetch Data (Parallelizable in future versions)
    with st.spinner('Fetching market data and news...'):
        stock_df = extractor.get_stock_history(period="3mo")
        news_df = extractor.get_news()

    # --- SECTION 1: MARKET DATA ---
    st.subheader("Market Performance (3 Months)")
    
    if not stock_df.empty:
        # Create an interactive Plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=stock_df['Date'], 
            y=stock_df['Close'], 
            mode='lines', 
            name='Close Price',
            line=dict(color='#00CC96')
        ))
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Could not fetch stock data. Check the ticker symbol.")

    # --- SECTION 2: AI NEWS ANALYSIS ---
    st.subheader("AI-Powered News Sentiment")
    
    if not news_df.empty:
        with st.spinner('Running FinBERT Model on headlines...'):
            analyzed_df = analyzer.analyze_dataframe(news_df)
        
        # Calculate Stats
        sentiment_counts = analyzed_df['sentiment_label'].value_counts()
        # --- DATABASE SAVE ---
        new_count = save_results(ticker, analyzed_df)
        if new_count > 0:
            st.success(f"✅ Saved {new_count} new articles to the database.")
        else:
            st.info("ℹ️ No new articles to save (all duplicates).")
        # ---------------------
        total_articles = len(analyzed_df)
        pos_count = sentiment_counts.get('positive', 0)
        neg_count = sentiment_counts.get('negative', 0)
        neu_count = sentiment_counts.get('neutral', 0)

        # --- LAYOUT: Metrics on Left, Chart on Right ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Total Articles", total_articles)
            st.metric("Positive 🟢", pos_count)
            st.metric("Negative 🔴", neg_count)
            st.metric("Neutral ⚪", neu_count)
        
        with col2:
            # Create a Donut Chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Positive', 'Negative', 'Neutral'],
                values=[pos_count, neg_count, neu_count],
                hole=.5, # Makes it a Donut
                marker_colors=['#00CC96', '#EF553B', '#636EFA'] # Green, Red, Blue
            )])
            fig_pie.update_layout(
                title_text="Sentiment Distribution",
                height=300,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Show the actual data table below
        st.markdown("### Latest Headlines")
        st.dataframe(
            analyzed_df[['title', 'published', 'sentiment_label', 'sentiment_score']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No recent news found for this ticker.")
        st.divider()
        st.subheader("🗄️ Database History (All Time)")
        history_df = get_recent_sentiment(ticker)
        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True)
        else:
            st.write("No history found in database yet.")
else:
    st.write("👈 Enter a ticker in the sidebar and click 'Run Analysis'")