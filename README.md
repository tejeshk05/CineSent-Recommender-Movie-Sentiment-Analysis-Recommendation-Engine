# CineSent Recommender: Movie Sentiment Analysis & Recommendation Engine 🎥

CineSent is a Streamlit web application designed to analyze movie sentiment based on IMDb reviews and provide recommendations. It utilizes the OMDb API for movie details and BeautifulSoup for web scraping IMDb reviews. Sentiment analysis is performed using the VADER (Valence Aware Dictionary and sEntiment Reasoner) from NLTK.

## Deployment
- The project is deployed and can be accessed at [deployed link](https://cinesent-movie-recommender.streamlit.app/).

## Features

- **Movie Details Display**: Fetches and displays movie details such as title, year, director, plot, ratings, and more using the OMDb API.
  
- **IMDb Reviews Scraping**: Scrapes up to 50 user reviews from IMDb for the specified movie title.
  
- **Sentiment Analysis**: Uses VADER to analyze sentiment from each review and categorizes it into positive, negative, or neutral/mixed.
  
- **Recommendation Engine**: Based on average sentiment scores and IMDb ratings, provides a recommendation whether to watch the movie, with reasons provided.

## Getting Started

To run this application locally, follow these steps:

### Prerequisites

- Python 3.6+
- Pip (Python package installer)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/CineSent-Recommender-Movie-Sentiment-Analysis-Recommendation-Engine.git
   cd CineSent-Recommender
   ```
2. Install dependencies:

   ```bash
    pip install -r requirements.txt

   ```
2. Run the Streamlit app:

   ```bash
    streamlit run app.py

   ```
4. Open your web browser and go to http://localhost:8501.

## Screenshots & Videos
![Screenshot 2024-06-14 200439](https://github.com/tejeshk05/CineSent-Recommender-Movie-Sentiment-Analysis-Recommendation-Engine/assets/166478758/6712ec7f-ec16-4161-8907-872f52b5d451)
![Screenshot 2024-06-14 200539](https://github.com/tejeshk05/CineSent-Recommender-Movie-Sentiment-Analysis-Recommendation-Engine/assets/166478758/8bee5221-2f00-45f2-825e-db07c8ee05f4)
![Screenshot 2024-06-14 200601](https://github.com/tejeshk05/CineSent-Recommender-Movie-Sentiment-Analysis-Recommendation-Engine/assets/166478758/af34a0b5-3f69-43a7-a9be-42e876310761)

https://github.com/tejeshk05/CineSent-Recommender-Movie-Sentiment-Analysis-Recommendation-Engine/assets/166478758/2ce40d58-293d-4dbe-9bcf-f1600c0b67d1

## Requirements
- Python 3.6+
- Streamlit
- requests
- BeautifulSoup4
- nltk

## How to Use

1. **Get an OMDb API Key:**
   - Visit the [OMDb API Key page](https://www.omdbapi.com/apikey.aspx).
   - Sign up with your email to get a free API key.
   - Enter the API key in the sidebar of the application.

   ![OMDb API Key](https://github.com/tejeshk05/CineSent-Recommender-Movie-Sentiment-Analysis-Recommendation-Engine/assets/166478758/692d9a35-d482-4f69-9534-1efeb5a3a81d)


2. **Enter a Movie Title:**
   - Type the title of the movie you want to analyze into the designated input field.

3. **View the Results:**
   - The application will display detailed movie information fetched from OMDb.
   - It will scrape IMDb reviews and perform sentiment analysis using VADER.
   - Based on the sentiment scores and ratings, the app will provide a personalized movie recommendation.

## Built With
- Streamlit - The web framework used
- OMDb API - Open Movie Database API
- Beautiful Soup - HTML parsing library
- NLTK - Natural Language Toolkit for sentiment analysis

## Authors
- Your Name - D.Tejesh Kumar

## Contact
- For any questions or suggestions, please open an issue or contact the repository owner at dtejesh05k@gmail.com.
 
   
