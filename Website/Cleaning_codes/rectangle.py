from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def draw_rectangles_on_pdf(input_pdf_path, output_pdf_path, height1, height2):
    # Create a temporary PDF to draw rectangles
    temp_pdf_path = "temp_rectangles.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)

    # Get the width and height of the page
    width, height = letter

    # Set the fill and stroke color to white
    c.setFillColorRGB(1, 1, 1)  # White fill
    c.setStrokeColorRGB(1, 1, 1)  # White border

    # Draw the first rectangle starting from the top
    c.rect(0, height - height1, width, height1, fill=1, stroke=1)

    # Draw the second rectangle starting from the bottom
    c.rect(0, 0, width, height2, fill=1, stroke=1)

    c.save()

    # Read the original PDF and the temporary PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Overlay the rectangles on each page of the original PDF
    temp_reader = PdfReader(temp_pdf_path)

    for page in reader.pages:
        page.merge_page(temp_reader.pages[0])
        writer.add_page(page)

    # Write the modified PDF to the output path
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

# Specify the heights for the rectangles
height1 = 470 # Height of the first rectangle (from the top)
height2 = 0 # Height of the second rectangle (from the bottom)

# Input and output PDF file paths
input_pdf_path = "29.pdf"
output_pdf_path = "modified_output.pdf"

# Draw rectangles on the PDF
draw_rectangles_on_pdf(input_pdf_path, output_pdf_path, height1, height2)
