from textblob import TextBlob
from textblob.np_extractors import ConllExtractor
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from wordcloud import WordCloud
import time


def analyze_sentiment(tweet):
    """ Analyze the sentiment of each tweet, return 'positive', 'neutral' or 'negative'"""
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

def sentiment_analysis(news_output):
    """ Analyze the sentiment of each tweet, return a dictionary of the sentiment count for each company focus"""
    sentiment_result = {}

    for company_focus, all_news in news_output.items():
        sentiment_count = {'positive': 0, 'neutral': 0, 'negative': 0}
        for news in all_news:
            for title, description in news.items():
                sentiment = analyze_sentiment(title+description)
                sentiment_count[sentiment] += 1   
        sentiment_result[company_focus] = sentiment_count
    
    return sentiment_result

def analyze_topics(tweet):
    """ Extract the topics of each tweet, return a list of topics"""
    analysis=TextBlob(tweet, np_extractor=ConllExtractor())
    return analysis.noun_phrases

def topics_analysis(news_output):
    """ Analyze the topics of each tweet, return a dictionary of the topics for each company focus"""
    topics_result = {}

    for company_focus, all_news in news_output.items():
        # Use list comprehension to improve readability and performance
        topics = [topic for news in all_news for title, description in news.items() for topic in analyze_topics(title + description)]
        topics_result[company_focus] = topics
    return topics_result

def update_wordcloud(i, topics_result, tab):  
    """ Generate the word cloud for each topic"""  
    # Generate a word cloud from the topic's content
    wordcloud = WordCloud(collocations=False, background_color="white").generate(' '.join(topics_result[tab]))
    
    # Clear the current axes and display the new word cloud
    plt.gca().clear()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

def create_wordcloud_animation(topics_result, tab):
    """ Create a word cloud animation for each topic, return the filename of the animation"""
    fig = plt.figure(figsize=(9, 6))
    fig.patch.set_facecolor('#C4C4C4')  # Set the outside background color 
    ani = animation.FuncAnimation(fig, update_wordcloud, fargs=(topics_result, tab), frames=3, interval=1500, blit=False)

    # Save the animation
    filename = f'assets/wordcloud_{tab}_{time.time()}.gif'
    ani.save(filename, writer='pillow', fps=1)
    return filename

# Local Test 
if __name__ == "__main__":
    company_focus_data = {
        'Enercon Supply Chain': [
            {"Enercon to receive € 500 million as aid from German govt": "The turbine manufacturer claimed that it suffered a breakdown or supply chain/logistics problems caused by restrictions due to the COVID-19"},
            {"'We're all in trouble' | Wind turbine makers selling at a loss and in a ...": "... Enercon tell WindEurope 2022. ... “It is really ridiculous to think how we can sustain a supply chain in a growing industry with these kind of"},
            # ... (other tweets)
        ],
        'Anglian Water Incident Rate': [
            {"\"We're sorry\": Anglian Water accepts responsibility in national ...": "Anglian Water has joined a national apology from water companies for the alarming rate of sewage dumps and spills – after nearly 4,000 were"},
            # ... (other tweets)
        ],
        'Apple User Experience': [
            {"UX rant: The nightmare horrorshow that is the Apple TV remote | Ars ...": "Thankfully, though, this interaction travesty provides some good insight into what makes or breaks the user experience. The “all things to"},
            # ... (other tweets)
        ]
    }

    result = sentiment_analysis(company_focus_data)

    for tab, topics_result in result.items():
        filename = create_wordcloud_animation(topics_result, tab)
        print(f"Word cloud animation saved as {filename}")