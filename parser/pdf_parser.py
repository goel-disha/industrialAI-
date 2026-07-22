"""
Reads every PDF inside the GX Works export folder
and extracts raw text.
"""

from pathlib import Path
import pdfplumber
from typing import Dict


class PDFReader:
    def __init__(self, folder: str):

        self.folder = Path(folder)

    def read_pdf(self, pdf_path: Path) -> str:
        text = ""

        try:

            with pdfplumber.open(pdf_path) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

        except Exception as e:

            print(f"Error reading {pdf_path.name}: {e}")

        return text

    def read_all(self) -> Dict[str, str]:

        documents = {}

        for pdf in self.folder.glob("*.pdf"):

            documents[pdf.name] = self.read_pdf(pdf)

        return documents


if __name__ == "__main__":

    reader = PDFReader("docs/gxworks_exports")

    docs = reader.read_all()

    print(f"Loaded {len(docs)} PDFs")

    for name, text in docs.items():

        print("=" * 50)

        print(name)

        print(text[:500])
