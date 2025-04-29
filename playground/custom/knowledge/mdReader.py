from agno.document.reader.base import Reader
from agno.document.base import Document
from typing import List, Any, Union, IO
import os
from pathlib import Path


class MDReader(Reader):
    """Markdown reader that reads markdown documents from a file path"""

    def __init__(self, chunk: bool = True, chunk_size: int = 3000, **kwargs):
        super().__init__(chunk=chunk, chunk_size=chunk_size, **kwargs)

    def read(self, md_file: Union[str, Path, IO[Any]]) -> List[Document]:
        """
        Read a Markdown file and convert it to a list of Documents.
        
        Args:
            md_file: Path to the Markdown file to read, can be a string path, Path object, or file-like object.
            
        Returns:
            A list of Document objects containing the Markdown content.
        """
        if isinstance(md_file, str) and not os.path.exists(md_file):
            raise FileNotFoundError(f"Markdown file not found: {md_file}")
        
        try:
            # Get document name for metadata
            if isinstance(md_file, str):
                doc_name = os.path.basename(md_file).split(".")[0].replace(" ", "_")
            elif isinstance(md_file, Path):
                doc_name = md_file.name.split(".")[0].replace(" ", "_")
            else:
                doc_name = getattr(md_file, 'name', 'md').split(".")[0].replace(" ", "_")
                
            # Read the Markdown file
            if isinstance(md_file, (str, Path)):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = md_file.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
            
            # Create a Document object for the markdown content
            document = Document(
                name=doc_name,
                id=f"{doc_name}_content",
                meta_data={"file": doc_name},
                content=content
            )
            
            documents = [document]
            
            # Chunk the documents if needed
            if self.chunk:
                return self._build_chunked_documents(documents)
            
            return documents
        
        except Exception as e:
            raise Exception(f"Failed to read Markdown file: {str(e)}")

    def _build_chunked_documents(self, documents: List[Document]) -> List[Document]:
        """Helper method to chunk a list of documents"""
        chunked_documents: List[Document] = []
        for document in documents:
            chunked_documents.extend(self.chunk_document(document))
        return chunked_documents

    async def async_read(self, md_file: Union[str, Path, IO[Any]]) -> List[Document]:
        """
        Asynchronously read a Markdown file.
        
        Args:
            md_file: Path to the Markdown file to read.
            
        Returns:
            A list of Document objects containing the Markdown content.
        """
        import asyncio
        return await asyncio.to_thread(self.read, md_file)