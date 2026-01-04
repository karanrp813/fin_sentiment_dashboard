# 📈 Modern Quant: AI-Powered Stock Sentiment Dashboard

## 🚀 Project Overview
**Modern Quant** is a financial intelligence tool that correlates real-time market news with stock performance. Unlike traditional dashboards that only show price history, this application uses **Deep Learning (BERT)** to analyze the *sentiment* of financial news, helping users visualize the psychological factors driving market movements.

## 🏗️ Architecture & Tech Stack
This project follows a **Microservices-inspired architecture** with a clear separation between Data Ingestion, Intelligence, and Presentation layers.

* **Frontend:** Streamlit (Interactive Data Visualization)
* **Backend Logic:** Python 3.9+
* **AI Model:** Hugging Face Transformers (`ProsusAI/finbert`) for Financial NLP.
* **Data Pipeline:** * **yfinance API** for real-time OHLCV market data.
    * **Custom Scraper** with error handling for scraping Yahoo Finance news headers.
* **Visualization:** Plotly (Interactive Charts & Donut Graphs).

## ⚡ Key Features
* **Real-Time Data Ingestion:** Fetches live stock data and news headlines instantly.
* **Sentiment Classification:** Uses `FinBERT` (a BERT model fine-tuned on financial text) to classify headlines as Positive, Negative, or Neutral with high confidence.
* **Drift-Resistant Scraping:** Includes a robust parsing engine capable of handling schema drift in the Yahoo Finance API.
* **Visual Analytics:** Overlays sentiment distribution against 3-month price history.

## 🛠️ Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/modern-quant.git](https://github.com/YOUR_USERNAME/modern-quant.git)
    cd fin_sentiment_dashboard
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application**
    ```bash
    streamlit run src/dashboard.py
    ```

## 📊 Future Roadmap
* **Database Integration:** Migrate from in-memory processing to PostgreSQL for historical sentiment tracking.
* **Dockerization:** Containerize the application for cloud deployment (AWS/Azure).
* **CI/CD:** Implement GitHub Actions for automated testing of the scraper logic.
