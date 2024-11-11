import fitz  # PyMuPDF
import re
import os

def detect_all_questions(input_pdf, total_questions=30):
    # Open the PDF file
    pdf_document = fitz.open(input_pdf)

    # Define pattern to match question numbers at the start of a line (e.g., "1", "2", etc.)
    question_pattern = re.compile(r'^(\d+)\s')  # Capture question number at line start
    left_margin_limit = 56.7  # 2 cm in points

    found_questions = {}  # Dictionary to store found questions {question_number: (page_num, start_position, end_position)}
    questions_per_page = {}  # Dictionary to count questions on each page

    # Primary scan: Look for questions within the left margin and matching the question pattern
    def primary_scan():
        last_found_question = 0  # Track the last found question number
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            page_text_blocks = page.get_text("blocks")  # Get text blocks with positions
            questions_per_page[page_num] = 0  # Initialize question count for the page

            # Process each block to identify question numbers within the 2 cm margin
            for i, block in enumerate(page_text_blocks):
                bbox, text = block[:4], block[4].strip()  # Extract bounding box and clean text
                if bbox[0] <= left_margin_limit:
                    match = re.match(question_pattern, text)
                    if match:
                        question_number = int(match.group(1))
                        # Ensure questions are detected in the correct order
                        if question_number != last_found_question + 1:
                            continue
                        # Add the question only if it hasn't been found
                        if question_number not in found_questions:
                            found_questions[question_number] = (page_num, bbox, bbox)  # Store start and end as the same for simplicity
                            questions_per_page[page_num] += 1  # Increment question count for the page
                            last_found_question = question_number  # Update last found question

    # Helper function to locate missing questions within expected ranges
    def search_for_gaps():
        last_found_question = max(found_questions.keys(), default=0)  # Get the last found question
        missing_questions = set(range(1, total_questions + 1)) - set(found_questions.keys())

        sorted_found = sorted(found_questions.keys())
        for i in range(len(sorted_found) - 1):
            start_question = sorted_found[i]
            end_question = sorted_found[i + 1]
            # Identify any missing questions in the current range
            missing_in_range = [q for q in missing_questions if start_question < q < end_question]
            if missing_in_range:
                start_page = found_questions[start_question][0]
                end_page = found_questions[end_question][0]
                # Search within the specific range of pages
                for question_number in missing_in_range:
                    for page_num in range(start_page, end_page + 1):
                        page = pdf_document[page_num]
                        page_text_blocks = page.get_text("blocks")
                        for i, block in enumerate(page_text_blocks):
                            text = block[4].strip()
                            match = re.match(question_pattern, text)
                            if match:
                                found_question_num = int(match.group(1))
                                # Ensure detected question is in the correct sequence
                                if found_question_num == question_number and found_question_num not in found_questions:
                                    found_questions[found_question_num] = (page_num, block[:4], block[:4])  # Store start and end as the same for simplicity
                                    questions_per_page[page_num] += 1  # Increment question count for the page
                                    break

    # Final extraction-based search for any remaining missing questions
    def extraction_based_search():
        last_found_question = max(found_questions.keys(), default=0)  # Get the last found question
        missing_questions = set(range(1, total_questions + 1)) - set(found_questions.keys())
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            page_text = page.get_text("text")  # Extract full text of the page
            
            # Process each line of the page text
            lines = page_text.splitlines()
            for j, line in enumerate(lines):
                words = line.strip().split()
                if words and words[0].isdigit():
                    question_number = int(words[0])
                    if question_number in missing_questions and question_number not in found_questions:
                        # Ensure detected question is in the correct sequence
                        if question_number != last_found_question + 1:
                            continue
                        found_questions[question_number] = (page_num, (0,0,0,0), (0,0,0,0))  # Store start and end as the same for simplicity
                        questions_per_page[page_num] += 1  # Increment question count for the page
                        last_found_question = question_number  # Update last found question

    # Function to save each question as a new PDF file
    def save_question_as_pdf(index, page_num, subject_code, year, mapping, paper_number):
        # Create a new PDF document
        new_pdf_document = fitz.open()
        # Copy the page from the original PDF to the new PDF
        new_page = new_pdf_document.new_page(width=pdf_document[page_num].rect.width,
                                              height=pdf_document[page_num].rect.height)
        new_page.show_pdf_page(new_page.rect, pdf_document, page_num)

        # Define the output path for the new PDF
        output_directory = os.path.join("temp_output_questions", subject_code, str(year), mapping, str(paper_number))
        os.makedirs(output_directory, exist_ok=True)
        output_path = os.path.join(output_directory, f"{index}.pdf")

        # Save the new PDF
        new_pdf_document.save(output_path)
        new_pdf_document.close()
        print(f"Saved PDF as {output_path}")

    # Extract subject code, year, mapping, and paper number from the input PDF filename
    base_name = os.path.basename(input_pdf)
    match = re.match(r'(\d{4})_(s|w|m)(\d{2})_qp_(\d{1,2})_cleaned\.pdf', base_name)
    if match:
        subject_code, mapping_letter, year_suffix, paper_number = match.groups()
        year = 2000 + int(year_suffix)  # Convert to full year
        mapping = {'s': 'May_June', 'w': 'Oct_Nov', 'm': 'Feb_March'}[mapping_letter]

        # Run the scans in order until all questions are found
        primary_scan()
        if len(found_questions) < total_questions:
            search_for_gaps()
        if len(found_questions) < total_questions:
            extraction_based_search()

        # Save each detected question as a separate PDF
        for index, question_number in enumerate(sorted(found_questions.keys()), start=1):
            page_num, _, _ = found_questions[question_number]
            save_question_as_pdf(index, page_num, subject_code, year, mapping, paper_number)

# Function to process all PDFs in the specified directory
def process_all_pdfs(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            input_pdf = os.path.join(directory, filename)
            detect_all_questions(input_pdf)

# Example usage
input_directory = "output_cleaned"  # Replace with your directory containing PDF files
process_all_pdfs(input_directory)