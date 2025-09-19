# app.py
import io
import os
import re
import uvicorn
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from parser_core import extract_text_from_file, parse_resume
from starlette.middleware.cors import CORSMiddleware

API_KEY_ENV = "RESUME_API_KEY"
EXPECTED_KEY = os.getenv(API_KEY_ENV, "dev")

app = FastAPI(
    title="Resume Parsing API",
    version="1.0.0",
    description="Parses resumes (PDF/DOCX/TXT) into structured JSON.",
)

# Serve static files from the "web" directory at /web
app.mount("/web", StaticFiles(directory="web", html=True), name="web")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for development
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def require_api_key(
    x_api_key: Optional[str] = Header(default=None),
    api_key: Optional[str] = None,
):
    # Check if API key is provided in header or query parameter
    provided_key = x_api_key or api_key
    
    if not EXPECTED_KEY:
        # If no expected key is configured, skip authentication
        return True
    
    if not provided_key or provided_key != EXPECTED_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    
    return True

# ---- Schemas ----

class Link(BaseModel):
    type: Optional[str] = Field(None, description="linkedin/github/portfolio/website/other")
    url: str

class Education(BaseModel):
    institution: Optional[str]
    degree: Optional[str]
    field: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    gpa: Optional[str]
    location: Optional[str]
    highlights: Optional[List[str]] = []

class Experience(BaseModel):
    title: Optional[str]
    company: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    location: Optional[str]
    bullets: Optional[List[str]] = []
    technologies: Optional[List[str]] = []

class Project(BaseModel):
    name: Optional[str]
    description: Optional[str]
    bullets: Optional[List[str]] = []
    technologies: Optional[List[str]] = []
    link: Optional[str]

class Certification(BaseModel):
    name: Optional[str]
    issuer: Optional[str]
    date: Optional[str]
    license: Optional[str]
    url: Optional[str]

class ParseRequest(BaseModel):
    text: Optional[str] = Field(None, description="Raw resume text if not uploading a file.")

class ParseResponse(BaseModel):
    detected_language: Optional[str]
    candidate_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    summary: Optional[str]
    links: List[Link] = []
    skills: List[str] = []
    skill_groups: Dict[str, List[str]] = {}
    languages: List[str] = []
    education: List[Education] = []
    experience: List[Experience] = []
    projects: List[Project] = []
    certifications: List[Certification] = []
    raw_text: Optional[str] = Field(None, description="Use only for debugging")

@app.get("/")
def root():
    """Redirect root to web interface."""
    return RedirectResponse(url="/web/")

@app.get("/favicon.ico")
def favicon():
    """Handle favicon requests to avoid 404 errors."""
    return RedirectResponse(url="/web/favicon.ico", status_code=301)

@app.get("/health")
def health():
    return {"ok": True, "version": "1.0.0"}

@app.post("/parse", response_model=ParseResponse)
async def parse_endpoint(
    file: Optional[UploadFile] = File(default=None),
    text: Optional[str] = Form(default=None),
    include_raw_text: bool = Form(default=False),
    api_key: Optional[str] = Query(default=None, description="API key for authentication"),
    x_api_key: Optional[str] = Header(default=None, description="API key for authentication (header)"),
):
    # Manual authentication check
    provided_key = x_api_key or api_key
    
    if EXPECTED_KEY and (not provided_key or provided_key != EXPECTED_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide either 'file' or 'text'.")
    if file and text:
        raise HTTPException(status_code=400, detail="Provide only one of 'file' or 'text'.")

    if file:
        content = await file.read()
        try:
            resume_text = extract_text_from_file(content, file.filename)
        except ValueError as e:
            raise HTTPException(status_code=415, detail=str(e))
    else:
        resume_text = text or ""

    parsed = parse_resume(resume_text)
    if include_raw_text:
        parsed["raw_text"] = resume_text
    else:
        parsed["raw_text"] = None
    return JSONResponse(parsed)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")), reload=False)
