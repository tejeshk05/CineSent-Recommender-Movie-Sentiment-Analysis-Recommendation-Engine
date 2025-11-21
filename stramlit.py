import streamlit as st
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time
import pandas as pd
import plotly.express as px
from collections import Counter
import json
import re

# Configure page
st.set_page_config(
    page_title="CineSent Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the VADER sentiment analyzer
try:
    nltk.download('vader_lexicon', quiet=True)
except:
    pass
sid = SentimentIntensityAnalyzer()

# Function to fetch movie details from OMDb API with error handling and retry
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_movie_details(title, api_key):
    """Fetch movie details from OMDb API with retry mechanism"""
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={title}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Response') == 'False':
                return None
            return data
        except requests.exceptions.Timeout:
            if attempt < 2:
                st.warning(f'Request timeout. Retrying... ({attempt + 1}/3)')
                time.sleep(2)
            else:
                st.error('Request timeout after multiple attempts')
        except requests.exceptions.RequestException as e:
            if attempt < 2:
                st.warning(f'Error: {e}. Retrying... ({attempt + 1}/3)')
                time.sleep(2)
            else:
                st.error(f'Failed to fetch movie details: {e}')
    return None

# Function to scrape IMDb reviews and ratings using BeautifulSoup
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def scrape_imdb_reviews(imdb_id, max_reviews=50):
    """Scrape IMDb reviews with improved error handling and multiple selector strategies"""
    url = f'https://www.imdb.com/title/{imdb_id}/reviews'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            review_list = []
            
            # Strategy 1: Find review containers (lister-item)
            review_containers = soup.find_all('div', class_='lister-item')
            
            if review_containers:
                for container in review_containers[:max_reviews]:
                    # Find review text - try multiple selectors
                    review_text = None
                    review_selectors = [
                        ('div', {'class': 'text show-more__control'}),
                        ('div', {'class': 'content'}),
                        ('div', {'class': 'text'}),
                        ('div', {'class': 'review-container'}),
                        ('p', {'class': 'text'}),
                    ]
                    
                    for tag, attrs in review_selectors:
                        review_elem = container.find(tag, attrs)
                        if review_elem:
                            review_text = review_elem.get_text(strip=True)
                            if review_text and len(review_text) > 20:  # Ensure meaningful content
                                break
                    
                    if not review_text:
                        # Try to find any text content in the container
                        text_divs = container.find_all('div', class_=lambda x: x and 'text' in x.lower())
                        for div in text_divs:
                            text = div.get_text(strip=True)
                            if text and len(text) > 20:
                                review_text = text
                                break
                    
                    if not review_text or len(review_text) < 20:
                        continue
                    
                    # Find rating - try multiple selectors
                    rating = 'N/A'
                    rating_selectors = [
                        ('span', {'class': 'rating-other-user-rating'}),
                        ('span', {'class': 'ipl-rating-star__rating'}),
                        ('span', {'class': 'rating'}),
                        ('div', {'class': 'ipl-rating-star'}),
                    ]
                    
                    for tag, attrs in rating_selectors:
                        rating_elem = container.find(tag, attrs)
                        if rating_elem:
                            # Try to find the actual rating number
                            rating_span = rating_elem.find('span')
                            if rating_span:
                                rating_text = rating_span.get_text(strip=True)
                            else:
                                rating_text = rating_elem.get_text(strip=True)
                            
                            # Extract numeric rating
                            rating_match = re.search(r'(\d+)', rating_text)
                            if rating_match:
                                rating = rating_match.group(1)
                                break
                    
                    review_list.append({
                        'review': review_text,
                        'rating': rating
                    })
            
            # Strategy 2: If no containers found, try direct selectors
            if not review_list:
                # Try finding reviews directly
                review_elements = soup.find_all('div', class_='text show-more__control')
                if not review_elements:
                    review_elements = soup.find_all('div', class_='content')
                if not review_elements:
                    review_elements = soup.find_all('div', class_=lambda x: x and 'text' in str(x).lower())
                
                # Find ratings separately
                rating_elements = soup.find_all('span', class_='rating-other-user-rating')
                if not rating_elements:
                    rating_elements = soup.find_all('span', class_='ipl-rating-star__rating')
                if not rating_elements:
                    rating_elements = soup.find_all('span', class_=lambda x: x and 'rating' in str(x).lower())
                
                for i, review_elem in enumerate(review_elements[:max_reviews]):
                    review_text = review_elem.get_text(strip=True)
                    if not review_text or len(review_text) < 20:
                        continue
                    
                    rating = 'N/A'
                    if i < len(rating_elements):
                        try:
                            rating_text = rating_elements[i].get_text(strip=True)
                            rating_match = re.search(r'(\d+)', rating_text)
                            if rating_match:
                                rating = rating_match.group(1)
                        except:
                            pass
                    
                    review_list.append({
                        'review': review_text,
                        'rating': rating
                    })
            
            # Strategy 3: Try finding by data attributes or IDs
            if not review_list:
                # Look for any divs with review-like content
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text(strip=True)
                    # Check if it looks like a review (has reasonable length and sentence structure)
                    if text and 50 < len(text) < 5000 and '.' in text:
                        # Check if it's not already in our list
                        if not any(text[:50] in r['review'][:50] for r in review_list):
                            review_list.append({
                                'review': text,
                                'rating': 'N/A'
                            })
                            if len(review_list) >= max_reviews:
                                break
            
            if review_list:
                return review_list[:max_reviews]
            else:
                # Debug: Save HTML for inspection (optional, can be removed)
                return None
            
        except requests.exceptions.Timeout:
            if attempt < 2:
                st.warning(f'Request timeout. Retrying... ({attempt + 1}/3)')
                time.sleep(2)
            else:
                st.error('Request timeout after multiple attempts')
        except requests.exceptions.RequestException as e:
            if attempt < 2:
                st.warning(f'Error: {e}. Retrying... ({attempt + 1}/3)')
                time.sleep(2)
            else:
                st.error(f'Failed to scrape reviews: {e}')
        except Exception as e:
            if attempt < 2:
                st.warning(f'Unexpected error: {e}. Retrying... ({attempt + 1}/3)')
                time.sleep(2)
            else:
                st.error(f'Unexpected error during scraping: {e}')
    return None

# Function to perform sentiment analysis on reviews using VADER
@st.cache_data
def analyze_sentiment_vader(reviews):
    """Perform sentiment analysis on reviews with detailed scores"""
    sentiment_scores = []
    for review in reviews:
        scores = sid.polarity_scores(review['review'])
        sentiment_scores.append({
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'rating': review['rating'],
            'review': review['review']
        })
    return sentiment_scores

# Define a function to classify sentiment based on compound score
def classify_sentiment(score):
    """Classify sentiment based on compound score"""
    if score > 0.05:
        return 'Positive'
    elif score < -0.05:
        return 'Negative'
    else:
        return 'Neutral'

# Define a function to recommend a movie based on sentiment scores and ratings
def recommend_movie(movie_title, sentiment_scores, ratings):
    """Generate movie recommendation based on sentiment and ratings"""
    # Filter out N/A ratings
    valid_ratings = [int(r) for r in ratings if r != 'N/A' and r.isdigit()]
    average_sentiment_score = sum(score['compound'] for score in sentiment_scores) / len(sentiment_scores)
    average_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0
    
    # Count sentiment distribution
    positive_count = sum(1 for s in sentiment_scores if s['compound'] > 0.05)
    negative_count = sum(1 for s in sentiment_scores if s['compound'] < -0.05)
    neutral_count = len(sentiment_scores) - positive_count - negative_count
    
    if average_sentiment_score > 0.1 and average_rating >= 7.0:
        recommendation = f"<span style='color: green; font-size: 18px;'><b>🎬 I highly recommend '{movie_title}'!</b>" \
                          f" It has received overwhelmingly positive reviews ({positive_count}/{len(sentiment_scores)}) " \
                          f"and high ratings ({round(average_rating, 1)}/10).</span>"
    elif average_sentiment_score < -0.1 and average_rating <= 4.0:
        recommendation = f'<span style=\'color: red; font-size: 18px;\'><b>🎬 I do not recommend \'{movie_title}\'...</b>' \
                         f' It has received mostly negative reviews ({negative_count}/{len(sentiment_scores)}) ' \
                         f'and low ratings ({round(average_rating, 1)}/10).</span>'
    else:
        recommendation = f"<span style='color: orange; font-size: 18px;'><b>🎬 You may enjoy watching '{movie_title}'!</b>" \
                          f" It has received mixed reviews (Positive: {positive_count}, Negative: {negative_count}, Neutral: {neutral_count}) " \
                          f"and ratings ({round(average_rating, 1)}/10).</span>"

    return recommendation, average_sentiment_score, average_rating, positive_count, negative_count, neutral_count

# Streamlit app
st.title('🎬 CineSent Recommender: Movie Sentiment Analysis & Recommendation Engine 🎥')
st.markdown("---")

# Sidebar Configuration
st.sidebar.header('⚙️ Configuration')

# API Key Input
api_key = st.sidebar.text_input('OMDb API Key:', type='password', help='Enter your OMDb API key to fetch movie details')

# Configuration Options
st.sidebar.subheader('📊 Analysis Settings')
max_reviews = st.sidebar.slider('Number of Reviews to Analyze', min_value=10, max_value=100, value=50, step=10)

st.sidebar.markdown("""
    **How to get an OMDb API key:**
    1. Visit the [OMDb API](https://www.omdbapi.com/apikey.aspx) page.
    2. Sign up with your email to get a free API key.
    3. Enter the API key in the sidebar.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 About")
st.sidebar.info("""
    **CineSent Recommender** analyzes movie reviews from IMDb using 
    Natural Language Processing (NLP) and provides intelligent 
    recommendations based on sentiment analysis.
""")

# Main Content
col1, col2 = st.columns([3, 1])
with col1:
    movie_title = st.text_input('🎥 Enter a movie title:', placeholder='e.g., The Matrix, Inception, Interstellar')
with col2:
    st.write("")
    st.write("")
    analyze_button = st.button('🔍 Analyze', type='primary', use_container_width=True)

# Process when button is clicked or movie title is entered
if (analyze_button or movie_title) and api_key and movie_title:
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Fetch movie details
    status_text.text('📡 Fetching movie details from OMDb API...')
    progress_bar.progress(20)
    movie_details = get_movie_details(movie_title, api_key)

    if movie_details and movie_details.get('Response') != 'False':
        imdb_id = movie_details.get('imdbID')
        if imdb_id:
            # Display Movie Details
            st.markdown("## 🎬 Movie Details")
            col1, col2 = st.columns([1, 2])
            with col1:
                poster_url = movie_details.get('Poster', 'N/A')
                if poster_url and poster_url != 'N/A':
                    st.image(poster_url, width=300)
                else:
                    st.info("Poster not available")
            
            with col2:
                st.markdown(f"""
                <div style="padding: 10px;">
                    <h2>{movie_details.get('Title', 'N/A')} ({movie_details.get('Year', 'N/A')})</h2>
                    <p><b>⭐ IMDb Rating:</b> {movie_details.get('imdbRating', 'N/A')}/10 ({movie_details.get('imdbVotes', 'N/A')} votes)</p>
                    <p><b>📅 Released:</b> {movie_details.get('Released', 'N/A')}</p>
                    <p><b>⏱️ Runtime:</b> {movie_details.get('Runtime', 'N/A')}</p>
                    <p><b>🎭 Genre:</b> {movie_details.get('Genre', 'N/A')}</p>
                    <p><b>🎬 Director:</b> {movie_details.get('Director', 'N/A')}</p>
                    <p><b>✍️ Writer:</b> {movie_details.get('Writer', 'N/A')}</p>
                    <p><b>👥 Actors:</b> {movie_details.get('Actors', 'N/A')}</p>
                    <p><b>📖 Plot:</b> {movie_details.get('Plot', 'N/A')}</p>
                    <p><b>🏆 Awards:</b> {movie_details.get('Awards', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

            # Step 2: Scrape reviews
            status_text.text('🕷️ Scraping IMDb reviews...')
            progress_bar.progress(40)
            review_data = scrape_imdb_reviews(imdb_id, max_reviews)

            if review_data and len(review_data) > 0:
                # Step 3: Analyze sentiment
                status_text.text('🧠 Analyzing sentiment...')
                progress_bar.progress(60)
                sentiment_scores = analyze_sentiment_vader(review_data)
                
                # Filter valid ratings
                valid_ratings = [int(s['rating']) for s in sentiment_scores if s['rating'] != 'N/A' and str(s['rating']).isdigit()]
                
                # Step 4: Generate recommendation
                status_text.text('💡 Generating recommendation...')
                progress_bar.progress(80)
                
                recommendation, avg_sentiment, avg_rating, pos_count, neg_count, neu_count = recommend_movie(
                    movie_details.get('Title', movie_title), 
                    sentiment_scores, 
                    [s['rating'] for s in sentiment_scores]
                )
                
                progress_bar.progress(100)
                status_text.text('✅ Analysis complete!')
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()

                # Summary & Recommendation Section
                st.markdown("## 📊 Sentiment Analysis Summary")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Overall Sentiment", classify_sentiment(avg_sentiment), 
                             f"{avg_sentiment:.3f}")
                with col2:
                    st.metric("Average Rating", f"{avg_rating:.1f}/10" if avg_rating > 0 else "N/A")
                with col3:
                    st.metric("Positive Reviews", pos_count, f"{pos_count/len(sentiment_scores)*100:.1f}%")
                with col4:
                    st.metric("Negative Reviews", neg_count, f"{neg_count/len(sentiment_scores)*100:.1f}%")
                
                # Recommendation Box
                summary_sentiment = classify_sentiment(avg_sentiment)
                summary_color = 'green' if summary_sentiment == 'Positive' else 'red' if summary_sentiment == 'Negative' else 'orange'
                st.markdown(f"""
                <div style="border: 3px solid {summary_color}; border-radius: 10px; padding: 20px; margin: 20px 0; background-color: rgba(0,0,0,0.05);">
                    <h3 style="color: {summary_color}; margin-top: 0;">Overall Sentiment: {summary_sentiment}</h3>
                    <p style="font-size: 16px;">{recommendation}</p>
                </div>
                """, unsafe_allow_html=True)

                # Data Visualization
                st.markdown("## 📈 Visualizations")
                
                # Sentiment Distribution Pie Chart
                fig_pie = px.pie(
                    values=[pos_count, neg_count, neu_count],
                    names=['Positive', 'Negative', 'Neutral'],
                    title='Sentiment Distribution',
                    color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#f39c12'}
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                
                # Sentiment Scores Distribution
                sentiment_values = [s['compound'] for s in sentiment_scores]
                fig_hist = px.histogram(
                    x=sentiment_values,
                    nbins=20,
                    title='Sentiment Score Distribution',
                    labels={'x': 'Sentiment Score', 'y': 'Number of Reviews'},
                    color_discrete_sequence=['#3498db']
                )
                fig_hist.add_vline(x=avg_sentiment, line_dash="dash", line_color="red", 
                                 annotation_text=f"Average: {avg_sentiment:.3f}")
                
                # Ratings Distribution (if available)
                if valid_ratings:
                    rating_counts = Counter(valid_ratings)
                    fig_ratings = px.bar(
                        x=list(rating_counts.keys()),
                        y=list(rating_counts.values()),
                        title='Rating Distribution',
                        labels={'x': 'Rating (out of 10)', 'y': 'Number of Reviews'},
                        color=list(rating_counts.values()),
                        color_continuous_scale='Viridis'
                    )
                
                # Display charts in columns
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    st.plotly_chart(fig_pie, use_container_width=True)
                with chart_col2:
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                if valid_ratings:
                    st.plotly_chart(fig_ratings, use_container_width=True)

                # Detailed Reviews Section
                st.markdown("## 📝 Detailed Reviews Analysis")
                
                # Filter options
                filter_col1, filter_col2 = st.columns(2)
                with filter_col1:
                    sentiment_filter = st.selectbox('Filter by Sentiment', ['All', 'Positive', 'Negative', 'Neutral'])
                with filter_col2:
                    sort_option = st.selectbox('Sort by', ['Default', 'Most Positive', 'Most Negative', 'Highest Rating', 'Lowest Rating'])
                
                # Filter and sort reviews
                filtered_scores = sentiment_scores.copy()
                if sentiment_filter != 'All':
                    filtered_scores = [s for s in filtered_scores if classify_sentiment(s['compound']) == sentiment_filter]
                
                if sort_option == 'Most Positive':
                    filtered_scores.sort(key=lambda x: x['compound'], reverse=True)
                elif sort_option == 'Most Negative':
                    filtered_scores.sort(key=lambda x: x['compound'])
                elif sort_option == 'Highest Rating':
                    filtered_scores.sort(key=lambda x: int(x['rating']) if x['rating'] != 'N/A' and str(x['rating']).isdigit() else 0, reverse=True)
                elif sort_option == 'Lowest Rating':
                    filtered_scores.sort(key=lambda x: int(x['rating']) if x['rating'] != 'N/A' and str(x['rating']).isdigit() else 10)
                
                # Display filtered reviews
                for i, score_data in enumerate(filtered_scores[:20]):  # Show top 20
                    sentiment = classify_sentiment(score_data['compound'])
                    sentiment_color = 'green' if sentiment == 'Positive' else 'red' if sentiment == 'Negative' else 'orange'
                    
                    rating_display = score_data['rating']
                    if rating_display != 'N/A' and str(rating_display).isdigit():
                        stars = '⭐' * int(rating_display)
                        rating_display = f"{stars} ({rating_display}/10)"
                    
                    st.markdown(f"""
                    <div style="border-left: 4px solid {sentiment_color}; padding: 15px; margin: 10px 0; background-color: rgba(0,0,0,0.02); border-radius: 5px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <strong style="color: {sentiment_color};">{sentiment}</strong>
                            <span><b>Rating:</b> {rating_display}</span>
                        </div>
                        <p style="margin: 0;">{score_data['review'][:500]}{'...' if len(score_data['review']) > 500 else ''}</p>
                        <div style="margin-top: 10px; font-size: 12px; color: #666;">
                            <span>Compound: {score_data['compound']:.3f}</span> | 
                            <span>Positive: {score_data['positive']:.3f}</span> | 
                            <span>Negative: {score_data['negative']:.3f}</span> | 
                            <span>Neutral: {score_data['neutral']:.3f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export functionality
                st.markdown("## 💾 Export Results")
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    # Export as CSV
                    df = pd.DataFrame([
                        {
                            'Review': s['review'],
                            'Rating': s['rating'],
                            'Sentiment': classify_sentiment(s['compound']),
                            'Compound Score': s['compound'],
                            'Positive': s['positive'],
                            'Negative': s['negative'],
                            'Neutral': s['neutral']
                        }
                        for s in sentiment_scores
                    ])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"{movie_details.get('Title', 'movie')}_sentiment_analysis.csv",
                        mime="text/csv"
                    )
                
                with export_col2:
                    # Export as JSON
                    export_data = {
                        'movie': movie_details.get('Title'),
                        'analysis_date': pd.Timestamp.now().isoformat(),
                        'summary': {
                            'average_sentiment': avg_sentiment,
                            'average_rating': avg_rating,
                            'positive_count': pos_count,
                            'negative_count': neg_count,
                            'neutral_count': neu_count,
                            'total_reviews': len(sentiment_scores)
                        },
                        'reviews': sentiment_scores
                    }
                    json_str = json.dumps(export_data, indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"{movie_details.get('Title', 'movie')}_sentiment_analysis.json",
                        mime="application/json"
                    )
                
            else:
                st.error('❌ No reviews found. The movie might not have enough reviews on IMDb.')
        else:
            st.error('❌ IMDb ID not found. Please check the movie title and try again.')
    else:
        if movie_details and movie_details.get('Response') == 'False':
            st.error(f"❌ Movie not found: {movie_details.get('Error', 'Unknown error')}")
        else:
            st.error('❌ Failed to fetch movie details. Please check your API key and internet connection.')
else:
    if not api_key:
        st.info("👈 Please enter your OMDb API key in the sidebar to get started.")
    elif not movie_title:
        st.info("👆 Enter a movie title above and click 'Analyze' to begin sentiment analysis.")
