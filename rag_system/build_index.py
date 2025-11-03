# ============================================================
# Imports
# ============================================================

import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from rank_bm25 import BM25Okapi
import pickle
import os
import time

# ============================================================
# Configuration Paths and Parameters
# ============================================================

PROCESSED_DATA_PATH = "data/processed/medsage_processed.csv"
VECTOR_STORE_PATH = "rag_system/vector_store"
BM25_INDEX_PATH = "rag_system/vector_store/bm25_index.pkl"
# Path to the local embedding model
LOCAL_EMBEDDING_MODEL = "./all-MiniLM-L6-v2"

# ============================================================
# Main Function: Build and Save Indexes
# ============================================================

def build_and_save_indices():
    """
    Reads processed data and creates both a FAISS vector index (GPU-based)
    and a BM25 keyword index, then saves them locally.
    """

    # Check if processed data exists
    if not os.path.exists(PROCESSED_DATA_PATH):
        print(f"Error: Processed data not found at {PROCESSED_DATA_PATH}")
        return

    # Load the processed CSV data containing questions and answers
    print("Loading processed data...")
    df = pd.read_csv(PROCESSED_DATA_PATH)

    # Remove entries with missing 'question' or 'answer'
    df.dropna(subset=['question', 'answer'], inplace=True)

    # Concatenate relevant fields into a single text for embedding/indexing
    df['text'] = (
        df['focus'].fillna('') + ". " +
        df['question'].fillna('') + " " +
        df['answer'].fillna('') + " " +
        df['semantic_types'].str.replace('|', ' ').fillna('') + " " +
        df['synonyms'].str.replace('|', ' ').fillna('')
    )
    texts = df['text'].tolist()
    print(f"Loaded {len(texts)} documents for indexing.")

    # Initialize local embedding model
    print(f"Initializing local embedding model: {LOCAL_EMBEDDING_MODEL}")
    embedding_model = HuggingFaceEmbeddings(model_name=LOCAL_EMBEDDING_MODEL)

    # Build FAISS index with GPU support
    print("Building FAISS index on GPU... This should be fast.")
    start_time = time.time()
    vector_store = FAISS.from_texts(texts, embedding_model)
    vector_store.save_local(VECTOR_STORE_PATH)
    end_time = time.time()
    print(f"FAISS index built and saved successfully in {end_time - start_time:.2f} seconds.")

    # Build BM25 index (keyword-based)
    print("Building BM25 index...")
    start_time = time.time()
    # Tokenize documents for BM25
    tokenized_corpus = [doc.split(" ") for doc in texts]
    bm25 = BM25Okapi(tokenized_corpus)
    # Save BM25 index and documents
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump({'bm25': bm25, 'docs': texts}, f)
    end_time = time.time()
    print(f"BM25 index built and saved successfully in {end_time - start_time:.2f} seconds.")


# Entry point execution check
if __name__ == "__main__":
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    build_and_save_indices()
