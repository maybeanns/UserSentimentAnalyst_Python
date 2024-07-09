import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

def analyze_user_sentiment(product_link):
    try:
        response = requests.get(product_link)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching the product link: {e}"

    soup = BeautifulSoup(response.content, 'html.parser')

    star_rating_element = soup.find('span', class_='a-icon-alt')
    if not star_rating_element:
        return None, "No star rating found."
    try:
        star_rating = float(star_rating_element.text.split()[0])
    except ValueError:
        return None, "Error parsing star rating."

    reviews = []
    review_elements = soup.find_all('span', {'data-hook': 'review-body'})
    for review_element in review_elements:
        reviews.append(review_element.text.strip())

    if not reviews:
        return None, "No reviews found."

    sentiment_scores = [TextBlob(review).sentiment.polarity for review in reviews]
    if not sentiment_scores:
        return None, "No sentiment scores calculated."

    happy_count = sum(1 for score in sentiment_scores if score > 0.2)
    dissatisfied_count = sum(1 for score in sentiment_scores if score < -0.2)
    neutral_count = len(sentiment_scores) - happy_count - dissatisfied_count

    total_reviews = len(sentiment_scores)
    happy_percentage = (happy_count / total_reviews) * 100
    dissatisfied_percentage = (dissatisfied_count / total_reviews) * 100
    neutral_percentage = (neutral_count / total_reviews) * 100

    return {
        'star_rating': star_rating,
        'happy_percentage': happy_percentage,
        'dissatisfied_percentage': dissatisfied_percentage,
        'neutral_percentage': neutral_percentage
    }, None

st.title('Product Sentiment Analysis')
st.header('Enter the Amazon Product Link')

product_link = st.text_input('Product Link')

if st.button('Analyze'):
    if product_link:
        result, error = analyze_user_sentiment(product_link)
        if error:
            st.error(error)
        else:
            st.success('Analysis Complete!')
            st.subheader(f"Star Rating: ⭐ {result['star_rating']}/5")
            st.write(f"😊 Happy: **{result['happy_percentage']:.2f}%**")
            st.write(f"😡 Dissatisfied: **{result['dissatisfied_percentage']:.2f}%**")
            st.write(f"😐 Neutral: **{result['neutral_percentage']:.2f}%**")
    else:
        st.error('Please enter a product link.')
