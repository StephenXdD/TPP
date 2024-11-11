from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def draw_rectangles_on_pdf(input_pdf_path, output_pdf_path):
    # Determine the question number from the filename
    question_number = input_pdf_path.split('.')[0]  # Get the number from the filename (e.g., '1' from '1.pdf')

    # Create a temporary PDF to draw rectangles
    temp_pdf_path = "temp_rectangles.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)

    # Read the original PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Initialize variables for the rectangle positions
    top_y = None
    bottom_y = None
    page_height = letter[1]  # Use letter page height directly

    # Flag to determine if we found the correct question number
    found_question = False

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                # Check if the line is a standalone digit representing the question number
                if line.strip() == question_number:
                    # Found the question number
                    found_question = True

                    # Get the starting position of the question
                    bottom_y = (len(lines) - i) * 12  # Calculate the bottom position (12 is approx line height)

                    # Set top_y to the position before the question starts
                    if i > 0:  # Check if there is a line above
                        top_y = (len(lines) - (i + 1)) * 12
                    else:
                        top_y = page_height  # If it's the first line, set it to the page height

                    print(f"Question {question_number} found at top: {top_y}, bottom: {bottom_y}")
                    break  # Exit the inner loop after finding the question number

                # If we already found the question, check for the next question
                if found_question and line.strip().isdigit():
                    next_question_number = line.strip()
                    if int(next_question_number) > int(question_number):
                        break  # Stop if we encounter a higher question number

        if found_question:
            break  # Break the outer loop if the question has been found

    # Ensure we found both top and bottom positions before drawing
    if top_y is not None and bottom_y is not None:
        # Set the fill and stroke color to black for debugging
        c.setFillColorRGB(0, 0, 0)  # Black fill
        c.setStrokeColorRGB(0, 0, 0)  # Black border

        # Draw the top rectangle covering everything above the question
        c.rect(0, top_y, letter[0], page_height - top_y, fill=1)

        # Draw the bottom rectangle covering everything below the question
        c.rect(0, 0, letter[0], bottom_y, fill=1)
        
        # Save the rectangles on the temporary PDF
        c.showPage()  # Finalize the current page
    else:
        print("Could not determine rectangle positions.")

    c.save()

    # Check if the temporary PDF was created successfully
    temp_reader = PdfReader(temp_pdf_path)
    if not temp_reader.pages:
        print("Error: Temporary PDF was not created correctly or is empty.")
        return

    # Read the temporary PDF and overlay rectangles on the original PDF
    for page in reader.pages:
        page.merge_page(temp_reader.pages[0])
        writer.add_page(page)

    # Write the modified PDF to the output path
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

# Input and output PDF file paths
input_pdf_path = "1.pdf"  # Change this to your specific PDF filename
output_pdf_path = "modified_output.pdf"

# Draw rectangles on the PDF
draw_rectangles_on_pdf(input_pdf_path, output_pdf_path)
