from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(text):
    """Get embeddings for text"""
    if isinstance(text, str):
        return model.encode(text)
    elif isinstance(text, list):
        return model.encode(text)
    else:
        return None

def calculate_similarity(text1, text2):
    """Calculate cosine similarity between two texts"""
    emb1 = get_embeddings(text1)
    emb2 = get_embeddings(text2)
    
    if emb1 is not None and emb2 is not None:
        # Calculate cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)
    return 0.0 