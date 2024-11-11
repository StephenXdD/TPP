import os

def delete_unwanted_pdfs(base_folder):
    # Define the set of valid filenames from 1.pdf to 40.pdf
    valid_filenames = {f"{i}.pdf" for i in range(1, 41)}

    # Walk through the base folder and all its subdirectories
    for root, dirs, files in os.walk(base_folder):
        for filename in files:
            if filename.endswith(".pdf") and filename not in valid_filenames:
                # Full path to the file
                file_path = os.path.join(root, filename)
                # Delete the file if it's not in the valid set
                os.remove(file_path)
                print(f"Deleted: {file_path}")

# Example usage
output_base_folder = "output_questions"  # The base folder for output
delete_unwanted_pdfs(output_base_folder)
