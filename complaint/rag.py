import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(BASE_DIR, 'faiss_index')

INDEX_PATH = os.path.join(INDEX_DIR, 'index.faiss')
CHUNKS_PATH = os.path.join(INDEX_DIR, 'chunks.pkl')

embedding_model = None
retriever = None

def get_embedding_model():
    global embedding_model

    if embedding_model is None:
        print('Loading embedding model...')
        embedding_model = SentenceTransformer(
            'sentence-transformers/all-MiniLM-L6-v2'
        )
    return embedding_model

class RAGRetriever:
    def __init__(self):
        self.index = None
        self.chunks = []
        self.load()

    def load(self):
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(CHUNKS_PATH, 'rb') as f:
                self.chunks = pickle.load(f)

    def search(self, query, k=3):
        if self.index is None:
            return []
        
        embedding_model=get_embedding_model()
        vector = embedding_model.encode([query])
        _, indices = self.index.search(vector, k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.chunks):
                results.append(self.chunks[idx])

        return results

def get_retriever():
    global retriever

    if retriever is None:
        retriever = RAGRetriever()

    return retriever