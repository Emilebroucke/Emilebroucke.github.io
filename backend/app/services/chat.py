from typing import Dict, List

import numpy as np

from ..prompts import FORMAT_RULES, RETRIEVAL_INSTRUCTION, SYSTEM_PROMPT
from .embeddings import EmbeddingService
from .index import ProjectIndex


class ChatService:
    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service

    def retrieve(self, project_dir: str, query: str, top_k: int = 8) -> List[Dict[str, str]]:
        project_index = ProjectIndex(project_dir, self.embedding_service.model.get_sentence_embedding_dimension())
        query_vec = self.embedding_service.embed([query])
        results = project_index.search(query, query_vec, top_k=top_k)
        formatted = []
        for record, score in results:
            formatted.append(
                {
                    "source_id": record.source_id,
                    "page": record.page,
                    "chunk_id": record.chunk_id,
                    "text": record.text,
                    "filename": record.filename,
                    "score": score,
                }
            )
        return formatted

    def build_messages(self, user_message: str, retrieved: List[Dict[str, str]]) -> List[Dict[str, str]]:
        snippets = []
        for item in retrieved:
            snippets.append(
                f"[S{item['source_id']}:p{item['page']}:c{item['chunk_id']}] {item['filename']}: {item['text']}"
            )
        context_block = "\n".join(snippets) if snippets else "(no relevant sources found)"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": RETRIEVAL_INSTRUCTION},
            {"role": "system", "content": FORMAT_RULES},
            {
                "role": "user",
                "content": (
                    "User request:\n"
                    f"{user_message}\n\n"
                    "Retrieved snippets:\n"
                    f"{context_block}"
                ),
            },
        ]
        return messages
