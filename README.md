## CineSent Recommender: Movie Sentiment Analysis & Recommendation Engine 🎥

CineSent is a Streamlit web application that analyzes IMDb movie reviews, performs sentiment analysis, and generates intelligent watch recommendations.  
It uses the OMDb API for movie metadata, BeautifulSoup for scraping IMDb reviews, and VADER (from NLTK) for sentiment scoring.

## 🚀 Deployment
- [Click here to open the Movie Recommender App](https://cinesent-movie-recommender.streamlit.app/)

## ✨ Key Features

- **Rich movie details**
  - Fetches title, year, genre, runtime, plot, cast, IMDb rating, votes, awards, etc. from OMDb.

- **IMDb reviews scraping**
  - Scrapes up to a configurable number of user reviews for a given movie from IMDb.
  - Uses multiple HTML selector strategies to handle IMDb layout changes.

- **Advanced sentiment analysis**
  - Uses NLTK VADER to compute compound, positive, negative, and neutral sentiment scores.
  - Classifies each review as Positive, Negative, or Neutral.

- **Recommendation engine**
  - Combines average sentiment score and user ratings to recommend:
    - Highly recommended
    - Not recommended
    - Mixed / may enjoy
  - Shows counts of positive/negative/neutral reviews.

- **Interactive data visualizations**
  - Sentiment distribution pie chart.
  - Sentiment score histogram with average line.
  - Rating distribution bar chart (when ratings are available).

- **User-friendly UI & UX**
  - Modern Streamlit layout with sidebar configuration.
  - Progress bar and status messages for each analysis step.
  - Filter and sort reviews by sentiment, rating, or score.

- **Exportable insights**
  - Download full analysis as CSV.
  - Download structured JSON with summary + all reviews and scores.

## 🧰 Tech Stack

- **Frontend / App**: Streamlit  
- **Backend / Logic**: Python  
- **APIs**: OMDb API, IMDb (scraping)  
- **Libraries**:
  - `requests`, `beautifulsoup4`
  - `nltk` (VADER sentiment)
  - `pandas`, `plotly`

## 🛠 Getting Started (Local)

### Prerequisites

- Python 3.8+  
- Pip (Python package manager)

### 1. Clone the repository

```bash
git clone https://github.com/tejeshk05/CineSent-Recommender-Movie-Sentiment-Analysis-Recommendation-Engine.git
cd "CineSent Recommender"
```

### 2. Create & activate a virtual environment (optional but recommended)

```bash
python -m venv venv

# PowerShell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit app

```bash
streamlit run stramlit.py
```

Then open your browser at `http://localhost:8501` if it doesn’t open automatically.

## 📌 How to Use

1. **Get an OMDb API key**
   - Visit the OMDb API key page: `https://www.omdbapi.com/apikey.aspx`
   - Sign up with your email to get a free API key.
   - Enter the key in the sidebar under **OMDb API Key**.

2. **Configure analysis**
   - Choose how many IMDb reviews to analyze (slider in the sidebar).

3. **Enter a movie title**
   - Type a movie name (e.g., “Inception”, “The Matrix”, “Interstellar”) in the input box.
   - Click **Analyze**.

4. **Explore results**
   - View movie details (poster, plot, cast, ratings, etc.).
   - Review the sentiment summary and recommendation.
   - Inspect charts for sentiment and rating distributions.
   - Scroll through individual reviews with sentiment labels and scores.
   - Export results as CSV or JSON.

## 📦 Requirements (summary)

Main Python dependencies (see `requirements.txt` for exact versions):
- `streamlit`
- `requests`
- `beautifulsoup4`
- `nltk`
- `pandas`
- `plotly`

## 👤 Author

- **Name**: D. Tejesh Kumar  
- **GitHub**: `https://github.com/tejeshk05`

## 📬 Contact

- For questions, issues, or suggestions, please open a GitHub issue  
  or email: `dtejesh05k@gmail.com`
