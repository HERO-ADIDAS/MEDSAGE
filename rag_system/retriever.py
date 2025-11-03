# ============================================================
# Imports
# ============================================================

import pickle
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
import numpy as np
from collections import defaultdict  # Used for Reciprocal Rank Fusion (RRF) scoring


# ============================================================
# Configuration Constants
# ============================================================

VECTOR_STORE_PATH = "rag_system/vector_store"
BM25_INDEX_PATH = "rag_system/vector_store/bm25_index.pkl"
LOCAL_EMBEDDING_MODEL = "./all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
RRF_K = 60  # Constant used in Reciprocal Rank Fusion scoring, typical value


# ============================================================
# Advanced Retriever Class implementing Hybrid Search
# ============================================================

class AdvancedRetriever:
    def __init__(self):
        """
        Initialize the retriever by loading all necessary models and indexes:
        - Local embedding model for FAISS vectors
        - FAISS vector store
        - BM25 index and associated documents
        - Cross-encoder model for re-ranking
        """
        print("Loading local retriever components...")

        # Load embedding model for vector representations
        self.embedding_model = HuggingFaceEmbeddings(model_name=LOCAL_EMBEDDING_MODEL)

        # Load local FAISS vector store with embeddings
        self.vector_store = FAISS.load_local(
            VECTOR_STORE_PATH,
            self.embedding_model,
            allow_dangerous_deserialization=True
        )

        # Load BM25 index and documents from pickle file
        with open(BM25_INDEX_PATH, "rb") as f:
            bm25_data = pickle.load(f)
            self.bm25 = bm25_data['bm25']
            self.bm25_docs = bm25_data['docs']  # List of document texts for BM25

        # Load Cross-Encoder model for semantic re-ranking
        self.cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)

        print("Retriever loaded successfully.")

    def search(self, query: str, k_retrieve: int = 50, k_rerank: int = 25, k_final: int = 5) -> str:
        """
        Perform a hybrid semantic and keyword search with Reciprocal Rank Fusion (RRF),
        followed by re-ranking using a Cross-Encoder, and return top-k final documents as context.

        Args:
            query (str): The input query string.
            k_retrieve (int): Number of documents to fetch initially from each search method.
            k_rerank (int): Number of top documents to re-rank with the Cross-Encoder.
            k_final (int): Number of top documents to return as the final result.

        Returns:
            str: Combined top document texts, separated by delimiters, as the retrieved context.
        """
        print(f"[Retriever] Performing hybrid search with RRF for: '{query}'")

        # --- 1. Retrieve candidates from FAISS vector store (semantic search) ---
        faiss_results_with_scores = self.vector_store.similarity_search_with_score(query, k=k_retrieve)
        # Map documents to their rank (1-based)
        faiss_ranked_results = {doc.page_content: i + 1 for i, (doc, score) in enumerate(faiss_results_with_scores)}
        print(f"[Retriever] FAISS found {len(faiss_ranked_results)} candidates.")

        # --- 2. Retrieve candidates from BM25 (keyword-based) ---
        tokenized_query = query.split(" ")
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_n_bm25_indices = np.argsort(bm25_scores)[::-1][:k_retrieve]
        # Map documents to their rank (1-based)
        bm25_ranked_results = {self.bm25_docs[idx]: i + 1 for i, idx in enumerate(top_n_bm25_indices)}
        print(f"[Retriever] BM25 found {len(bm25_ranked_results)} candidates.")

        # --- 3. Reciprocal Rank Fusion (RRF) to combine rankings ---
        rrf_scores = defaultdict(float)
        all_docs = set(faiss_ranked_results.keys()) | set(bm25_ranked_results.keys())

        for doc in all_docs:
            if doc in faiss_ranked_results:
                rrf_scores[doc] += 1.0 / (RRF_K + faiss_ranked_results[doc])
            if doc in bm25_ranked_results:
                rrf_scores[doc] += 1.0 / (RRF_K + bm25_ranked_results[doc])

        # Sort documents by combined RRF score in descending order
        reranked_by_rrf = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
        print(f"[Retriever] RRF combined to {len(reranked_by_rrf)} unique candidates.")

        # Select top candidates for cross-encoder re-ranking
        candidates_for_rerank = [doc for doc, score in reranked_by_rrf[:k_rerank]]

        if not candidates_for_rerank:
            return ""

        # --- 4. Cross-Encoder re-ranking to refine top documents ---
        print(f"[Retriever] Re-ranking top {len(candidates_for_rerank)} RRF candidates with CrossEncoder...")
        pairs = [[query, doc] for doc in candidates_for_rerank]
        scores = self.cross_encoder.predict(pairs, show_progress_bar=False)
        final_ranked_docs = sorted(zip(scores, candidates_for_rerank), key=lambda x: x[0], reverse=True)
        print(f"[Retriever] CrossEncoder re-ranking complete.")

        # --- 5. Format and return the final top-k documents as context ---
        final_docs = [doc for score, doc in final_ranked_docs[:k_final]]
        print(f"[Retriever] Selected top {len(final_docs)} documents.")

        context = "\n\n---\n\n".join(final_docs)

        return context
