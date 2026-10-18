from typing import Literal
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document

def split_documents_recursive(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[Document]:
    """
    Split a list of Document objects into smaller chunks using RecursiveCharacterTextSplitter.

    Args:
        documents (list[Document]): A list of Document objects to be split. Each document object is a single page of the PDF.
        chunk_size (int): The maximum size of each chunk. Default is 1000 characters.
        chunk_overlap (int): The number of characters to overlap between chunks. Default is 200 characters.

    Returns:
        list[Document]: A list of Document objects after splitting.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    split_docs: list[Document] = []
    for doc in documents:
        # Split the document into chunks
        chunks: list[str] = text_splitter.split_text(doc.page_content)

        
        # Create new Document objects for each chunk with the same metadata as the original document with an additonal 
        # metadata field "chunk_index" to indicate the index of the chunk
        for i, chunk in enumerate(chunks):
            new_doc = Document(
                page_content=chunk,
                metadata={**doc.metadata, "chunk_index": i} # **doc.metadata: copies all key-value pairs from doc.metadata and adds a new key-value pair "chunk_index": i 
                # to append it to the metadata of the new chunked documents
            )
            split_docs.append(new_doc)        
        
    
    return split_docs


def split_texts_semantic(documents: list[Document], embedding_model: HuggingFaceEmbeddings, breakpoint_threshold_type: Literal[
        "percentile", "standard_deviation", "interquartile", "gradient"
    ] = "percentile",
    breakpoint_threshold_amount: float = 95) -> list[Document]:
    text_splitter = SemanticChunker(embeddings=embedding_model, breakpoint_threshold_type=breakpoint_threshold_type, breakpoint_threshold_amount=breakpoint_threshold_amount)

    split_docs: list[Document] = []

    for doc in documents:
        # split the page into chunks, which returns a list of plain strings
        raw_chunks: list[str] = text_splitter.split_text(doc.page_content)

        # keep only chunks that have real text, so blank ones are never stored
        chunks: list[str] = []
        for c in raw_chunks:
            if c.strip():  # check if the chunk is not empty or just whitespace
                chunks.append(c)       

        for i, chunk in enumerate(chunks):
            new_document = Document(
                page_content=chunk,
                metadata={**doc.metadata, "chunk_index": i}
            )
            split_docs.append(new_document)

    return split_docs
