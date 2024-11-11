import os
from pdf2docx import Converter
from docx import Document
from docx.shared import Pt  # For setting font size

def pdf_to_docx_bulk(input_base_folder, output_base_folder):
    # Traverse through all subdirectories to find PDF files
    for root, _, files in os.walk(input_base_folder):
        for filename in files:
            if filename.endswith('.pdf'):
                # Full path to the PDF file
                pdf_file = os.path.join(root, filename)
                
                # Determine the relative path within the `input_base_folder`
                relative_path = os.path.relpath(root, input_base_folder)
                
                # Create the corresponding output path
                output_folder = os.path.join(output_base_folder, relative_path)
                os.makedirs(output_folder, exist_ok=True)
                
                # Define the DOCX file path
                docx_file = os.path.join(output_folder, filename.replace('.pdf', '.docx'))
                
                # Convert PDF to DOCX
                cv = Converter(pdf_file)
                cv.convert(docx_file, start=0, end=None)
                cv.close()
                print(f"Converted {pdf_file} to {docx_file}")
                
                # Set all text in the DOCX file to Arial
                set_font_to_arial(docx_file)
                print(f"Updated font in {docx_file} to Arial")

def set_font_to_arial(docx_file):
    # Open the DOCX file
    doc = Document(docx_file)
    
    # Iterate over all paragraphs and set the font to Arial
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(11)  # Set font size to 11 pt
    
    # Save changes to DOCX file
    doc.save(docx_file)

# Paths
input_base_folder = 'temp_output_questions'  # Starting folder with PDFs to convert
output_base_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'trial_output')

# Execute the bulk conversion
pdf_to_docx_bulk(input_base_folder, output_base_folder)
