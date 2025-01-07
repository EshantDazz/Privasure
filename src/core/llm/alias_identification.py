from src.core.llm.prompts import alias_prompt
from langchain_openai import AzureChatOpenAI
from src.core.llm.pydantic_classes import AliasMatch
from dotenv import load_dotenv
import os
import json
import asyncio

load_dotenv()
version = os.getenv("AZURE_OPENAI_API_VERSION")
azure_deployment = os.getenv("AZURE_OPENAI_CHAT_MODEL_ADVANCE")


llm = AzureChatOpenAI(
    azure_deployment=azure_deployment,
    api_version=version,
    temperature=0,
    max_retries=2,
)


async def get_allias_list(final_result, subject):
    filtered_data = [
        item for item in final_result if item["entity_type"] in ["Person", "PersonType"]
    ]

    # Remove 'file_name' key from each dictionary in the list
    for item in filtered_data:
        item.pop("file_name", None)

    # Write filtered data to JSON file
    with open("filter_data.json", "w") as f:
        json.dump(filtered_data, f, indent=4)

    structured_llm = llm.with_structured_output(AliasMatch)
    alias_chain = alias_prompt | structured_llm
    input_data = {"subject": subject, "final_result": filtered_data}
    alias_result = await alias_chain.ainvoke(input_data)
    return alias_result


async def process_all_files_alias(segregated_results, subject):
    async def safe_process(file_name, file_data):
        try:
            result = await get_allias_list(file_data, subject)
            return file_name, result.aliases
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")
            return file_name, []

    # Create tasks for each file
    tasks = [
        safe_process(file_name, file_data)
        for file_name, file_data in segregated_results.items()
    ]

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)

    # Convert results to dictionary
    return {file_name: aliases for file_name, aliases in results}
