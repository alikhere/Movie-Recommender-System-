# compress.py
import gzip
import pickle

# Load the original similarity matrix
with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

# Save it in a compressed format
with gzip.open('similarity.pkl.gz', 'wb') as f:
    pickle.dump(similarity, f)
