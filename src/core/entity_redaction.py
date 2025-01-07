from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from collections import defaultdict
import asyncio
from typing import Dict, List, Union


async def authenticate_client(endpoint: str, key: str) -> TextAnalyticsClient:
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, credential=ta_credential
    )
    return text_analytics_client


async def pii_recognition_by_category(
    client, document_chunks, file_name, confidence_threshold=0.20
):
    """
    Process either a single document or a list of document chunks
    """
    # Ensure document_chunks is a list
    if isinstance(document_chunks, str):
        documents = [document_chunks]
    else:
        documents = document_chunks

    categories = [
        "Organization",
        "PhoneNumber",
        "PersonType",
        "Address",
        "Person",
        "Email",
        "DateTime",
    ]

    categorized_results = {
        "file_name": file_name,
        "categories": {category: [] for category in categories},
    }

    # Track unique entities across all chunks
    unique_entries = defaultdict(lambda: defaultdict(float))

    try:
        # Process each chunk separately
        for chunk in documents:
            # Run the synchronous operation in a thread pool
            response = await asyncio.to_thread(
                client.recognize_pii_entities, [chunk], language="en"
            )
            result = [doc for doc in response if not doc.is_error]

            for doc in result:
                for entity in doc.entities:
                    if entity.confidence_score > confidence_threshold:
                        # Update if this is a new entry or has higher confidence
                        current_confidence = unique_entries[entity.category][
                            entity.text
                        ]
                        if entity.confidence_score > current_confidence:
                            unique_entries[entity.category][entity.text] = (
                                entity.confidence_score
                            )

        # Convert the unique entries to the final format
        for category in categories:
            for text, confidence in unique_entries[category].items():
                entity_info = {"text": text, "confidence_score": confidence}
                categorized_results["categories"][category].append(entity_info)

    except Exception as e:
        print(f"Error processing file {file_name}: {str(e)}")
        return None

    # Remove empty categories
    categorized_results["categories"] = {
        category: entities
        for category, entities in categorized_results["categories"].items()
        if entities
    }

    return categorized_results


async def process_multiple_documents(client, documents_dict, confidence_threshold=0.75):
    """
    Process multiple documents concurrently
    documents_dict: Dictionary with {filename: document_text or list_of_chunks}
    """
    tasks = []

    for file_name, document_content in documents_dict.items():
        task = pii_recognition_by_category(
            client, document_content, file_name, confidence_threshold
        )
        tasks.append(task)

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)
    return [
        result for result in results if result and any(result["categories"].values())
    ]


async def redact_entity(
    endpoint: str, key: str, documents: Dict[str, Union[str, List[str]]]
):
    # Initialize client
    client = await authenticate_client(endpoint=endpoint, key=key)

    # Process documents
    results = await process_multiple_documents(client, documents)
    return results
