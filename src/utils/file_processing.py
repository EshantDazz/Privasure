def process_documents_pos(documents, chunk_size=500):
    """
    Process a dictionary of documents, chunking any large values while maintaining the same keys.

    Args:
        documents (dict): Dictionary of documents with their content
        chunk_size (int): Maximum size of each chunk (default: 500)

    Returns:
        dict: Processed dictionary where large values are converted to lists of chunks
    """
    processed_docs = {}

    for key, value in documents.items():
        if len(value) <= chunk_size:
            processed_docs[key] = value
        else:
            chunks = []
            remaining_text = value

            while remaining_text:
                if len(remaining_text) <= chunk_size:
                    chunks.append(remaining_text)
                    break

                # Find the last space before chunk_size
                split_point = remaining_text.rfind(" ", 0, chunk_size)
                if split_point == -1:
                    split_point = chunk_size

                # Add chunk
                chunks.append(remaining_text[:split_point])

                # Remove processed chunk
                remaining_text = remaining_text[split_point:].lstrip()

            processed_docs[key] = chunks

    return processed_docs


import re


def extract_context_sentences(chunks, target_text, context_before, context_after):
    """
    Extract sentences around a target text with specified context window,
    handling both single strings and lists of chunks
    """
    # If chunks is a list, combine them with spaces
    if isinstance(chunks, list):
        text = " ".join(chunks)
    else:
        text = chunks

    # Split text into sentences (considering common abbreviations)
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)

    # Find the sentence containing the target text
    target_sentence_idx = None
    for idx, sentence in enumerate(sentences):
        if target_text in sentence:
            target_sentence_idx = idx
            break

    if target_sentence_idx is None:
        return None

    # Get context window
    start_idx = max(0, target_sentence_idx - context_before)
    end_idx = min(len(sentences), target_sentence_idx + context_after + 1)

    return " ".join(sentences[start_idx:end_idx])


def find_chunk_with_entity(chunks, entity_text):
    """
    Find which chunk contains the entity and return combined context
    """
    if isinstance(chunks, str):
        return chunks

    # Initialize variables for context
    chunk_idx = None
    for idx, chunk in enumerate(chunks):
        if entity_text in chunk:
            chunk_idx = idx
            break

    if chunk_idx is None:
        return " ".join(chunks)  # If not found, return all chunks combined

    # Get surrounding chunks for context
    start_idx = max(0, chunk_idx - 1)
    end_idx = min(len(chunks), chunk_idx + 2)
    return " ".join(chunks[start_idx:end_idx])


def process_entities_with_context(pii_results, documents):
    """
    Process PII entities and extract contextual sentences,
    handling both regular strings and chunked documents
    """
    context_results = []

    for doc_result in pii_results:
        file_name = doc_result["file_name"]
        document_content = documents[file_name]

        for category, entities in doc_result["categories"].items():
            for entity in entities:
                entity_text = entity["text"]

                # Determine context window based on category
                if category in ["Person", "PersonType"]:
                    context_before = 5
                    context_after = 3
                else:
                    context_before = 2
                    context_after = 2

                # Get relevant chunks containing the entity
                relevant_text = find_chunk_with_entity(document_content, entity_text)

                context = extract_context_sentences(
                    relevant_text, entity_text, context_before, context_after
                )

                if context:
                    result = {
                        "file_name": file_name,
                        "entity_type": category,
                        "entity_text": entity_text,
                        "context": context,
                    }
                    context_results.append(result)

    return context_results


def extract_context_sentences(text, target_text, context_before=3, context_after=2):
    """
    Extract sentences around a target text with specified context window
    """
    # Handle input text that could be either a string or list
    if isinstance(text, list):
        text = " ".join(text)

    # Split text into sentences (considering common abbreviations)
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)

    # Find the sentence containing the target text
    target_sentence_idx = None
    for idx, sentence in enumerate(sentences):
        if target_text in sentence:
            target_sentence_idx = idx
            break

    if target_sentence_idx is None:
        return None

    # Get context window
    start_idx = max(0, target_sentence_idx - context_before)
    end_idx = min(len(sentences), target_sentence_idx + context_after + 1)

    return " ".join(sentences[start_idx:end_idx])


def find_chunk_with_word(chunks, target_word):
    """
    Find and return relevant chunks containing the target word with context
    """
    if isinstance(chunks, str):
        return chunks

    # Find chunk containing the word
    relevant_chunks = []
    found_idx = -1

    for idx, chunk in enumerate(chunks):
        if target_word in chunk:
            found_idx = idx
            break

    if found_idx != -1:
        # Get surrounding chunks for context
        start_idx = max(0, found_idx - 1)
        end_idx = min(len(chunks), found_idx + 2)
        relevant_chunks = chunks[start_idx:end_idx]
        return " ".join(relevant_chunks)

    return " ".join(chunks)  # If not found, return all chunks


def process_pos_with_context(pos_results, documents):
    """
    Process POS results and extract contextual sentences,
    handling both regular strings and chunked documents
    """
    context_results = []

    for doc_result in pos_results:
        file_name = doc_result["file_name"]
        document_content = documents[file_name]

        for pos_category, entities in doc_result["categories"].items():
            for entity in entities:
                entity_text = entity["text"]

                # Get relevant chunk context for this entity
                relevant_text = find_chunk_with_word(document_content, entity_text)

                context = extract_context_sentences(
                    relevant_text, entity_text, context_before=3, context_after=2
                )

                if context:
                    result = {
                        "file_name": file_name,
                        "pos_category": pos_category,
                        "entity_text": entity_text,
                        "context": context,
                    }
                    context_results.append(result)

    return context_results


def deduplicate_person_contexts(contextual_results1):
    """
    Properly deduplicate contexts between Person and PersonType categories
    while preserving other categories
    """
    # Keep track of seen contexts for Person/PersonType
    seen_contexts = {}
    indices_to_remove = set()

    # First pass: Collect all Person entries
    for idx, result in enumerate(contextual_results1):
        if result["entity_type"] == "Person":
            context = result["context"]
            if context not in seen_contexts:
                seen_contexts[context] = {
                    "idx": idx,
                    "type": "Person",
                    "entity_text": result["entity_text"],
                }

    # Second pass: Check PersonType entries and mark duplicates for removal
    for idx, result in enumerate(contextual_results1):
        if result["entity_type"] == "PersonType":
            context = result["context"]
            if context in seen_contexts:
                indices_to_remove.add(idx)
            else:
                seen_contexts[context] = {
                    "idx": idx,
                    "type": "PersonType",
                    "entity_text": result["entity_text"],
                }

    # Create new list without duplicate contexts
    deduplicated_results = []

    for idx, result in enumerate(contextual_results1):
        if result["entity_type"] not in ["Person", "PersonType"]:
            # Keep all non-Person/PersonType entries
            deduplicated_results.append(result)
        elif idx not in indices_to_remove and result["context"] in seen_contexts:
            if seen_contexts[result["context"]]["idx"] == idx:
                deduplicated_results.append(result)

    return deduplicated_results


def process_all_results(contextual_results1, contextual_results2):
    """
    Process both PII and POS results with proper deduplication
    """
    deduplicated_results1 = deduplicate_person_contexts(contextual_results1)

    return {"pii_results": deduplicated_results1, "pos_results": contextual_results2}


# Verification function
def verify_uniqueness(results):
    """
    Verify that contexts are unique between Person and PersonType
    """
    contexts = {}
    duplicates = []

    for result in results:
        if result["entity_type"] in ["Person", "PersonType"]:
            context = result["context"]
            if context in contexts:
                duplicates.append(
                    {
                        "context": context,
                        "first": contexts[context],
                        "second": {
                            "type": result["entity_type"],
                            "text": result["entity_text"],
                        },
                    }
                )
            else:
                contexts[context] = {
                    "type": result["entity_type"],
                    "text": result["entity_text"],
                }

    return len(duplicates) == 0, duplicates


def segregate_by_file(results, unique_files):
    """
    Segregate results by file name

    Args:
        results: List of result dictionaries
        unique_files: List of unique file names

    Returns:
        dict: Dictionary with file names as keys and their respective results as values
    """
    segregated_data = {file_name: [] for file_name in unique_files}

    for item in results:
        file_name = item["file_name"]
        segregated_data[file_name].append(item)

    return segregated_data


def find_filtered_entities(segregated_results, files_alias, subject):
    filtered_results = {}

    for filename in segregated_results:
        # Get list of aliases for this file
        file_aliases = files_alias.get(filename, [])

        # Initialize list for this file
        filtered_entities = []

        for item in segregated_results[filename]:
            should_include = False

            if item.get("entity_type") == "Person":
                # Include person only if not in aliases and not the subject
                if (
                    item.get("entity_text") not in file_aliases
                    and item.get("entity_text") != subject
                ):
                    should_include = True
            else:
                # Include all non-Person entities
                should_include = True

            if should_include:
                filtered_entities.append(item)

        if filtered_entities:  # Only add to result if we found any entities
            filtered_results[filename] = filtered_entities

    return filtered_results


def clean_nested_dict(data):
    """
    Removes 'file_name' key-value pairs from nested dictionaries while preserving the outer structure.

    Args:
        data (dict): Input dictionary containing nested data

    Returns:
        dict: Cleaned dictionary with 'file_name' entries removed from nested structures
    """
    # If the input is not a dictionary, return it as is
    if not isinstance(data, dict):
        return data

    # Create a new dictionary for the cleaned data
    cleaned_data = {}

    # Iterate through all key-value pairs in the input dictionary
    for key, value in data.items():
        if isinstance(value, list):
            # If value is a list, process each item in the list
            cleaned_list = []
            for item in value:
                if isinstance(item, dict):
                    # Remove 'file_name' from each dictionary in the list
                    cleaned_dict = {k: v for k, v in item.items() if k != "file_name"}
                    cleaned_list.append(cleaned_dict)
                else:
                    cleaned_list.append(item)
            cleaned_data[key] = cleaned_list
        else:
            # Keep other key-value pairs as they are
            cleaned_data[key] = value

    return cleaned_data


# Example usage:
# cleaned_result = clean_nested_dict(your_dictionary)
