# insight-scan
Steps to run the project and generate sentiment analysis data - 

- Be sure to have an updated python version. (3.8 or later)

- Clone this repository.

- Run the following commands in your terminal.
    - Install the required dependencies. 
        - pip install -r requirements.txt
    - Run the sentiment analysis script.
        - python src\sentiment_analysis.py
        - Enter the app you want to search for reviews. Examples - Chess, Duolingo, LinkedIn, Spotify, etc.

**Generated Outputs**
- CSV file with web-scraped user reviews for the user-specified application.
- CSV file containing sentiment analysis results, which can be used by developers to filter out good and bad reviews.
- .txt file with detailed evaluation metrics for the sentiment analysis model, such as accuracy, precision, recall, and F1-score.