import asyncio
from typing import Dict, List, Any
import random
import time
import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from src.core.llm.redaction_prompts import pronoun_prompt
from src.core.llm.pydantic_classes import RedactionResult

load_dotenv()
version = os.getenv("AZURE_OPENAI_API_VERSION")
azure_deployment = os.getenv("AZURE_OPENAI_CHAT_MODEL_ADVANCE")


llm = AzureChatOpenAI(
    azure_deployment=azure_deployment,
    api_version=version,
    temperature=0,
    max_retries=2,
)

structured_llm = llm.with_structured_output(RedactionResult)

pronoun_chain = pronoun_prompt | structured_llm


async def process_single_pronoun(
    pronoun_chain, input_data: Dict[str, Any], max_retries: int = 7
) -> Dict[str, Any]:
    """Process a single pronoun with custom retry logic."""
    retries = 0
    while retries < max_retries:
        try:
            result = await pronoun_chain.ainvoke(input_data)

            if result.redaction_reason:
                return {
                    "pronoun": input_data["input"]["entity_text"],
                    "pos_category": input_data["input"]["pos_category"],
                    "Redacted_text": result.redacted_text,
                    "redaction_reason": result.redaction_reason,
                    "corpus": input_data["input"]["context"],
                }
            return None

        except Exception as e:
            retries += 1
            if retries == max_retries:
                print(
                    f"Failed after {max_retries} attempts for pronoun {input_data['input'].get('entity_text', 'unknown')}: {str(e)}"
                )
                return None

            # Exponential backoff with some randomness
            wait_time = (2**retries) + random.uniform(0, 1)
            print(
                f"Retry {retries} for pronoun {input_data['input'].get('entity_text', 'unknown')}. Waiting {wait_time:.2f} seconds..."
            )
            await asyncio.sleep(wait_time)


async def process_pronoun_batch(
    pronouns_batch: List[Dict], pronoun_chain, subjects: Dict
) -> List[Dict]:
    """Process a batch of pronouns concurrently."""

    async def safe_process(pronoun_data: Dict) -> Dict:
        input_data = {"input": pronoun_data, "subjects": subjects}
        return await process_single_pronoun(pronoun_chain, input_data)

    # Create tasks for all pronouns in the batch
    tasks = [safe_process(pronoun) for pronoun in pronouns_batch]

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)

    # Filter out None results and return valid ones
    return [result for result in results if result is not None]


async def process_all_pronouns(
    pronouns: Dict[str, List[Dict]], pronoun_chain, subjects: Dict
) -> List[Dict]:
    """Process all pronouns across all categories concurrently."""
    # Flatten the pronouns dictionary into a single list
    all_pronouns = []
    for value in pronouns.values():
        all_pronouns.extend(value)

    # Process all pronouns concurrently
    results = await process_pronoun_batch(all_pronouns, pronoun_chain, subjects)
    return results


# Example usage
async def redact_pronouns(pronouns, subjects):
    # Your existing pronouns dictionary and subjects
    pronouns_result = await process_all_pronouns(pronouns, pronoun_chain, subjects)
    return pronouns_result
