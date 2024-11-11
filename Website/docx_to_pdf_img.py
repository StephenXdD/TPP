import os
import win32com.client

def docx_to_pdf_bulk_win32(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    word = win32com.client.Dispatch('Word.Application')
    processed_files = []
    errors = []

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.docx') and not filename.startswith('~$'):
            docx_file = os.path.join(input_folder, filename)
            pdf_file = os.path.join(output_folder, filename.replace('.docx', '.pdf'))

            try:
                doc = word.Documents.Open(docx_file)
                doc.SaveAs(pdf_file, FileFormat=17)  # 17 is the format code for PDF
                doc.Close()
                processed_files.append((docx_file, pdf_file))
                print(f"Converted: {docx_file} to {pdf_file}")
            except Exception as e:
                errors.append((docx_file, str(e)))
                print(f"Error converting {docx_file}: {e}")

    word.Quit()

    print("\nConversion Summary:")
    print(f"Successfully converted {len(processed_files)} files.")
    if errors:
        print(f"Encountered errors with {len(errors)} files:")
        for error_file, error_message in errors:
            print(f"  - {error_file}: {error_message}")

# Example usage
if __name__ == "__main__":
    input_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'trial_output')
    output_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'pdf_output')
    docx_to_pdf_bulk_win32(input_folder, output_folder)
