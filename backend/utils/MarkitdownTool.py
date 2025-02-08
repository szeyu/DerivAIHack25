from markitdown import MarkItDown

class MarkItDownConverter:
    def __init__(self):
        # Initialize the MarkItDown converter
        self.converter = MarkItDown()

    def convert_pdf_to_markdown(self, pdf_path: str) -> str:
        """
        Convert a PDF file (specified by its local path) to Markdown.
        
        :param pdf_path: Path to the PDF file.
        :return: The converted Markdown text.
        """
        result = self.converter.convert(pdf_path)
        return result.text_content

# Sample usage
if __name__ == "__main__":
    pdf_file_path = "/home/ssyok/Documents/Hackathons/DerivAIHack25/backend/data/COURSE PLANNING.pdf"  # Replace with the actual path to your PDF
    converter = MarkItDownConverter()
    
    try:
        markdown_text = converter.convert_pdf_to_markdown(pdf_file_path)
        print("Converted Markdown Output:\n")
        print(markdown_text)
    except Exception as e:
        print(f"Error: {e}")
