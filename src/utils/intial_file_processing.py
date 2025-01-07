import pandas as pd
from io import BytesIO
import aiofiles
import asyncio
import pdfplumber
from pathlib import Path
from typing import Dict
import shutil
import streamlit as st


async def create_pii_excel(pii_results):
    """Create a formatted Excel file from PII results."""
    records = []

    for result in pii_results:
        file_name = result["file_name"]
        categories = result["categories"]

        for category, entities in categories.items():
            for entity in entities:
                records.append(
                    {
                        "File Name": file_name,
                        "Category": category,
                        "Detected Text": entity["text"],
                        "Confidence Score": f"{entity['confidence_score']:.2%}",
                    }
                )

    df = pd.DataFrame(records)

    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="PII Detection Results")

        workbook = writer.book
        worksheet = writer.sheets["PII Detection Results"]

        # Add formatting
        header_format = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#4B0082",  # Dark purple background
                "font_color": "white",
                "border": 1,
                "align": "center",
            }
        )

        # Center align format for cells
        center_format = workbook.add_format({"align": "center"})

        # Percentage format for confidence scores
        percent_format = workbook.add_format({"num_format": "0.00%", "align": "center"})

        # Apply formats to columns
        for col_num, column in enumerate(df.columns):
            worksheet.write(0, col_num, column, header_format)

            # Set column width based on content
            max_length = max(df[column].astype(str).apply(len).max(), len(column))
            worksheet.set_column(col_num, col_num, max_length + 3)

            # Apply center alignment to all cells in the column
            if column == "Confidence Score":
                worksheet.set_column(col_num, col_num, max_length + 3, percent_format)
            else:
                worksheet.set_column(col_num, col_num, max_length + 3, center_format)

        # Add alternating row colors
        for row_num in range(1, len(df) + 1):
            if row_num % 2 == 0:
                worksheet.set_row(
                    row_num, None, workbook.add_format({"bg_color": "#F0F0F0"})
                )

    return output.getvalue()


async def create_upload_dir():
    """Create a temporary directory for PDF storage if it doesn't exist."""
    pdf_dir = Path("pdf_storage")
    if not pdf_dir.exists():
        pdf_dir.mkdir(parents=True)
    return pdf_dir


async def process_pdf(pdf_path: Path) -> str:
    """Extract text from PDF using pdfplumber asynchronously."""
    loop = asyncio.get_running_loop()
    try:

        def extract_text():
            with pdfplumber.open(pdf_path) as pdf:
                return "\n\n".join(page.extract_text() for page in pdf.pages)

        return await loop.run_in_executor(None, extract_text)
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


async def cleanup_files(directory: Path):
    """Remove all files from the specified directory asynchronously."""
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, lambda: shutil.rmtree(directory) if directory.exists() else None
        )
        return True
    except Exception as e:
        st.error(f"Error during cleanup: {str(e)}")
        return False


async def save_uploaded_file(upload_dir: Path, uploaded_file) -> Path:
    """Save uploaded file asynchronously."""
    temp_path = upload_dir / uploaded_file.name
    async with aiofiles.open(temp_path, "wb") as f:
        await f.write(uploaded_file.getbuffer())
    return temp_path


async def process_uploaded_files(uploaded_files) -> Dict[str, str]:
    """Process multiple files asynchronously and return results dictionary."""
    if not uploaded_files:
        return {}

    upload_dir = await create_upload_dir()
    results = {}

    try:
        # Save files
        save_tasks = [save_uploaded_file(upload_dir, file) for file in uploaded_files]
        saved_paths = await asyncio.gather(*save_tasks)

        # Process PDFs
        process_tasks = [process_pdf(path) for path in saved_paths]
        contents = await asyncio.gather(*process_tasks)

        # Create results dictionary
        results = {
            uploaded_file.name: content
            for uploaded_file, content in zip(uploaded_files, contents)
        }

    finally:
        # Cleanup
        if upload_dir.exists():
            await cleanup_files(upload_dir)

    return results
