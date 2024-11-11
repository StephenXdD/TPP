import PyPDF2

def extract_all_text(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)
        
        # Initialize to store the full text
        full_text = ""
        
        # Loop through all pages and extract text
        for page_num in range(total_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            full_text += text  # Append text of the current page
        
        return full_text

# Example usage
pdf_path = "9706_s07_qp_2_cleaned.pdf"
pdf_text = extract_all_text(pdf_path)

# Print the full text of the PDF
print(pdf_text)
