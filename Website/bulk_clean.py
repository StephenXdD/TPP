import fitz  # PyMuPDF
import os
import re

# Define the mapping for month abbreviations
mapping = {
    's': 'M/J',  # Mapping for 's'
    'm': 'F/M',  # Mapping for 'm'
    'w': 'O/N'   # Mapping for 'w'
}

def get_texts_to_remove(file_name):
    base_texts_to_remove = [
        "www.dynamicpapers.com", 
        "[Turn over", 
        "[Turn over ", 
        "DO NOT WRITE IN THIS MARGIN",
        "[Total: 30]",  # Add the text to remove
        "[Total: 15]",
        "06_9706_12_2024_1.13b",
        "Answer all the questions in the spaces provided."
          # This is the previously handled case
    ]
    
    # Extract parts of the file name to construct dynamic text
    match = re.match(r"(\d+)_([smw])(\d+)_qp_(\d+)", file_name)
    if match:
        paper_code = match.group(1)
        letter = match.group(2)
        year_suffix = match.group(3)
        paper_number = match.group(4)

        # Ensure paper_number and year_suffix are two digits, add leading zero if necessary
        paper_number = paper_number.zfill(2)  # Add leading zero to paper number if needed
        year_suffix = year_suffix.zfill(2)  # Add leading zero to year suffix if needed

        # Construct dynamic text formats
        dynamic_text_with_slash = f"{paper_code}/{paper_number}/{mapping.get(letter, '')}/{year_suffix}"
        dynamic_text_without_slash = f"{paper_code}_{paper_number}_{mapping.get(letter, '')}{year_suffix}"
        copyright_year = f"© UCLES 20{year_suffix}"

        # Add pattern for "9706/02/M/J04" (without the final slash) as per request
        dynamic_text_no_slash_final = f"{paper_code}/{paper_number}/{mapping.get(letter, '')}{year_suffix}"

        # Dynamically add 9706/2/M/J/02 to the list of text to remove for any matching file
        dynamic_text_generic = f"{paper_code}/{paper_number}/{mapping.get(letter, '')}/{year_suffix}"

        return base_texts_to_remove + [
            copyright_year, 
            dynamic_text_with_slash, 
            dynamic_text_without_slash,
            dynamic_text_no_slash_final,  # Newly added static pattern for removal
            dynamic_text_generic  # Add this dynamic pattern that works for any year/paper_number mapping
        ]
    
    return base_texts_to_remove

def remove_headers_footers_and_specific_pages(input_pdf, output_pdf, texts_to_remove, blank_page_text="BLANK PAGE", header_height=38):
    pdf_document = fitz.open(input_pdf)
    
    if len(pdf_document) > 0:
        pdf_document.delete_page(0)  # Remove the first page

    pages_to_delete = []

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        page_width = page.rect.width

        # Mark pages for deletion based on specific text conditions
        page_text = page.get_text("text").upper()
        if blank_page_text in page_text or "BEGINS ON PAGE" in page_text or "ADDITIONAL PAGE" in page_text:
            pages_to_delete.append(page_number)
        elif "IS ON THE NEXT PAGE." in page_text:
            pages_to_delete.append(page_number)
        if "PLEASE TURN OVER" in page_text:
            pages_to_delete.append(page_number)

        # Redact any text within the header area at the top of each page
        header_area = fitz.Rect(0, 0, page_width, header_height)  # Top 50 units of the page
        for block in page.get_text("blocks"):
            x0, y0, x1, y1, text = block[:5]
            if header_area.intersects(fitz.Rect(x0, y0, x1, y1)):
                page.add_redact_annot(fitz.Rect(x0, y0, x1, y1))

        # Redact only specific words exactly as spelled with matching cases
        case_sensitive_words = ["For", "Examiner's", "Use"]
        for word in case_sensitive_words:
            for instance in page.search_for(word):
                matched_text = page.get_text("text", clip=instance)
                if matched_text.strip() == word:
                    page.add_redact_annot(instance)
        
        # Redact other texts in texts_to_remove, case-insensitive as per usual
        for text in texts_to_remove:
            for rect in page.search_for(text, quads=True):
                page.add_redact_annot(rect)
        
        page.apply_redactions()  # Apply all redactions for this page

    # Delete unwanted pages in reverse order
    for page_number in reversed(pages_to_delete):
        pdf_document.delete_page(page_number)

    # Handle the last page to remove everything below 150 points from the bottom of the page
    if len(pdf_document) > 0:
        last_page = pdf_document[-1]

        # Remove any horizontal line above the footer text
        rects = last_page.get_text("blocks")
        for block in rects:
            if len(block) >= 5:
                x0, y0, x1, y1, _, text, _ = block
                if (y0 > last_page.rect.height - 60) and (y1 - y0 < 5):  # Height threshold for a line
                    last_page.add_redact_annot(fitz.Rect(x0, y0, x1, y1))

        # Remove everything from the bottom of the last page that is below 150 points
        bottom_y = last_page.rect.height
        cutoff_y = bottom_y - 160
        last_page.add_redact_annot(fitz.Rect(0, cutoff_y, last_page.rect.width, bottom_y))  # Redact everything below cutoff_y

        last_page.apply_redactions()  # Apply all redactions for the last page

    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    pdf_document.save(output_pdf)
    pdf_document.close()

# Bulk processing
input_directory = "input_pdfs"
output_directory = "output_cleaned"

for file_name in os.listdir(input_directory):
    if file_name.endswith(".pdf"):
        input_pdf_path = os.path.join(input_directory, file_name)
        output_pdf_path = os.path.join(output_directory, f"{file_name.replace('.pdf', '_cleaned.pdf')}")

        texts_to_remove = get_texts_to_remove(file_name)
        remove_headers_footers_and_specific_pages(input_pdf_path, output_pdf_path, texts_to_remove)

print("Bulk cleaning completed.")
