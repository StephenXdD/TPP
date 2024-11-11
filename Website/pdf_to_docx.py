import os
from pdf2docx import Converter
from docx import Document
from docx.shared import Pt  # For setting font size

def pdf_to_docx_bulk(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Loop through all PDF files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_file = os.path.join(input_folder, filename)
            docx_file = os.path.join(output_folder, filename.replace('.pdf', '.docx'))
            
            # Convert each PDF to DOCX
            cv = Converter(pdf_file)
            cv.convert(docx_file, start=0, end=None)
            cv.close()
            print(f"Converted {pdf_file} to {docx_file}")
            
            # Set all text to Arial in the DOCX file
            set_font_to_arial(docx_file)
            print(f"Updated font in {docx_file} to Arial")

def set_font_to_arial(docx_file):
    doc = Document(docx_file)
    
    # Iterate over all paragraphs and set the font to Arial
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(11)  # Optional: set font size, e.g., 11 pt
    
    # Save changes
    doc.save(docx_file)

# Path to input folder
input_folder = 'input_pdfs'  # Adjust this to the correct path for your input files

# Path to output folder on Desktop
output_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'trial_output')

# Example usage
pdf_to_docx_bulk(input_folder, output_folder)
