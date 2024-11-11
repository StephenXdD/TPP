import os
import win32com.client

def docx_to_pdf_bulk_win32(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    word = win32com.client.Dispatch('Word.Application')
    processed_files = []
    errors = []

    for root, _, files in os.walk(input_folder):
        for filename in files:
            if filename.lower().endswith('.docx') and not filename.startswith('~$'):
                # Build the full path to the .docx file
                docx_file = os.path.join(root, filename)

                # Preserve the directory structure in the output folder
                relative_path = os.path.relpath(root, input_folder)
                output_dir = os.path.join(output_folder, relative_path)
                os.makedirs(output_dir, exist_ok=True)

                # Build the full path for the .pdf file in the output directory
                pdf_file = os.path.join(output_dir, filename.replace('.docx', '.pdf'))

                try:
                    # Open, convert, and save the document as PDF
                    doc = word.Documents.Open(docx_file)
                    doc.SaveAs(pdf_file, FileFormat=17)  # 17 is the format code for PDF
                    doc.Close()
                    processed_files.append((docx_file, pdf_file))
                    print(f"Converted: {docx_file} to {pdf_file}")
                except Exception as e:
                    errors.append((docx_file, str(e)))
                    print(f"Error converting {docx_file}: {e}")

    word.Quit()

    # Print a summary of the conversion process
    print("\nConversion Summary:")
    print(f"Successfully converted {len(processed_files)} files.")
    if errors:
        print(f"Encountered errors with {len(errors)} files:")
        for error_file, error_message in errors:
            print(f"  - {error_file}: {error_message}")

# Example usage
input_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'trial_output')
output_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'pdf_output')
docx_to_pdf_bulk_win32(input_folder, output_folder)
