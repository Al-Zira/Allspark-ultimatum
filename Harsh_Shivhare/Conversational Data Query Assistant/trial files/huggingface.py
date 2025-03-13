from sentence_transformers import SentenceTransformer

# Download model locally
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.save('.')