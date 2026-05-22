import os
import pickle
import faiss
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, 'documents')  # Directory holding all PDFs
INDEX_DIR = os.path.join(BASE_DIR, 'faiss_index')

os.makedirs(INDEX_DIR, exist_ok=True)

INDEX_PATH = os.path.join(INDEX_DIR, 'index.faiss')
CHUNKS_PATH = os.path.join(INDEX_DIR, 'chunks.pkl')


def extract_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:  # Avoid adding None values
                text += page_text + '\n'
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""


def chunk_text(text, chunk_size=1000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def main():
    all_chunks = []

    # Check if directory exists
    if not os.path.exists(DOCS_DIR):
        print(f"Directory not found: {DOCS_DIR}")
        return

    # Loop through all files in the documents directory
    for file_name in os.listdir(DOCS_DIR):
        if file_name.lower().endswith('.pdf'):
            pdf_path = os.path.join(DOCS_DIR, file_name)
            print(f"Processing: {file_name}")
            
            text = extract_text(pdf_path)
            chunks = chunk_text(text)
            all_chunks.extend(chunks)  # Combine chunks into one main list

    if not all_chunks:
        print("No text chunks found. Indexing aborted.")
        return

    print(f"Total chunks extracted: {len(all_chunks)}")
    print("Generating embeddings...")

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(all_chunks)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)

    with open(CHUNKS_PATH, 'wb') as f:
        pickle.dump(all_chunks, f)

    print('FAISS index created successfully for all documents.')


if __name__ == '__main__':
    main()
