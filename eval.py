# ============================================================
# Imports
# ============================================================

import pandas as pd
from rag_system.retriever import AdvancedRetriever
import time
import re
from difflib import SequenceMatcher  # Imported but not currently used
from sentence_transformers import SentenceTransformer, util

# ============================================================
# Constants and Configuration
# ============================================================

embedding_model = SentenceTransformer('./all-MiniLM-L6-v2')  # Load embedding model once
COSINE_SIM_THRESHOLD = 0.85  # Threshold for semantic cosine similarity
EVAL_DATA_PATH = "eval.csv"  # Evaluation data filepath
K = 10  # Number of top documents to consider in metrics
SIMILARITY_THRESHOLD = 0.9  # For SequenceMatcher (optional, currently unused)


# ============================================================
# Utility Functions
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text by lowercasing, stripping, reducing whitespace, and removing some punctuation.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = re.sub(r'[.,!?"\'-]', '', text)  # Remove punctuation (adjust as needed)
    return text


def calculate_metrics(retrieved_docs: list[str], relevant_docs: list[str], k: int, query_index: int) -> tuple[int, float]:
    """
    Calculate Hit Rate and Mean Reciprocal Rank (MRR) for one query.
    Uses cosine similarity of embeddings with threshold defined globally.
    
    Args:
        retrieved_docs: List of retrieved document texts.
        relevant_docs: List of expected relevant document texts.
        k: Top-k cutoff for evaluation.
        query_index: Index for logging/debugging.
    
    Returns:
        hit (int): 1 if any retrieved doc matches relevant docs semantically, 0 otherwise.
        reciprocal_rank (float): Reciprocal rank of first matching document or 0 if none found.
    """
    hit = 0
    reciprocal_rank = 0.0
    top_k_retrieved = retrieved_docs[:k]

    # Filter out empty or invalid docs to avoid errors
    relevant_docs = [doc for doc in relevant_docs if isinstance(doc, str) and doc.strip()]
    retrieved_docs = [doc for doc in top_k_retrieved if isinstance(doc, str) and doc.strip()]

    if not relevant_docs or not retrieved_docs:
        print(f"  [MetricsDebug Q{query_index}] Missing valid relevant or retrieved docs.")
        return 0, 0.0

    # Encode documents into embeddings (Tensor format)
    relevant_embeddings = embedding_model.encode(relevant_docs, convert_to_tensor=True)
    retrieved_embeddings = embedding_model.encode(retrieved_docs, convert_to_tensor=True)

    found_match_at_rank = -1

    # Check each retrieved doc against all relevant docs for semantic similarity
    for rank, retrieved_emb in enumerate(retrieved_embeddings, 1):
        cosine_scores = util.cos_sim(retrieved_emb, relevant_embeddings)
        max_similarity = float(cosine_scores.max())

        print(f"    [MetricsDebug Q{query_index} Rank {rank}] Max Cosine Similarity: {max_similarity:.4f}")

        if max_similarity >= COSINE_SIM_THRESHOLD:
            print(f"    [MetricsDebug Q{query_index} Rank {rank}] ---> SEMANTIC MATCH FOUND (cos_sim >= {COSINE_SIM_THRESHOLD})")
            if found_match_at_rank == -1:
                found_match_at_rank = rank
            break  # Stop checking after first match

    if found_match_at_rank != -1:
        hit = 1
        reciprocal_rank = 1.0 / found_match_at_rank
        print(f"  [MetricsDebug Q{query_index}] First match at Rank {found_match_at_rank}. Hit=1, RR={reciprocal_rank:.4f}")
    else:
        print(f"  [MetricsDebug Q{query_index}] No semantic match found in Top {k}. Hit=0, RR=0.0")

    return hit, reciprocal_rank

# ============================================================
# Main Evaluation Function
# ============================================================

def evaluate_retriever():
    """
    Loads evaluation queries and relevant documents, uses AdvancedRetriever to retrieve,
    compares results using semantic cosine similarity metrics, and prints overall Hit Rate and MRR.
    """
    print("Loading retriever...")
    try:
        retriever = AdvancedRetriever()
    except Exception as e:
        print(f"Failed to initialize retriever: {e}")
        return

    print(f"Loading evaluation data from: {EVAL_DATA_PATH}")
    try:
        eval_df = pd.read_csv(EVAL_DATA_PATH)
        relevant_cols = [col for col in eval_df.columns if col.startswith('relevant_doc_')]
        print(f"Found {len(eval_df)} evaluation queries.")
    except FileNotFoundError:
        print(f"Error: Evaluation data file not found at '{EVAL_DATA_PATH}'.")
        return
    except Exception as e:
        print(f"Error loading evaluation data: {e}")
        return

    total_hits = 0
    total_reciprocal_rank = 0.0
    start_time = time.time()

    print(f"\nRunning evaluation for Top {K} results...")
    queries_evaluated_count = 0

    for index, row in eval_df.iterrows():
        query_index = index + 1
        query = str(row['query']).strip() if pd.notna(row['query']) else None
        relevant_docs = [str(row[col]).strip() for col in relevant_cols if pd.notna(row[col])]
        relevant_docs = [doc for doc in relevant_docs if doc]

        if not query or not relevant_docs:
            print(f"Skipping row {query_index}: Missing query or valid relevant documents.")
            continue

        queries_evaluated_count += 1
        print(f"\n--- Query {query_index}/{len(eval_df)}: '{query}' ---")
        print(f"Expected Relevant Doc(s) (first 100 chars): {[doc[:100]+'...' for doc in relevant_docs]}")

        retrieved_docs_str = retriever.search(query, k_final=K)
        retrieved_docs_list = retrieved_docs_str.split("\n\n---\n\n") if retrieved_docs_str else []
        print(f"Retrieved {len(retrieved_docs_list)} docs.")

        print("Top Retrieved Docs (first 100 chars):")
        if not retrieved_docs_list:
            print("  (None)")
        for i, doc in enumerate(retrieved_docs_list[:K]):
            print(f"  {i+1}. {doc[:100]}...")

        hit, reciprocal_rank = calculate_metrics(retrieved_docs_list, relevant_docs, K, query_index)
        total_hits += hit
        total_reciprocal_rank += reciprocal_rank
        print(f"Result for Query {query_index}: Hit={hit}, RR={reciprocal_rank:.4f}")

    end_time = time.time()

    # Compute average Hit Rate (%) and MRR across all queries evaluated
    hit_rate = (total_hits / queries_evaluated_count) * 100 if queries_evaluated_count > 0 else 0
    mrr = (total_reciprocal_rank / queries_evaluated_count) if queries_evaluated_count > 0 else 0

    print("\n--- Evaluation Summary ---")
    print(f"Total Queries Evaluated: {queries_evaluated_count}")
    print(f"Evaluation Rank (k): {K}")
    print(f"Hit Rate@{K}: {hit_rate:.2f}%")
    print(f"MRR@{K}: {mrr:.4f}")
    print(f"Total Evaluation Time: {end_time - start_time:.2f} seconds")


# ============================================================
# Main Execution Guard
# ============================================================

if __name__ == "__main__":
    evaluate_retriever()
