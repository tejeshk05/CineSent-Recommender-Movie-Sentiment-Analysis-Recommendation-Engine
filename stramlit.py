import streamlit as st
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time

# Initialize the VADER sentiment analyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# Function to fetch movie details from OMDb API with error handling and retry
def get_movie_details(title, api_key):
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={title}'
    for _ in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            st.warning(f'Retrying due to error: {e}')
            time.sleep(2)  # Wait for 2 seconds before retrying
    return None

# Function to scrape IMDb reviews and ratings using BeautifulSoup
def scrape_imdb_reviews(imdb_id, max_reviews=50):
    url = f'https://www.imdb.com/title/{imdb_id}/reviews'
    for _ in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            reviews = soup.find_all('div', class_='text show-more__control')[:max_reviews]
            ratings = soup.find_all('span', class_='rating-other-user-rating')[:max_reviews]

            review_list = []
            for review, rating in zip(reviews, ratings):
                review_text = review.text.strip()
                rating_text = rating.find('span').text.strip()
                review_list.append({'review': review_text, 'rating': rating_text})

            return review_list
        except requests.exceptions.RequestException as e:
            st.warning(f'Retrying due to error: {e}')
            time.sleep(2)  # Wait for 2 seconds before retrying
    return None

# Function to perform sentiment analysis on reviews using VADER
def analyze_sentiment_vader(reviews):
    sentiment_scores = []
    for review in reviews:
        # Analyze sentiment for each review
        scores = sid.polarity_scores(review['review'])
        sentiment_scores.append((scores['compound'], review['rating']))  # Using compound score as overall sentiment
    return sentiment_scores

# Define a function to classify sentiment based on compound score
def classify_sentiment(score):
    if score > 0.2:
        return 'Positive'
    elif score >= -0.9 and score <= 0.1:
        return 'Negative'
    else:
        return 'Neutral'

# Define a function to recommend a movie based on sentiment scores and ratings
def recommend_movie(movie_title, sentiment_scores, ratings):
    average_sentiment_score = sum(score[0] for score in sentiment_scores) / len(sentiment_scores)
    average_rating = sum(int(rating) for rating in ratings) / len(ratings)

    if round(average_sentiment_score, 1) > 0.2 and average_rating >= 6.5:
        recommendation = f"<span style='color: green; font-size: 18px;'><b>🎬 I highly recommend '{movie_title}'!</b>" \
                          f" It has received positive reviews and high ratings ({round(average_rating, 1)}).</span>"
    elif round(average_sentiment_score, 1) >= -0.9 and round(average_sentiment_score, 1) <= 0.1 and average_rating <= 4:
        recommendation = f'<span style=\'color: red; font-size: 18px;\'><b>🎬 I do not recommend \'{movie_title}\'...</b>' \
                         f' It has received negative reviews and low ratings ({round(average_rating, 1)}).</span>'
    else:
        recommendation = f"<span style='color: orange; font-size: 18px;'><b>🎬 You may enjoy watching '{movie_title}'!</b>" \
                          f" It has received mixed reviews and ratings ({round(average_rating, 1)}).</span>"

    return recommendation

# Streamlit app
st.title('🎬 CineSent Recommender: Movie Sentiment Analysis & Recommendation Engine 🎥')

st.sidebar.header('Enter API Key')
api_key = st.sidebar.text_input('OMDb API Key:', type='password')

st.sidebar.markdown("""
    **How to get an OMDb API key:**
    1. Visit the [OMDb API Key](https://www.omdbapi.com/apikey.aspx?__EVENTTARGET=freeAcct&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%2FwEPDwUKLTIwNDY4MTIzNQ9kFgYCAQ9kFgICBw8WAh4HVmlzaWJsZWhkAgIPFgIfAGhkAgMPFgIfAGhkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYDBQtwYXRyZW9uQWNjdAUIZnJlZUFjY3QFCGZyZWVBY2N0oCxKYG7xaZwy2ktIrVmWGdWzxj%2FDhHQaAqqFYTiRTDE%3D&__VIEWSTATEGENERATOR=5E550F58&__EVENTVALIDATION=%2FwEdAAU%2BO86JjTqdg0yhuGR2tBukmSzhXfnlWWVdWIamVouVTzfZJuQDpLVS6HZFWq5fYpioiDjxFjSdCQfbG0SWduXFd8BcWGH1ot0k0SO7CfuulHLL4j%2B3qCcW3ReXhfb4KKsSs3zlQ%2B48KY6Qzm7wzZbR&at=freeAcct&Email=) page.
    2. Sign up with your email to get a free API key.
    3. Enter the API key in the sidebar.
""")

movie_title = st.text_input('Enter a movie title:')

if api_key and movie_title:
    with st.spinner('Fetching movie details...'):
        movie_details = get_movie_details(movie_title, api_key)

    if movie_details:
        imdb_id = movie_details.get('imdbID')
        if imdb_id:
            st.subheader('Movie Details')
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(movie_details.get('Poster', 'N/A'), width=230)  # Increase width for larger image
            with col2:
                st.markdown(f"""
                <b>Title:</b> {movie_details.get('Title', 'N/A')}<br>
                <b>Year:</b> {movie_details.get('Year', 'N/A')}<br>
                <b>Rated:</b> {movie_details.get('Rated', 'N/A')}<br>
                <b>Released:</b> {movie_details.get('Released', 'N/A')}<br>
                <b>Runtime:</b> {movie_details.get('Runtime', 'N/A')}<br>
                <b>Genre:</b> {movie_details.get('Genre', 'N/A')}<br>
                <b>Director:</b> {movie_details.get('Director', 'N/A')}<br>
                <b>Writer:</b> {movie_details.get('Writer', 'N/A')}<br>
                <b>Actors:</b> {movie_details.get('Actors', 'N/A')}<br>
                <b>Plot:</b> {movie_details.get('Plot', 'N/A')}<br>
                <b>Language:</b> {movie_details.get('Language', 'N/A')}<br>
                <b>Country:</b> {movie_details.get('Country', 'N/A')}<br>
                <b>Awards:</b> {movie_details.get('Awards', 'N/A')}
                """, unsafe_allow_html=True)

            with st.spinner('Scraping IMDb reviews...'):
                review_data = scrape_imdb_reviews(imdb_id)

            if review_data:
                sentiment_scores = analyze_sentiment_vader(review_data)
                ratings = [data['rating'] for data in review_data][:50]

                st.subheader('Summary & Recommendation')
                average_sentiment_score = sum(score[0] for score in sentiment_scores) / len(sentiment_scores)
                average_rating = sum(int(rating) for rating in ratings) / len(ratings)
                summary_sentiment = classify_sentiment(round(average_sentiment_score, 1))
                summary_color = 'green' if summary_sentiment == 'Positive' else 'red' if summary_sentiment == 'Negative' else 'orange'
                summary_text = f"""
                <div style="border: 2px solid {summary_color}; padding: 10px; margin-bottom: 10px;">
                    <h3>Overall Sentiment: <span style="color: {summary_color};">{summary_sentiment}</span></h3>
                    <p>{recommend_movie(movie_title, sentiment_scores, ratings)}</p>
                </div>
                """
                st.markdown(summary_text, unsafe_allow_html=True)

                st.subheader('Reviews')
                for i, (score, rating) in enumerate(sentiment_scores):
                    sentiment = classify_sentiment(score)
                    sentiment_color = 'green' if sentiment == 'Positive' else 'red' if sentiment == 'Negative' else 'orange'
                    st.markdown(f"""
                    <div style="border: 1px solid {sentiment_color}; padding: 10px; margin: 5px 0;">
                        <b>Review {i + 1}:</b> {review_data[i]["review"]}<br>
                        <b>Rating:</b> {'⭐' * int(rating)}<br>
                        <b>Sentiment:</b> <span style="color: {sentiment_color};">{sentiment} ({score})</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error('No reviews found')
        else:
            st.error('IMDb ID not found')
    else:
        st.error('No movie details found')
