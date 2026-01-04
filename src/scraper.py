import yfinance as yf
import pandas as pd
from datetime import datetime

class FinancialExtractor:
    """
    A dedicated class for extracting financial data.
    """
    
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol.upper()
        self.ticker = yf.Ticker(self.ticker_symbol)

    def get_stock_history(self, period="1mo"):
        """
        Fetches historical stock data.
        """
        try:
            df = self.ticker.history(period=period, auto_adjust=True)
            df = df.reset_index()
            df['Date'] = df['Date'].dt.date
            return df[['Date', 'Close', 'Volume']]
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return pd.DataFrame()

    def _extract_item_data(self, item):
        """
        Internal Helper: Handles both 'Flat' and 'Nested' API responses.
        """
        title = None
        link = None
        publisher = 'Unknown'
        published = datetime.now().timestamp()

        # --- STRATEGY 1: Check if data is nested inside 'content' (Your Case) ---
        if 'content' in item:
            content = item['content']
            title = content.get('title')
            
            # Links are often buried deep in the new format
            click_through = content.get('clickThroughUrl')
            if click_through:
                link = click_through.get('url')
            
            # Sometimes the provider is inside content
            provider = content.get('provider')
            if provider:
                publisher = provider.get('displayName', 'Unknown')
                
            # Try to find a date
            published = content.get('pubDate', published)

        # --- STRATEGY 2: Check if data is at the top level (Old Case) ---
        if not title:
            title = item.get('title')
            
        if not link:
            link = item.get('link')
            if not link:
                link = item.get('url')

        return title, link, publisher, published

    def get_news(self):
        """
        Fetches the latest news using the robust parser.
        """
        try:
            news_list = self.ticker.news
            
            # --- DEBUGGING PRINT ---
            if len(news_list) > 0:
                print(f"DEBUG: Processing {len(news_list)} articles...")
                # If we still fail, this will tell us what is inside 'content'
                if 'content' in news_list[0]:
                    print(f"DEBUG: 'content' keys: {news_list[0]['content'].keys()}")
            # -----------------------

            cleaned_news = []
            
            for item in news_list:
                title, link, publisher, published = self._extract_item_data(item)
                
                # Only add if we successfully found a title
                if title:
                    cleaned_news.append({
                        'title': title,
                        'publisher': publisher,
                        'link': link or 'No Link Found', # Handle missing links gracefully
                        'published': published
                    })
            
            return pd.DataFrame(cleaned_news)
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return pd.DataFrame()

# --- TESTING BLOCK ---
if __name__ == "__main__":
    extractor = FinancialExtractor("AAPL")
    df = extractor.get_news()
    print("\n--- RESULT ---")
    if not df.empty:
        print(df[['title', 'link']].head())
    else:
        print("Still returned empty DataFrame.")