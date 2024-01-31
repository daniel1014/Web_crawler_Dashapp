# Web_crawler_Dashapp
Available at: https://web-crawler-dashapp.azurewebsites.net/

To get started for testing/ playing around,  please visit the website and explore the "login" function. You'll initially see a pre-input row (Supplier: Enercon, Focus: Supply Chain) on top of the Input Table. Create a new username (or load the demo input with username "AECOM" or "Test"), input your interested field to search about, and utilise the "Add Input" and "Delete Selected Row" buttons to add or remove rows by selecting the clickbox. Next, you can experiment the main functions by clicking the button "Search", "Sentiment Analysis", and "Topic Extraction"! 🚀

This Dash application, named "News Scraper Tool", is a web application designed to scrape news from the Google Search Engine API (free tier). It's built using Python's Dash framework and integrates with AECOM database (Microsoft SQL) for data storage and retrieval. Here are its main features:

1. User Authentication: Users can enter their username and load their data by clicking the 'Login (load your data)' button. The status of the login operation is displayed in an alert box. You can save back your input and output data into AECOM database at the end along with your unique username. 

2. Data Input: Users can input data into a table, specifying the 'Supplier', 'Focus', and 'Number of Search'. They can add new rows to the table or delete selected rows. The data in the table can be uploaded to the AECOM database by clicking the 'Upload to AECOM Database' button.

3. News Scraping: By clicking the 'Search' button, the application will scrape news related to the 'Supplier' and 'Focus' specified in the input table. The number of search results is determined by the 'Number of Search' field. The search results include the news title, date, description, and URL.

4. Data Output: The search results are displayed in a table on the page. The table supports pagination and displays 10 results per page. The 'URL' column in the table is clickable, allowing users to directly access the news articles.

5. Sentiment Analysis: By clicking the "Sentiment Analysis" button, the application will analyze sentiment of the searched news article (news description), classify whether if it is "positive", "neutral" or "negative" based on the sentiment polarity, and populate the count of sentiment type in a horizontal bar chart. 

6. Topic Extraction: By clicking the "Topic Analysis" button, the application will use the TextBlob library with the ConllExtractor to extract noun phrases, which are used as the topics of news. Then it will generate the word cloud image and transform it into animated word cloud graphic (GIF) for the chosen topics. By clicking different tab underneath, it will populate the corresponding animated wordcloud graphic.  

7. Data Download: Users can download the search results as an Excel or CSV file. They can select the file type from a dropdown menu and click the 'Download Result' button to download the file.

Technical details: 
1. To avoid being blocked as against the terms of service of both Azure/Google, it utilized an official Google programmable search engine V1 with a unique API key and search engine ID for the purpose of customized web scrapping (Free-tier with limit of 10,000 queries per day)
 
2. It's important to note that the Azure web app operates on the Free F1 plan with the lowest scale of CPU and memory. Consequently, there is a loading time of approximately 1-2 minutes during the initial launch. However, once activated, the application operates smoothly.

![image](https://github.com/daniel1014/Web_crawler_Dashapp/assets/11716270/7239deac-0ce0-4c19-b022-7c9688469fcc)

![Dash and 22 more pages - Work - Microsoft_ Edge 2024-01-29 10-08-12](https://github.com/daniel1014/Web_crawler_Dashapp/assets/11716270/633a2492-9fc5-498f-9293-eadf60fbedf9)

