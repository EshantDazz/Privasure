from ftplib import all_errors
import streamlit as st
import pdfplumber
from pathlib import Path
import shutil
import asyncio
from dotenv import load_dotenv
import os
from langchain_community.callbacks import get_openai_callback
import pandas as pd
from datetime import datetime
from src.utils.download_excel import create_combined_report
from src.utils.file_processing import (
    process_documents_pos,
    process_entities_with_context,
    process_pos_with_context,
    process_all_results,
    segregate_by_file,
    find_filtered_entities,
    clean_nested_dict,
)
from src.core.llm.pronoun_redaction import redact_pronouns
from src.core.entity_redaction import redact_entity
from src.utils.intial_file_processing import process_uploaded_files
from src.core.llm.alias_identification import process_all_files_alias
from src.core.llm.redaction_ai import generate_redactions
from src.core.pos_redaction import process_pos_analysis

load_dotenv()

key = os.getenv("AZURE_PII_KEY")
endpoint = os.getenv("AZURE_PII_ENDPOINT")


async def render_ui():
    """Async function to render the Streamlit UI."""
    st.title("SAR Redactions streamlit app")
    st.write("Upload PDF files to extract their text content")

    # Add subject input box
    subject = st.text_input(
        "Please enter the subject:", placeholder="e.g., Mark Harrison"
    )

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files", type="pdf", accept_multiple_files=True
    )

    if uploaded_files and subject:
        if st.button("Process PDFs"):
            with st.spinner("Processing PDFs..."):
                documents = await process_uploaded_files(uploaded_files)

            with st.spinner("Detecting PIIS and POS..."):
                if documents:
                    documents = process_documents_pos(documents)
                    results1 = await redact_entity(
                        documents=documents, key=key, endpoint=endpoint
                    )

                    results2 = await process_pos_analysis(documents)

            with st.spinner("Preprocess Data"):
                contextual_results1 = process_entities_with_context(results1, documents)
                contextual_results2 = process_pos_with_context(results2, documents)

                final_results = process_all_results(
                    contextual_results1, contextual_results2
                )
                unique_files = list(
                    set(item["file_name"] for item in final_results["pii_results"])
                )
                segregated_results = segregate_by_file(
                    final_results["pii_results"], unique_files
                )
                files_alias = await process_all_files_alias(segregated_results, subject)

                all_aliases = []
                for aliases in files_alias.values():
                    all_aliases.extend(aliases)

                unique_all_aliases = list(set(all_aliases))
                all_aliases = [subject] + unique_all_aliases
                st.info(f"Aliases of the subject are {all_aliases}")

                segregated_results_pos = segregate_by_file(
                    final_results["pos_results"], unique_files
                )

                non_alias_perameters = find_filtered_entities(
                    segregated_results, files_alias, subject=subject
                )
                non_alias_perameters = clean_nested_dict(non_alias_perameters)
                clean_pronouns = clean_nested_dict(segregated_results_pos)

            with st.spinner("Generating Redactions......."):
                with get_openai_callback() as cb:
                    redactions = await generate_redactions(
                        non_alias_parameters=non_alias_perameters, alias=all_aliases
                    )
                    pronouns_redaction = await redact_pronouns(
                        clean_pronouns, all_aliases
                    )
                    print(f"Total Cost (USD): ${format(cb.total_cost, '.6f')}")

                st.toast(
                    f"Total Cost (USD): ${format(cb.total_cost, '.6f')}", icon="💰"
                )

                st.info("These are the redactions")
                st.json(redactions)

                st.info("These are the pronouns redacted")
                st.json(pronouns_redaction)

                # Add download buttons
                try:
                    combined_report = create_combined_report(
                        results1, redactions, subject, pronouns_redaction
                    )
                    st.download_button(
                        label="Download Complete Analysis Report",
                        data=combined_report,
                        file_name=f"document_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")

    elif uploaded_files and not subject:
        st.warning("Please enter a subject before processing.")


async def main():
    """Main async function."""
    await render_ui()


if __name__ == "__main__":
    asyncio.run(main())
