import pdfkit
import os

def html_to_pdf(html_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    output_pdf = os.path.join(output_dir, "resume.pdf")

    # Convert HTML → PDF using wkhtmltopdf
    pdfkit.from_file(html_path, output_pdf)

    return output_pdf

