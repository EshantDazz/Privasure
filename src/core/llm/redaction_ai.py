from langchain_openai import AzureChatOpenAI
from src.core.llm.pydantic_classes import RedactionResult
import os
from src.core.llm.redaction_prompts import (
    persom_prompt,
    phone_number_prompt,
    email_prompt,
    organisation_prompt,
    address_prompt,
)
from dotenv import load_dotenv
import asyncio
from asyncio import sleep

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

person_chain = persom_prompt | structured_llm
organization_chain = organisation_prompt | structured_llm
phone_number_chain = phone_number_prompt | structured_llm
email_chain = email_prompt | structured_llm
address_chain = address_prompt | structured_llm


async def process_entity(chain, item, subjects, max_retries=6):
    retry_count = 0
    while retry_count < max_retries:
        try:
            input_data = {"subjects": subjects, "input": item}
            result = await chain.ainvoke(input_data)
            return {
                "Entity": item["entity_text"],
                "Redaction_text": result.redacted_text,
                "redaction_reason": result.redaction_reason,
                "corpus": item["context"],
            }
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                print(
                    f"Failed after {max_retries} attempts for entity {item['entity_text']}: {str(e)}"
                )
                raise e

            # Exponential backoff: 2^retry_count seconds
            wait_time = 2**retry_count
            print(
                f"Attempt {retry_count} failed for {item['entity_text']}, retrying in {wait_time} seconds..."
            )
            await sleep(wait_time)


async def process_all_entities(
    persons, organizations, emails, phone_numbers, addresses, subjects
):
    tasks = []

    # Add person tasks
    tasks.extend([process_entity(person_chain, person, subjects) for person in persons])

    # Add organization tasks
    tasks.extend([process_entity(person_chain, org, subjects) for org in organizations])

    # Add email tasks
    tasks.extend([process_entity(email_chain, email, subjects) for email in emails])

    # Add phone number tasks
    tasks.extend(
        [process_entity(phone_number_chain, phone, subjects) for phone in phone_numbers]
    )

    # Add address tasks
    tasks.extend(
        [process_entity(address_chain, address, subjects) for address in addresses]
    )

    # Run all tasks concurrently and gather results
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out any failed results
    result = [r for r in results if not isinstance(r, Exception)]
    return result


async def generate_redactions(non_alias_parameters, alias):
    for key, data in non_alias_parameters.items():
        # Initialize all entity type lists in one line
        entity_lists = {
            entity_type: []
            for entity_type in [
                "Organization",
                "PhoneNumber",
                "PersonType",
                "Address",
                "Person",
                "Email",
                "DateTime",
            ]
        }

        # Append full entity information to their respective lists
        [
            entity_lists[item["entity_type"]].append(
                {"entity_text": item["entity_text"], "context": item["context"]}
            )
            for item in data
        ]

        # Unpack into separate variables
        organizations = entity_lists["Organization"]
        persons = entity_lists["Person"]
        phone_numbers = entity_lists["PhoneNumber"]
        emails = entity_lists["Email"]
        addresses = entity_lists["Address"]

        redaction = await process_all_entities(
            persons, organizations, emails, phone_numbers, addresses, alias
        )
        return redaction
