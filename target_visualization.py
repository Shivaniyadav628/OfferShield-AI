import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data/raw/fake_job_postings.csv")

# Count genuine and fraudulent jobs
target_counts = df["fraudulent"].value_counts()

# Create a bar chart
plt.figure(figsize=(8, 5))

target_counts.plot(
    kind="bar",
    color=["green", "red"]
)

# Add graph labels
plt.title("Genuine vs Fraudulent Job Postings")
plt.xlabel("Job Category")
plt.ylabel("Number of Job Postings")

# Change category names
plt.xticks(
    [0, 1],
    ["Genuine Jobs", "Fraudulent Jobs"],
    rotation=0
)

# Display the graph
plt.show()