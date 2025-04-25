from agno.document.reader.base import Reader
from agno.document.base import Document
from typing import List, Any, Union, IO
import fitz  # PyMuPDF
import os
from pathlib import Path


class PDFReader(Reader):
    """PDF reader that reads PDF documents from a file path"""

    def __init__(self, chunk: bool = True, chunk_size: int = 3000, **kwargs):
        super().__init__(chunk=chunk, chunk_size=chunk_size, **kwargs)

    def read(self, pdf: Union[str, Path, IO[Any]]) -> List[Document]:
        """
        Read a PDF file and convert it to a list of Documents.
        
        Args:
            pdf: Path to the PDF file to read, can be a string path, Path object, or file-like object.
            
        Returns:
            A list of Document objects containing the PDF content.
        """
        if isinstance(pdf, str) and not os.path.exists(pdf):
            raise FileNotFoundError(f"PDF file not found: {pdf}")
        
        try:
            # Get document name for metadata
            if isinstance(pdf, str):
                doc_name = os.path.basename(pdf).split(".")[0].replace(" ", "_")
            elif isinstance(pdf, Path):
                doc_name = pdf.name.split(".")[0].replace(" ", "_")
            else:
                doc_name = getattr(pdf, 'name', 'pdf').split(".")[0].replace(" ", "_")
                
            # Open the PDF file
            doc = fitz.open(pdf)
            
            documents = []
            # Process each page and create a Document for it
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                content = page.get_text()
                
                # Create a Document object for each page
                document = Document(
                    name=doc_name,
                    id=f"{doc_name}_{page_num+1}",
                    meta_data={"page": page_num+1},
                    content=content
                )
                documents.append(document)
            
            # Close the PDF
            doc.close()
            
            # Chunk the documents if needed
            if self.chunk:
                return self._build_chunked_documents(documents)
            
            return documents
        
        except Exception as e:
            raise Exception(f"Failed to read PDF file: {str(e)}")

    def _build_chunked_documents(self, documents: List[Document]) -> List[Document]:
        """Helper method to chunk a list of documents"""
        chunked_documents: List[Document] = []
        for document in documents:
            chunked_documents.extend(self.chunk_document(document))
        return chunked_documents

    async def async_read(self, pdf: Union[str, Path, IO[Any]]) -> List[Document]:
        """
        Asynchronously read a PDF file.
        
        Args:
            pdf: Path to the PDF file to read.
            
        Returns:
            A list of Document objects containing the PDF content.
        """
        import asyncio
        return await asyncio.to_thread(self.read, pdf)