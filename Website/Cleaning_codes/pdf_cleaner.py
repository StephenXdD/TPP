import fitz  # PyMuPDF

def remove_headers_footers_and_specific_pages(input_pdf, output_pdf, texts_to_remove, footer_text, blank_page_text="BLANK PAGE", header_height=50):
    # Open the input PDF
    pdf_document = fitz.open(input_pdf)
    
    # Remove the first page
    if len(pdf_document) > 0:
        pdf_document.delete_page(0)  # Delete the first page (page index 0)

    pages_to_delete = []

    # Process each page to remove headers and mark pages for deletion
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        
        # Define the top area (header area) where page numbers or headers might be located
        page_width, page_height = page.rect.width, page.rect.height
        header_rect = fitz.Rect(0, 0, page_width, header_height)

        # Redact content in the header area
        header_text_instances = page.get_text("blocks")
        for block in header_text_instances:
            x0, y0, x1, y1, _, text, _ = block
            if y1 <= header_height:
                page.add_redact_annot(fitz.Rect(x0, y0, x1, y1))

        # Apply redactions to remove header content
        page.apply_redactions()

        # Check if "BLANK PAGE" remains after removing headers
        page_text = page.get_text("text").upper()
        if blank_page_text in page_text:
            pages_to_delete.append(page_number)

        # Check for pages containing "question begins on page"
        if "BEGINS ON PAGE" in page_text.upper():
            pages_to_delete.append(page_number)
        
        # Check for pages containing "Additional Page"
        if "ADDITIONAL PAGE" in page_text.upper():
            pages_to_delete.append(page_number)

    # Delete pages marked for deletion, starting from the last to avoid reindexing issues
    for page_number in reversed(pages_to_delete):
        pdf_document.delete_page(page_number)

    # Remove specific text instances across all remaining pages
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        
        for text in texts_to_remove:
            text_instances = page.search_for(text)
            for rect in text_instances:
                page.add_redact_annot(rect)
            page.apply_redactions()

    # Remove footer and line on the last page
    if len(pdf_document) > 0:
        last_page = pdf_document[-1]
        
        # Search for the specific footer text on the last page
        footer_text_instances = last_page.search_for(footer_text)
        if footer_text_instances:
            footer_rect = footer_text_instances[0]
            footer_y0 = footer_rect.y0  # Top y-coordinate of the footer text

            # Expand the redaction rectangle slightly above the footer text to include the line
            line_offset = 15  # Adjust as needed to cover the line just above the footer text
            redaction_rect = fitz.Rect(0, footer_y0 - line_offset, page_width, page_height)
            last_page.add_redact_annot(redaction_rect)

            # Apply redactions to remove the footer and the line
            last_page.apply_redactions()
    
    # Save the modified PDF to the specified output path
    pdf_document.save(output_pdf)
    pdf_document.close()

# Example usage
input_pdf_path = "30.pdf"  # Path to your input PDF
output_pdf_path = "30temp.pdf"  # Path for saving the output PDF

# List of texts to remove
texts_to_remove = [
    "www.dynamicpapers.com", "[Turn over", "© UCLES 2024", "9709/12/ M/J/24", "9709/12/M/J/24", 
    "[Turn over ", "9709/12/M/J/24", "DO NOT WRITE IN THIS MARGIN", "Question 6 continues on the next page."
]

# Specific footer text on the last page
footer_text = ("Permission to reproduce items where third-party owned material protected by copyright is "
               "included has been sought and cleared where possible.")

remove_headers_footers_and_specific_pages(input_pdf_path, output_pdf_path, texts_to_remove, footer_text)
print(f"First page, headers, 'BLANK PAGE' pages, 'ADDITIONAL PAGE' pages, specified text instances, and footer with line on the last page removed. Saved as: {output_pdf_path}")
