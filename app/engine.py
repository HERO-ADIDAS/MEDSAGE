# ============================================================
# Imports
# ============================================================

from rag_system.retriever import AdvancedRetriever
from app.nim_client import get_nim_llm
from app import prompts
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
import re  # Import regex for simple rule-based checks

# ============================================================
# DiagnosticEngine Class
# Main class for handling diagnostic logic and LCEL chain creation
# ============================================================

class DiagnosticEngine:
    def __init__(self):
        """
        Initialize the DiagnosticEngine with LLM, classifier, and retriever.
        """
        print("Initializing Diagnostic Engine...")
        self.llm = get_nim_llm()  # Main LLM for diagnosis
        # Optional: Use a smaller/faster LLM for classification if needed
        self.classifier_llm = self.llm  # Using the same LLM for now
        self.retriever = AdvancedRetriever()
        print("Engine initialized. Ready for requests.")

    # ============================================================
    # Helper Methods
    # ============================================================

    def _format_history(self, chat_history: list) -> str:
        """
        Format chat history into a readable string for LLM context.
        """
        if not chat_history:
            return "No history yet."
        formatted_history = ""
        for turn in chat_history:
            formatted_history += f"User: {turn.human}\n"
            # Make sure the AI response exists before adding (important for current turn)
            if turn.ai:
                formatted_history += f"AI: {turn.ai}\n"
        return formatted_history.strip()

    def _classify_input(self, input_dict: dict) -> str:
        """
        Classify user input as ANSWER_ONLY or NEW_INFO.
        Uses rule-based checks first, then falls back to LLM classification.
        """
        history = input_dict["history"]
        last_user_message = history[-1].human
        last_ai_question = history[-2].ai if len(history) > 1 else ""  # Get previous AI question

        # --- 1. Rule-Based Check for simple answers ---
        simple_answer_pattern = r"^(yes|no|yeah|nope|yep|nah|i don'?t know|maybe|sometimes|rarely|often)\b[\.,!?]?\s*$"
        # Check if the message is short and matches simple patterns
        if len(last_user_message.split()) <= 5 and re.match(simple_answer_pattern, last_user_message, re.IGNORECASE):
            print("[DEBUG] Classified as ANSWER_ONLY (Rule-Based)")
            return "ANSWER_ONLY"

        # --- 2. LLM Classification (if rule doesn't match) ---
        print("[DEBUG] Performing LLM Classification...")
        classification_chain = (
            prompts.CLASSIFICATION_PROMPT
            | self.classifier_llm  # Use the dedicated classifier LLM if defined
            | StrOutputParser()
        )
        classification_result = classification_chain.invoke({
            "last_ai_question": last_ai_question,
            "user_input": last_user_message
        }).strip().upper()  # Ensure consistent format

        # Basic validation of LLM output
        if classification_result not in ["NEW_INFO", "ANSWER_ONLY"]:
            print(f"[WARN] LLM Classifier returned unexpected value: '{classification_result}'. Defaulting to NEW_INFO.")
            classification_result = "NEW_INFO"  # Default to retrieving if unsure

        print(f"[DEBUG] Classified as {classification_result} (LLM)")
        return classification_result

    # ============================================================
    # Main Chain Creation
    # Creates the LCEL chain with conditional retrieval logic
    # ============================================================

    def get_chain(self):
        """
        Creates the main LCEL chain with conditional retrieval.
        """
        # --- Helper functions ---
        def extract_last_query(input_dict: dict) -> str:
            return input_dict["history"][-1].human

        def get_context(search_query: str) -> str:
            print(f"[DEBUG] Retrieving context for query: '{search_query}'")
            context = self.retriever.search(search_query)
            print(f"[DEBUG] Retrieved context length: {len(context)}")
            return context

        def should_retrieve(classification_result: str) -> bool:
            retrieve = classification_result == "NEW_INFO"
            print(f"[DEBUG] Should retrieve context? {retrieve}")
            return retrieve

        # --- Define Chain Steps ---

        # Step 1: Classify the latest user input
        classification_chain = RunnableLambda(self._classify_input)

        # Step 2: Define the RAG path (Retrieve context)
        rag_chain_with_context = RunnablePassthrough.assign(
            search_query=RunnableLambda(extract_last_query),  # Use direct query now
        ).assign(
            context=lambda x: get_context(x['search_query'])
        )

        # Step 3: Define the Non-RAG path (No context retrieval)
        chain_without_context = RunnablePassthrough.assign(
            search_query=RunnableLambda(extract_last_query),  # Still log the query used
            context=lambda x: "[CONTEXT SKIPPED]"  # Indicate context wasn't retrieved
        )

        # Step 4: Branch based on classification
        conditional_retrieval_chain = RunnableBranch(
            # Condition: If classification is NEW_INFO, run the RAG chain
            (lambda x: should_retrieve(x['classification']), rag_chain_with_context),
            # Default: Otherwise, run the chain without context
            chain_without_context
        )

        # Step 5: Final Generation Chain
        generation_chain = (
            prompts.DIAGNOSTIC_PROMPT
            | self.llm
            | StrOutputParser()
        )

        # --- Combine steps ---
        full_chain = RunnablePassthrough.assign(
            classification=classification_chain  # Run classification first
        ).pipe(  # Pipe the result (including classification) to the branch
            conditional_retrieval_chain
        ).assign(  # Now add history formatting and run the final generation
            history_formatted=lambda x: self._format_history(x['history'])
        ).assign(
            ai_response=lambda x: generation_chain.invoke(
                {"context": x['context'], "history": x['history_formatted']}
            )
        )

        # Select final outputs
        output_chain = full_chain | (lambda x: {
            "ai_response": x['ai_response'],
            "search_query": x.get('search_query', 'ERROR: search_query not found'),
            "retrieved_context": x.get('context', 'ERROR: context not found')
        })

        return output_chain
