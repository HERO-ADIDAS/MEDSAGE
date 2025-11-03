# ============================================================
# Imports
# ============================================================

import pandas as pd
import xml.etree.ElementTree as ET
import os

# ============================================================
# Configuration
# ============================================================

# List of raw data directories to process; currently contains approved folder only
RAW_DATA_DIRS = [
    "data/raw/4_MPlus_Health_Topics_QA"
]

# Output path for combined processed CSV
PROCESSED_DATA_PATH = "data/processed/medsage_processed.csv"

# ============================================================
# Main Preprocessing Function
# ============================================================

def preprocess_medquad_xml_recursive():
    """
    Recursively searches for all XML files in the specified data directories,
    extracts question-answer pairs along with associated metadata (focus topic,
    semantic types, synonyms), and combines all data into a single CSV file.
    """
    all_rows = []

    # Traverse all directories in RAW_DATA_DIRS
    for data_dir in RAW_DATA_DIRS:
        if not os.path.exists(data_dir):
            print(f"Warning: Data directory not found at {data_dir}. Skipping.")
            continue

        print(f"Searching for XML files in '{data_dir}'...")

        # Recursively walk directory to find XML files
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    try:
                        tree = ET.parse(file_path)
                        xml_root = tree.getroot()

                        # Extract main topic or focus from <Focus> tag
                        focus_element = xml_root.find('Focus')
                        focus_text = focus_element.text.strip() if focus_element is not None and focus_element.text else ""

                        # Extract semantic types and synonyms from <FocusAnnotations>, if available
                        focus_annotations = xml_root.find('.//FocusAnnotations')
                        semantic_types = []
                        synonyms = []
                        if focus_annotations is not None:
                            semantic_types = [st.text for st in focus_annotations.findall('.//SemanticType')]
                            synonyms = [s.text for s in focus_annotations.findall('.//Synonym')]

                        semantic_types_str = "|".join(filter(None, semantic_types))
                        synonyms_str = "|".join(filter(None, synonyms))

                        # Extract all QAPair entries with their questions and answers
                        for qa_pair in xml_root.findall('.//QAPair'):
                            question_element = qa_pair.find('Question')
                            answer_element = qa_pair.find('Answer')

                            if question_element is not None and answer_element is not None:
                                question = question_element.text
                                answer = answer_element.text

                                # Collect only complete QA pairs (non-empty)
                                if question and answer:
                                    all_rows.append({
                                        'focus': focus_text,
                                        'question': question.strip(),
                                        'answer': answer.strip(),
                                        'semantic_types': semantic_types_str,
                                        'synonyms': synonyms_str
                                    })

                    except ET.ParseError:
                        print(f"Warning: Could not parse {file_path}.")

    # Convert the list of dicts to a DataFrame
    print(f"\nExtracted a total of {len(all_rows)} question-answer pairs.")
    df = pd.DataFrame(all_rows)

    # Ensure output directory exists
    os.makedirs("data/processed", exist_ok=True)

    # Save combined data to CSV
    print(f"Saving combined processed data to {PROCESSED_DATA_PATH}")
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print("Preprocessing complete.")

# ============================================================
# Execution guard
# ============================================================

if __name__ == "__main__":
    preprocess_medquad_xml_recursive()
