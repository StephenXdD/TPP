import fitz  # PyMuPDF
import os
import re

def map_mapping_to_description(mapping):
    """Map the short mapping code to its full description."""
    mapping_dict = {
        'w': 'Oct_Nov',
        's': 'May_June',
        'm': 'Feb_March'
    }
    return mapping_dict.get(mapping, mapping)

def split_pdf(pdf_path, duplicates):
    # Extract the filename details
    filename = os.path.basename(pdf_path)
    match = re.match(r'(\d{4})_(w|s|m)(\d{2})_qp_(\d{1,2})_cleaned\.pdf', filename)

    if not match:
        raise ValueError(f"Filename format is incorrect for {filename}.")

    subject_code = match.group(1)
    mapping = match.group(2)
    year = '20' + match.group(3)
    paper_number = match.group(4)

    # Create output directory structure
    mapping_description = map_mapping_to_description(mapping)
    output_dir = os.path.join('temp_output_questions', subject_code, year, mapping_description, paper_number)
    os.makedirs(output_dir, exist_ok=True)

    # Open the PDF document
    print(f"Opening PDF: {pdf_path}")
    document = fitz.open(pdf_path)

    # Check the total number of pages
    page_count = len(document)
    print(f"Total pages: {page_count}")
    
    if page_count != len(duplicates):
        raise ValueError(f"Number of pages ({page_count}) does not match the length of duplicates list ({len(duplicates)}).")

    current_pdf_index = 1

    for page_num in range(page_count):
        print(f"Duplicating page {page_num + 1}...")
        for _ in range(duplicates[page_num]):  # Duplicate the page according to the specified number
            new_pdf_path = os.path.join(output_dir, f"{current_pdf_index}.pdf")
            new_pdf = fitz.open()  # Create a new PDF document
            new_pdf.insert_page(-1)  # Insert an empty page
            new_pdf[-1].show_pdf_page(new_pdf[-1].rect, document, page_num)  # Copy the content of the original page
            new_pdf.save(new_pdf_path)  # Save the new PDF
            new_pdf.close()
            print(f"Saved duplicated page as {new_pdf_path}")
            current_pdf_index += 1

    document.close()

def process_bulk_pdfs(input_directory, duplicates):
    """Process all PDF files in the input directory."""
    print(f"Processing PDFs in directory: {input_directory}")
    for filename in os.listdir(input_directory):
        if filename.endswith("_cleaned.pdf"):
            pdf_path = os.path.join(input_directory, filename)
            try:
                print(f"Processing {filename}...")
                split_pdf(pdf_path, duplicates)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Example usage
input_directory = "output_cleaned_4"  # Change to your input directory

# Specify how many copies for each page (e.g., for 10 pages: [4, 2, 3, 5, 2, 1, 3, 4, 2, 1])
duplicates = [4, 3, 3, 3, 3, 3, 4, 3, 2, 2]  # Change these values as needed for your 10 pages
process_bulk_pdfs(input_directory, duplicates)
