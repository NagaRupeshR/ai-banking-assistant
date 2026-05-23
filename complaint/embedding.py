from sentence_transformers import SentenceTransformer

embedding_model = None

def get_embedding_model():
    global embedding_model

    if embedding_model is None:
        print('Loading embedding model...')
        embedding_model = SentenceTransformer(
            'sentence-transformers/all-MiniLM-L6-v2'
        )
    return embedding_model