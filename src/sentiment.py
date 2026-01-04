from transformers import pipeline

class SentimentAnalyzer:
    """
    A singleton class to load the FinBERT model once and reuse it.
    Industry Standard: Loading ML models is expensive (RAM/Time). 
    We load it in __init__ so we don't reload it for every single headline.
    """
    
    def __init__(self):
        print("Loading FinBERT model... (This may take a moment on first run)")
        # We use the 'pipeline' abstraction for clean code.
        # "ProsusAI/finbert" is the industry-standard open-source financial model.
        self.pipe = pipeline("text-classification", model="ProsusAI/finbert")

    def analyze(self, text):
        """
        Analyzes a single string of text.
        Returns: {'label': 'positive'/'negative'/'neutral', 'score': float}
        """
        try:
            # The model returns a list of dicts: [{'label': 'positive', 'score': 0.95}]
            result = self.pipe(text)[0]
            return result
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {'label': 'neutral', 'score': 0.0}

    def analyze_dataframe(self, df):
        """
        Takes a DataFrame containing a 'title' column and adds sentiment columns.
        """
        if df.empty:
            return df
        
        print(f"Analyzing {len(df)} headlines...")
        
        # Apply the model to every row. 
        # In a massive production system, we would batch this or use GPU acceleration.
        # For a few hundred headlines, a simple .apply() is fine.
        results = df['title'].apply(lambda x: self.analyze(x))
        
        # Split the result into two new columns
        df['sentiment_label'] = results.apply(lambda x: x['label'])
        df['sentiment_score'] = results.apply(lambda x: x['score'])
        
        return df

# --- TESTING BLOCK ---
if __name__ == "__main__":
    print("--- Starting AI Test ---")
    
    analyzer = SentimentAnalyzer()
    
    # Test Case 1: Good News
    text1 = "Apple reports record-breaking quarterly profits."
    print(f"\nText: {text1}")
    print(f"Result: {analyzer.analyze(text1)}")
    
    # Test Case 2: Bad News
    text2 = "Inflation concerns cause markets to plummet."
    print(f"\nText: {text2}")
    print(f"Result: {analyzer.analyze(text2)}")
    
    print("\n--- Test Complete ---")