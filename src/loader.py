from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

def load_pdf(file_path: str) -> list[Document]:
    """
    Load a PDF file and return a list of Document objects.
    One Document per page, not one for the whole file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        list[Document]: A list of Document objects.
    """
    loader = PyPDFLoader(file_path)
    
    return loader.load()