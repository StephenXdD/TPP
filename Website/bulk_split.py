import fitz  # PyMuPDF
import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Mapping for month abbreviations
mapping_dict = {
    'w': 'Oct_Nov',
    'm': 'Feb_March',
    's': 'May_June'
}

def split_pdf_into_questions(input_pdf_path, output_dir):
    try:
        # Open the input PDF
        pdf_document = fitz.open(input_pdf_path)

        # Variable to hold the start page of each question
        question_start_page = None
        question_number = 1
        saved_questions = set()  # Track saved question numbers

        # Iterate through each page of the PDF
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            page_text = page.get_text("text").strip()

            # Check if the page contains a line that starts with a number (e.g., "1", "2", etc.)
            if page_text:
                first_line = page_text.splitlines()[0].strip()
                if first_line and first_line[0].isdigit():  # Check if it starts with a digit
                    current_question = int(first_line[0])
                    if current_question in saved_questions:
                        # Skip if the question was already saved
                        continue

                    if question_start_page is not None:
                        # Save the previous question's pages
                        save_question_pdf(pdf_document, question_start_page, page_number - 1, question_number, output_dir)
                        saved_questions.add(question_number)  # Mark this question as saved
                        question_number += 1

                    # Set the start page for the current question
                    question_start_page = page_number

        # Save the last question
        if question_start_page is not None and question_number not in saved_questions:
            save_question_pdf(pdf_document, question_start_page, len(pdf_document) - 1, question_number, output_dir)

        pdf_document.close()
    except Exception as e:
        logger.error(f"Error processing PDF {input_pdf_path}: {e}", exc_info=True)

def save_question_pdf(pdf_document, start_page, end_page, question_number, output_dir):
    try:
        pdf_writer = fitz.open()
        for page_index in range(start_page, end_page + 1):
            pdf_writer.insert_pdf(pdf_document, from_page=page_index, to_page=page_index)

        # Define the full path for saving each question PDF as just "1.pdf", "2.pdf", etc.
        output_pdf_path = os.path.join(output_dir, f"{question_number}.pdf")
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory structure exists

        pdf_writer.save(output_pdf_path)
        pdf_writer.close()
        logger.info(f"Created: {output_pdf_path}")
    except Exception as e:
        logger.error(f"Error saving question PDF {question_number} to {output_dir}: {e}", exc_info=True)

def process_pdf_folder(input_folder, output_base_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            # Parse filename components based on the updated regex
            match = re.match(r"(\d{4})_([wms])(\d{2})_qp_(\d{1,2})_cleaned", filename)
            if match:
                subject_code = match.group(1)
                mapping_code = match.group(2)
                year_suffix = match.group(3)
                paper_number = match.group(4)

                # Determine the year based on the suffix length and value
                if len(year_suffix) == 2:
                    if int(year_suffix) >= 15:
                        year = f"20{year_suffix}"  # Assume 2000s for 15 or above
                    else:
                        year = f"20{year_suffix}"  # Assume 2000s for 00 to 14
                else:
                    year = year_suffix  # Use the full four-digit year if provided

                mapping = mapping_dict.get(mapping_code, "Unknown_Mapping")
                
                # Define output directory structure
                output_dir = os.path.join(output_base_folder, subject_code, year, mapping, paper_number)

                # Split and save the questions
                input_pdf_path = os.path.join(input_folder, filename)
                split_pdf_into_questions(input_pdf_path, output_dir)
            else:
                logger.warning(f"Filename format not recognized: {filename}")

# Example usage
input_folder = "output_cleaned"  # Folder containing PDFs to process
output_base_folder = "output_questions"  # Base folder for saving split PDFs

process_pdf_folder(input_folder, output_base_folder)
