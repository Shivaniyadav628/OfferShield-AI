
import pandas as pd
from scipy.sparse import save_npz

# Import the preprocessing objects and data
from preprocessing import (
    X_train_processed,
    X_test_processed,
    y_train,
    y_test
)

# Save processed feature matrices
save_npz(
    "data/processed/X_train_processed.npz",
    X_train_processed
)

save_npz(
    "data/processed/X_test_processed.npz",
    X_test_processed
)

# Save target variables
y_train.to_csv(
    "data/processed/y_train.csv",
    index=False
)

y_test.to_csv(
    "data/processed/y_test.csv",
    index=False
)

print("PROCESSED DATA SAVED SUCCESSFULLY!")
