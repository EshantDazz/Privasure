import pandas as pd
from io import BytesIO
from datetime import datetime


def create_combined_report(pii_data, redactions_data, subject, pronouns_redaction=None):
    """
    Create a single comprehensive Excel report containing PII entities, redactions, and pronoun redactions

    Args:
        pii_data: List of dictionaries containing PII entities
        redactions_data: List of redaction results
        subject: String containing the subject name
        pronouns_redaction: List of pronoun redaction results (optional)
    """
    excel_buffer = BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        # Create summary sheet
        total_pronoun_redactions = len(pronouns_redaction) if pronouns_redaction else 0

        summary_data = {
            "Report Information": [
                "Analysis Date",
                "Subject",
                "Number of Files Analyzed",
                "Total Entities Detected",
                "Total Entity Redactions",
                "Total Pronoun Redactions",
            ],
            "Details": [
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                subject,
                len(pii_data),
                sum(
                    len(file_data["categories"].get("Person", []))
                    for file_data in pii_data
                ),
                len(redactions_data),
                total_pronoun_redactions,
            ],
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

        # Add PII Entities sheets (organized by file and category)
        for file_data in pii_data:
            file_name = file_data["file_name"]
            categories = file_data["categories"]

            # Create consolidated sheet for each file
            file_entities = []
            for category, entities in categories.items():
                for entity in entities:
                    entity_data = {
                        "Category": category,
                        "Entity": entity["text"],
                        "Confidence": entity["confidence_score"],
                    }
                    file_entities.append(entity_data)

            if file_entities:
                df = pd.DataFrame(file_entities)
                sheet_name = f"{file_name[:27]}_Entities"[:31]  # Excel sheet name limit
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Add Entity Redactions sheet
        redactions_formatted = []
        for item in redactions_data:
            redactions_formatted.append(
                {
                    "Original Entity": item["Entity"],
                    "Redaction Text": ", ".join(item["Redaction_text"]),
                    "Redaction Reason": item["redaction_reason"],
                    "Source Context": item["corpus"][:200] + "..."
                    if len(item["corpus"]) > 200
                    else item["corpus"],
                }
            )

        if redactions_formatted:
            pd.DataFrame(redactions_formatted).to_excel(
                writer, sheet_name="Entity_Redactions", index=False
            )

        # Add Pronoun Redactions sheet
        if pronouns_redaction:
            pronouns_formatted = []
            for item in pronouns_redaction:
                # Handle cases where Redacted_text is a list
                redacted_text = (
                    ", ".join(item["Redacted_text"])
                    if isinstance(item["Redacted_text"], list)
                    else item["Redacted_text"]
                )

                pronouns_formatted.append(
                    {
                        "Pronoun": item["pronoun"],
                        "POS Category": item["pos_category"],
                        "Redacted Text": redacted_text,
                        "Redaction Reason": item["redaction_reason"],
                        "Source Context": item["corpus"][:200] + "..."
                        if len(item["corpus"]) > 200
                        else item["corpus"],
                    }
                )

            if pronouns_formatted:
                pd.DataFrame(pronouns_formatted).to_excel(
                    writer, sheet_name="Pronoun_Redactions", index=False
                )

    excel_buffer.seek(0)
    return excel_buffer.getvalue()
