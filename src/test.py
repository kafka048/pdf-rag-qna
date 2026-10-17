from loader import load_pdf


## TESTING THE LOADER AND THE DOCUMENTS STRUCTURE AND THE CONTENT

file_path = "data/nandpur_water_security_handbook.pdf"

documents = load_pdf(file_path)

print(f"1. Loaded {len(documents)} documents.") # Print the number of documents loaded
print(f"2. Second document content \n: {documents[1].page_content[:500]}")  # Print first 500 characters of the first document
print(f"3. Second documment content length \n: {len(documents[1].page_content)}")  # Print length of the first document's content
print(f"4. Second document content \n: {documents[1].page_content}")  # Print full content of the second document
print(f"5. Second document metadata \n: {documents[1].metadata}")  # Print metadata of the first document
print(f"6. Second document page number \n: {documents[1].metadata.get('page_label', 'N/A')}")  # Print page number of the second document, if not available, print 'N/A'