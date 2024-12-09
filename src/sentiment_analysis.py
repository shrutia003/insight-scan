import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE, RandomOverSampler
import nltk
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import subprocess
import re

subprocess.run(["python", "src/scrape_play_store.py"], check=True)

google_play_file = "google_play_reviews.csv"
google_play_df = pd.read_csv(google_play_file)

nltk.download("stopwords")
nltk.download("wordnet")
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    """Clean, tokenize, and lemmatize text."""
    if pd.isnull(text):
        return ""
    text = re.sub(r"[^\w\s]", "", text).lower()
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(tokens)

google_play_df["Cleaned_Review"] = google_play_df["Review"].apply(preprocess_text)

def assign_sentiment(rating):
    try:
        rating = float(rating)
        if rating <= 2:
            return "negative"
        elif rating == 3:
            return "neutral"
        elif rating >= 4:
            return "positive"
    except ValueError:
        return "neutral"

google_play_df["Sentiment"] = google_play_df["Rating"].apply(assign_sentiment)

X = google_play_df["Cleaned_Review"]
y = google_play_df["Sentiment"]
X = X[X != ""]
y = y[X.index]

print("Unique labels in y before split:", pd.Series(y).unique())
if pd.isnull(y).any():
    print("Removing None values from y...")
    valid_indices = [i for i, label in enumerate(y) if label is not None]
    X = X[valid_indices]
    y = [str(label) for label in y if label is not None]

print("Class distribution after cleaning:", Counter(y))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

tfidf = TfidfVectorizer(max_features=5000, min_df=2, max_df=0.8, ngram_range=(1, 2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

try:
    smote = SMOTE(k_neighbors=3, random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_train_tfidf, y_train)
except ValueError:
    oversampler = RandomOverSampler(random_state=42)
    X_resampled, y_resampled = oversampler.fit_resample(X_train_tfidf, y_train)

param_grid = {
    "C": [0.1, 1, 10],
    "solver": ["liblinear"],
    "class_weight": ["balanced", None],
}
lr = LogisticRegression(random_state=42)
grid = GridSearchCV(lr, param_grid, cv=5, scoring="accuracy")
grid.fit(X_resampled, y_resampled)

best_model = grid.best_estimator_
print(f"Best Model: {best_model}")

y_pred = best_model.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

with open("sentiment_analysis_evaluation.txt", "w") as file:
    file.write("Sentiment Analysis Model Evaluation\n")
    file.write("="*40 + "\n")
    file.write(f"Accuracy: {accuracy}\n\n")
    file.write("Classification Report:\n")
    file.write(classification_rep + "\n\n")
    file.write("Confusion Matrix:\n")
    file.write(str(conf_matrix) + "\n")
print("Evaluation metrics saved to sentiment_analysis_evaluation.txt")

google_play_df["Predicted_Sentiment"] = best_model.predict(tfidf.transform(google_play_df["Cleaned_Review"]))
google_play_df.to_csv("sentiment_analysis_improved_results.csv", index=False)
print("Improved sentiment analysis results saved!")
