import json
import os
from datetime import datetime
from typing import List

import numpy as np

from ..config import settings
from ..utils.extract import detect_and_extract
from ..utils.text import chunk_text, sha256_bytes
from .embeddings import EmbeddingService
from .index import ChunkRecord, ProjectIndex


class IngestService:
    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service

    def ingest_file(self, project_dir: str, filename: str, file_bytes: bytes) -> dict:
        project_index = ProjectIndex(project_dir, self.embedding_service.model.get_sentence_embedding_dimension())
        sources = project_index.get_sources()
        file_hash = sha256_bytes(file_bytes)
        for source in sources:
            if source.get("hash") == file_hash:
                return {"status": "duplicate", "source_id": source["id"]}
        extracted_pages = detect_and_extract(filename, file_bytes)
        if not extracted_pages:
            return {"status": "unsupported", "filename": filename}
        source_id = project_index.next_source_id()
        source_entry = {
            "id": source_id,
            "filename": filename,
            "hash": file_hash,
            "pages": len(extracted_pages),
            "created_at": datetime.utcnow().isoformat(),
        }
        sources.append(source_entry)
        project_index.save_sources(sources)

        records: List[ChunkRecord] = []
        for page_number, text in extracted_pages:
            for chunk in chunk_text(text):
                records.append(
                    ChunkRecord(
                        chunk_id=project_index.next_chunk_id() + len(records),
                        source_id=source_id,
                        page=page_number,
                        text=chunk,
                        filename=filename,
                    )
                )
        if not records:
            return {"status": "empty", "filename": filename}
        texts = [record.text for record in records]
        embeddings = self.embedding_service.embed(texts)
        project_index.append_chunks(records, embeddings)
        return {"status": "indexed", "source_id": source_id, "chunks": len(records)}


class ProjectManager:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def list_projects(self) -> List[dict]:
        projects = []
        for name in sorted(os.listdir(self.data_dir)):
            path = os.path.join(self.data_dir, name)
            if os.path.isdir(path):
                projects.append({"id": name})
        return projects

    def create_project(self, name: str) -> dict:
        project_id = name.strip().lower().replace(" ", "-")
        project_dir = os.path.join(self.data_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        meta_path = os.path.join(project_dir, "project.json")
        if not os.path.exists(meta_path):
            with open(meta_path, "w", encoding="utf-8") as handle:
                json.dump({"id": project_id, "name": name}, handle, indent=2)
        return {"id": project_id, "name": name}

    def project_dir(self, project_id: str) -> str:
        return os.path.join(self.data_dir, project_id)
