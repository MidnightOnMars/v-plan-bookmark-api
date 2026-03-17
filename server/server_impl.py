from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict
import uuid
from datetime import datetime

app = FastAPI()

# ---------- Pydantic Models ----------
class BookmarkCreate(BaseModel):
    url: str = Field(..., description="The URL of the bookmark")
    title: str = Field(..., description="Title of the bookmark")
    tags: List[str] = Field(default_factory=list, description="List of tags")

class Bookmark(BaseModel):
    id: str = Field(..., description="Unique identifier for the bookmark")
    url: str
    title: str
    tags: List[str]
    created_at: str = Field(..., description="ISO8601 timestamp of creation")

# ---------- In-Memory Storage ----------
class BookmarkStorage:
    def __init__(self):
        # Store bookmarks keyed by their string ID
        self._store: Dict[str, Bookmark] = {}

    def get_all(self) -> List[Bookmark]:
        return list(self._store.values())

    def get_by_id(self, bookmark_id: str) -> Bookmark | None:
        return self._store.get(bookmark_id)

    def add(self, bookmark: Bookmark) -> None:
        self._store[bookmark.id] = bookmark

    def delete(self, bookmark_id: str) -> bool:
        if bookmark_id in self._store:
            del self._store[bookmark_id]
            return True
        return False

    def search_by_tag(self, tag: str) -> List[Bookmark]:
        return [b for b in self._store.values() if tag in b.tags]

# Global storage instance
storage = BookmarkStorage()

# ---------- FastAPI Routes ----------
# Search route must be declared before the generic {id} route
@app.get("/bookmarks/search", response_model=List[Bookmark])
def search_bookmarks(tag: str = Query(..., description="Tag to search for")):
    return storage.search_by_tag(tag)

@app.get("/bookmarks", response_model=List[Bookmark])
def list_bookmarks():
    return storage.get_all()

@app.post("/bookmarks", response_model=Bookmark)
def create_bookmark(payload: BookmarkCreate):
    new_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"
    bookmark = Bookmark(
        id=new_id,
        url=payload.url,
        title=payload.title,
        tags=payload.tags,
        created_at=created_at,
    )
    storage.add(bookmark)
    return bookmark

@app.get("/bookmarks/{bookmark_id}", response_model=Bookmark)
def get_bookmark(bookmark_id: str):
    bookmark = storage.get_by_id(bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark

@app.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(bookmark_id: str):
    success = storage.delete(bookmark_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"id": bookmark_id, "deleted": True}
