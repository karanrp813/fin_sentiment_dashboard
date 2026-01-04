from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import pandas as pd

# 1. Setup SQLite Database
DATABASE_URL = "sqlite:///sentiment.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Define the Table Model
class SentimentRecord(Base):
    __tablename__ = "news_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    title = Column(String)
    publisher = Column(String)
    link = Column(String, unique=True, index=True)
    published_date = Column(DateTime)
    sentiment_label = Column(String)
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# 3. Create Tables
def init_db():
    Base.metadata.create_all(bind=engine)

# 4. Data Operations (DEBUG VERSION)
def save_results(ticker, df):
    session = SessionLocal()
    count = 0
    try:
        print(f"\n--- DATABASE DEBUG: Attempting to save {len(df)} rows for {ticker} ---")
        
        # Get existing links
        existing_links_query = session.query(SentimentRecord.link).filter(SentimentRecord.ticker == ticker).all()
        existing_links = {r[0] for r in existing_links_query}
        print(f"DEBUG: Found {len(existing_links)} existing links in DB.")
        
        for index, row in df.iterrows():
            link = row['link']
            
            if link in existing_links:
                print(f"DEBUG: Skipping duplicate: {link[:30]}...")
                continue

            # Robust Date Handling
            raw_date = row.get('published')
            final_date = datetime.now() # Default fallback
            
            try:
                if isinstance(raw_date, (int, float)):
                    final_date = datetime.fromtimestamp(raw_date)
                elif isinstance(raw_date, str):
                    # Try to parse string, or just use current time if it fails
                    final_date = datetime.now() 
            except Exception as e:
                print(f"DEBUG: Date conversion failed, using Now. Error: {e}")

            record = SentimentRecord(
                ticker=ticker,
                title=row['title'],
                publisher=row.get('publisher', 'Unknown'),
                link=link,
                published_date=final_date,
                sentiment_label=row['sentiment_label'],
                sentiment_score=float(row['sentiment_score'])
            )
            session.add(record)
            count += 1
            print(f"DEBUG: Staged for save: {row['title'][:30]}...")

        print(f"DEBUG: Committing {count} new records to DB...")
        session.commit()
        print("DEBUG: Commit successful!")
        return count

    except Exception as e:
        print(f"CRITICAL DATABASE ERROR: {e}")
        session.rollback()
        return 0
    finally:
        session.close()

def get_recent_sentiment(ticker, limit=50):
    session = SessionLocal()
    try:
        records = session.query(SentimentRecord).filter(
            SentimentRecord.ticker == ticker
        ).order_by(SentimentRecord.published_date.desc()).limit(limit).all()
        
        data = [{
            "Date": r.published_date, 
            "Headline": r.title, 
            "Sentiment": r.sentiment_label,
            "Score": r.sentiment_score
        } for r in records]
        
        return pd.DataFrame(data)
    finally:
        session.close()