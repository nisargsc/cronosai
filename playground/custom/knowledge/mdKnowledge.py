from pathlib import Path
from typing import AsyncIterator, Iterator, List, Union

from pydantic import Field

from agno.document import Document
from agno.knowledge.agent import AgentKnowledge
from custom.knowledge.mdReader import MDReader


class MDKnowledgeBase(AgentKnowledge):
    path: Union[str, Path]

    exclude_files: List[str] = Field(default_factory=list)

    reader: MDReader = MDReader()

    @property
    def document_lists(self) -> Iterator[List[Document]]:
        """Iterate over Markdown files and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        _md_path: Path = Path(self.path) if isinstance(self.path, str) else self.path

        if _md_path.exists() and _md_path.is_dir():
            for _md in _md_path.glob("**/*.md"):
                if _md.name in self.exclude_files:
                    continue
                yield self.reader.read(md_file=_md)
        elif _md_path.exists() and _md_path.is_file() and _md_path.suffix == ".md":
            if _md_path.name in self.exclude_files:
                return
            yield self.reader.read(md_file=_md_path)

    @property
    async def async_document_lists(self) -> AsyncIterator[List[Document]]:
        """Iterate over Markdown files and yield lists of documents.
        Each object yielded by the iterator is a list of documents.

        Returns:
            Iterator[List[Document]]: Iterator yielding list of documents
        """

        _md_path: Path = Path(self.path) if isinstance(self.path, str) else self.path

        if _md_path.exists() and _md_path.is_dir():
            for _md in _md_path.glob("**/*.md"):
                if _md.name in self.exclude_files:
                    continue
                yield await self.reader.async_read(md_file=_md)
        elif _md_path.exists() and _md_path.is_file() and _md_path.suffix == ".md":
            if _md_path.name in self.exclude_files:
                return
            yield await self.reader.async_read(md_file=_md_path)