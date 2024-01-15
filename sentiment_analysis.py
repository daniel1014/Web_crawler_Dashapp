from textblob import TextBlob
import json

def analyze_sentiment(tweet):
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

def sentiment_analysis(company_focus_data):
    result = {}

    for company_focus, tweets in company_focus_data.items():
        sentiment_count = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for tweet_data in tweets:
            for tweet_text, tweet_content in tweet_data.items():
                sentiment = analyze_sentiment(tweet_content)
                sentiment_count[sentiment] += 1
        
        result[company_focus] = sentiment_count
    
    return result

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

    # Output the result in JSON format
    json_result = json.dumps(result, indent=2)
    print(json_result)