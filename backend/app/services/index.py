import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from ..utils.text import clean_text


@dataclass
class ChunkRecord:
    chunk_id: int
    source_id: int
    page: int
    text: str
    filename: str


class ProjectIndex:
    def __init__(self, project_dir: str, embedding_dim: int) -> None:
        self.project_dir = project_dir
        self.embedding_dim = embedding_dim
        self.index_path = os.path.join(project_dir, "index.faiss")
        self.chunks_path = os.path.join(project_dir, "chunks.jsonl")
        self.sources_path = os.path.join(project_dir, "sources.json")
        self._faiss = None
        self._chunks: List[ChunkRecord] = []
        self._bm25 = None

    @property
    def chunks(self) -> List[ChunkRecord]:
        if not self._chunks:
            self._chunks = self._load_chunks()
        return self._chunks

    @property
    def bm25(self) -> BM25Okapi:
        if self._bm25 is None:
            corpus = [clean_text(c.text).split() for c in self.chunks]
            self._bm25 = BM25Okapi(corpus) if corpus else BM25Okapi([[]])
        return self._bm25

    @property
    def faiss_index(self) -> faiss.IndexFlatIP:
        if self._faiss is None:
            if os.path.exists(self.index_path):
                self._faiss = faiss.read_index(self.index_path)
            else:
                self._faiss = faiss.IndexFlatIP(self.embedding_dim)
        return self._faiss

    def _load_chunks(self) -> List[ChunkRecord]:
        chunks = []
        if not os.path.exists(self.chunks_path):
            return chunks
        with open(self.chunks_path, "r", encoding="utf-8") as handle:
            for line in handle:
                data = json.loads(line)
                chunks.append(
                    ChunkRecord(
                        chunk_id=data["chunk_id"],
                        source_id=data["source_id"],
                        page=data["page"],
                        text=data["text"],
                        filename=data["filename"],
                    )
                )
        return chunks

    def save_faiss(self) -> None:
        if self._faiss is not None:
            faiss.write_index(self._faiss, self.index_path)

    def append_chunks(self, records: List[ChunkRecord], embeddings: np.ndarray) -> None:
        os.makedirs(self.project_dir, exist_ok=True)
        with open(self.chunks_path, "a", encoding="utf-8") as handle:
            for record in records:
                handle.write(
                    json.dumps(
                        {
                            "chunk_id": record.chunk_id,
                            "source_id": record.source_id,
                            "page": record.page,
                            "text": record.text,
                            "filename": record.filename,
                        }
                    )
                    + "\n"
                )
        self._chunks.extend(records)
        if embeddings.size:
            self.faiss_index.add(embeddings)
            self.save_faiss()
            self._bm25 = None

    def search(self, query: str, query_vec: np.ndarray, top_k: int = 8) -> List[Tuple[ChunkRecord, float]]:
        results: Dict[int, float] = {}
        if self.chunks:
            scores = self.bm25.get_scores(clean_text(query).split())
            top_bm = np.argsort(scores)[::-1][:top_k]
            for idx in top_bm:
                results[int(idx)] = max(results.get(int(idx), 0), float(scores[idx]))
        if self.faiss_index.ntotal > 0:
            faiss_scores, faiss_idx = self.faiss_index.search(query_vec, top_k)
            for score, idx in zip(faiss_scores[0], faiss_idx[0]):
                if idx == -1:
                    continue
                results[int(idx)] = max(results.get(int(idx), 0), float(score))
        ranked = sorted(results.items(), key=lambda item: item[1], reverse=True)[:top_k]
        return [(self.chunks[idx], score) for idx, score in ranked]

    def get_sources(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.sources_path):
            return []
        with open(self.sources_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def save_sources(self, sources: List[Dict[str, str]]) -> None:
        os.makedirs(self.project_dir, exist_ok=True)
        with open(self.sources_path, "w", encoding="utf-8") as handle:
            json.dump(sources, handle, indent=2)

    def next_chunk_id(self) -> int:
        return len(self.chunks) + 1

    def next_source_id(self) -> int:
        sources = self.get_sources()
        return len(sources) + 1
