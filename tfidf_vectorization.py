
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer

# Load the cleaned dataset
df = pd.read_csv("data/processed/jobs_cleaned.csv")

# Select job descriptions
descriptions = df["description"].fillna("")

# Create TF-IDF vectorizer
tfidf = TfidfVectorizer(
    max_features=1000,
    stop_words="english"
)

# Convert job descriptions into numerical features
tfidf_matrix = tfidf.fit_transform(descriptions)

# Display matrix shape
print("\nTF-IDF MATRIX SHAPE:")
print(tfidf_matrix.shape)

# Display total vocabulary size
print("\nTOTAL VOCABULARY WORDS:")
print(len(tfidf.get_feature_names_out()))

# Display first 10 vocabulary words
print("\nFIRST 10 VOCABULARY WORDS:")
print(tfidf.get_feature_names_out()[:10])

# Display first job's TF-IDF values
print("\nFIRST JOB TF-IDF VALUES:")
print(tfidf_matrix[0].toarray()[0][:10])

# Display non-zero TF-IDF features for the first job
print("\nNON-ZERO TF-IDF VALUES:")

feature_names = tfidf.get_feature_names_out()

first_job = tfidf_matrix[0].toarray()[0]

for index, value in enumerate(first_job):

    if value > 0:
        print(feature_names[index], ":", round(value, 4))