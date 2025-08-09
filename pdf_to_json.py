import os
from pdf2image import convert_from_path
import pytesseract

PDF_FOLDER = "pdfs"
OUTPUT_FOLDER = "output_txt"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def pdf_to_txt(pdf_path: str, output_folder: str) -> None:
    """Convert a PDF to text files using OCR, one TXT per page."""
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"ERROR converting {pdf_path}: {e}")
        return

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    for i, img in enumerate(images, start=1):
        try:
            text = pytesseract.image_to_string(img, lang='eng')
            output_path = os.path.join(output_folder, f"{base_name}_page_{i}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print(f"ERROR processing page {i} of {pdf_path}: {e}")
    print(f"OCR completed for: {pdf_path}")

if __name__ == "__main__":
    pdfs_processed = 0
    for filename in os.listdir(PDF_FOLDER):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(PDF_FOLDER, filename)
            pdf_to_txt(pdf_path, OUTPUT_FOLDER)
            pdfs_processed += 1
    print(f"Total PDFs processed: {pdfs_processed}")
