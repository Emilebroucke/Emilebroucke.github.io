import io
import json
import os
import zipfile
from typing import Dict, List

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from .config import settings
from .providers.registry import get_provider
from .services.chat import ChatService
from .services.embeddings import EmbeddingService
from .services.ingest import IngestService, ProjectManager
from .services.index import ProjectIndex

app = FastAPI(title="NotebookLM-Style Local App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

embedding_service = EmbeddingService(settings.embedding_model)
project_manager = ProjectManager(settings.data_dir)
chat_service = ChatService(embedding_service)


def _ingest_bytes(project_id: str, filename: str, content: bytes) -> Dict[str, str]:
    ingest_service = IngestService(embedding_service)
    project_dir = project_manager.project_dir(project_id)
    return ingest_service.ingest_file(project_dir, filename, content)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/projects")
async def list_projects() -> List[Dict[str, str]]:
    return project_manager.list_projects()


@app.post("/projects")
async def create_project(payload: Dict[str, str]) -> Dict[str, str]:
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Project name required")
    return project_manager.create_project(name)


@app.get("/projects/{project_id}/sources")
async def list_sources(project_id: str) -> List[Dict[str, str]]:
    project_dir = project_manager.project_dir(project_id)
    project_index = ProjectIndex(project_dir, embedding_service.model.get_sentence_embedding_dimension())
    return project_index.get_sources()


@app.post("/projects/{project_id}/upload")
async def upload_sources(
    project_id: str,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
) -> JSONResponse:
    project_dir = project_manager.project_dir(project_id)
    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail="Project not found")

    uploads = []
    for upload in files:
        data = upload.file.read()
        uploads.append((upload.filename, data))

    def _run_ingest() -> None:
        results = []
        for filename, data in uploads:
            if len(data) > settings.max_upload_mb * 1024 * 1024:
                raise HTTPException(status_code=413, detail="File too large")
            if filename.lower().endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(data)) as zf:
                    for info in zf.infolist():
                        if info.is_dir():
                            continue
                        results.append(_ingest_bytes(project_id, info.filename, zf.read(info)))
            else:
                results.append(_ingest_bytes(project_id, filename, data))
        return results

    background_tasks.add_task(_run_ingest)
    return JSONResponse({"status": "ingest_started", "files": [f.filename for f in files]})


@app.post("/projects/{project_id}/search")
async def search(project_id: str, payload: Dict[str, str]) -> List[Dict[str, str]]:
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query required")
    project_dir = project_manager.project_dir(project_id)
    return chat_service.retrieve(project_dir, query, top_k=payload.get("top_k", 8))


@app.post("/projects/{project_id}/chat/stream")
async def chat_stream(project_id: str, payload: Dict[str, str]) -> StreamingResponse:
    query = payload.get("message")
    if not query:
        raise HTTPException(status_code=400, detail="Message required")
    project_dir = project_manager.project_dir(project_id)
    retrieved = chat_service.retrieve(project_dir, query, top_k=payload.get("top_k", 8))
    messages = chat_service.build_messages(query, retrieved)
    provider = get_provider()

    def event_stream():
        yield "event: sources\n"
        yield f"data: {json.dumps(retrieved)}\n\n"
        for token in provider.stream_chat(messages):
            yield "event: token\n"
            yield f"data: {token}\n\n"
        yield "event: done\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
