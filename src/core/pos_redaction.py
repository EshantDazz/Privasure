import spacy
import asyncio
from typing import Dict, List, Union, Optional


async def analyze_pos_categories(
    document_chunks: Union[str, List[str]], file_name: str
) -> Optional[Dict]:
    """
    Extract pronouns and gender-specific nouns using spaCy with standardized output format

    Args:
        document_chunks (str or list): Input text or list of text chunks to analyze
        file_name (str): Name of the file being processed

    Returns:
        dict: Dictionary containing categorized words in standardized format
    """
    # Load English language model
    # Move this to a global variable or pass as parameter for better performance
    nlp = spacy.load("en_core_web_sm")

    # Initialize results structure
    categorized_results = {
        "file_name": file_name,
        "categories": {
            "personal_pronouns": [],
            "objective_pronouns": [],
            "possessive_pronouns": [],
            "interrogative_pronouns": [],
            "gender_nouns": [],
        },
    }

    # Define gender-related nouns
    gender_nouns = {
        "man",
        "woman",
        "boy",
        "girl",
        "male",
        "female",
        "gentleman",
        "lady",
        "sir",
        "madam",
        "father",
        "mother",
        "son",
        "daughter",
        "brother",
        "sister",
        "uncle",
        "aunt",
        "king",
        "queen",
        "prince",
        "princess",
        "husband",
        "wife",
        # Plurals
        "men",
        "women",
        "boys",
        "girls",
        "males",
        "females",
        "gentlemen",
        "ladies",
        "fathers",
        "mothers",
        "sons",
        "daughters",
        "brothers",
        "sisters",
        "uncles",
        "aunts",
        "kings",
        "queens",
        "princes",
        "princesses",
        "husbands",
        "wives",
    }

    # Ensure document_chunks is a list
    chunks = [document_chunks] if isinstance(document_chunks, str) else document_chunks

    try:
        # Track unique words across all chunks
        unique_entries = {
            category: set() for category in categorized_results["categories"]
        }

        # Process chunks asynchronously
        loop = asyncio.get_running_loop()

        async def process_chunk(chunk):
            # Process the text using spaCy in a thread pool
            doc = await loop.run_in_executor(None, nlp, chunk)

            chunk_entries = {
                category: set() for category in categorized_results["categories"]
            }

            # Process each token
            for token in doc:
                word_lower = token.text.lower()

                # Check for gender nouns
                if word_lower in gender_nouns:
                    chunk_entries["gender_nouns"].add(token.text)
                    continue

                # Check for pronouns
                if token.pos_ == "PRON":
                    if token.tag_ in ["WP", "WDT", "WP$"]:
                        category = "interrogative_pronouns"
                    elif token.tag_ == "PRP$":
                        category = "possessive_pronouns"
                    elif token.dep_ in ["nsubj", "nsubjpass"]:
                        category = "personal_pronouns"
                    elif token.dep_ in ["dobj", "pobj", "iobj"]:
                        category = "objective_pronouns"
                    else:
                        category = "personal_pronouns"

                    chunk_entries[category].add(token.text)

            return chunk_entries

        # Process all chunks concurrently
        chunk_results = await asyncio.gather(
            *[process_chunk(chunk) for chunk in chunks]
        )

        # Combine results from all chunks
        for chunk_result in chunk_results:
            for category, entries in chunk_result.items():
                unique_entries[category].update(entries)

        # Convert unique entries to final format
        for category in categorized_results["categories"]:
            categorized_results["categories"][category] = [
                {"text": word} for word in sorted(unique_entries[category])
            ]

        # Remove empty categories
        categorized_results["categories"] = {
            category: entities
            for category, entities in categorized_results["categories"].items()
            if entities
        }

    except Exception as e:
        print(f"Error processing file {file_name}: {str(e)}")
        return None

    return categorized_results


async def process_multiple_documents_for_pos(
    documents_dict: Dict[str, Union[str, List[str]]],
) -> List[Dict]:
    """
    Process multiple documents concurrently

    Args:
        documents_dict: Dictionary with {filename: document_text or list_of_chunks}

    Returns:
        List of dictionaries containing categorized words for each document
    """
    # Create tasks for all documents
    tasks = [
        analyze_pos_categories(document_content, file_name)
        for file_name, document_content in documents_dict.items()
    ]

    # Process all documents concurrently
    results = await asyncio.gather(*tasks)

    # Filter out None results
    return [result for result in results if result]


# Example usage in your Streamlit app:
async def process_pos_analysis(documents):
    """Wrapper function for POS analysis"""
    return await process_multiple_documents_for_pos(documents)
