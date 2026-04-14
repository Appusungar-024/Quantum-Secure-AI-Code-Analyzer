from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import validation
import crypto_detector
import pqc_converter
import os
from reporter import generate_structured_output
from typing import Optional

try:
    import openai
    openai_available = True
except ImportError:
    openai_available = False

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze_web")
def analyze_web(request: Request, code: Optional[str] = Form(None), file: Optional[UploadFile] = File(None), llm_enabled: bool = Form(False), use_local: bool = Form(False)):
    if file:
        content = file.file.read().decode("utf-8")
        filename = file.filename or "uploaded_code.py"
        temp_path = f"/tmp/{filename}"
        with open(temp_path, "w") as f:
            f.write(content)
        path = temp_path
    elif code:
        temp_path = "/tmp/user_code.py"
        with open(temp_path, "w") as f:
            f.write(code)
        path = temp_path
    else:
        return templates.TemplateResponse("index.html", {"request": request, "error": "No code provided"})

    try:
        report = validation.run_full_pipeline(path, llm_enabled=llm_enabled, use_local=use_local)
        structured = generate_structured_output(report)
        return templates.TemplateResponse("result.html", {"request": request, "structured": structured, "report": report})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/analyze/")
def analyze(path: str = "sample_code", llm_enabled: bool = False, use_local: bool = False):
    if not os.path.exists(path):
        # try relative to backend
        alt = os.path.join(os.path.dirname(__file__), "..", path)
        if os.path.exists(alt):
            path = alt
        else:
            raise HTTPException(status_code=404, detail="Path not found")

    report = validation.run_full_pipeline(path, llm_enabled=llm_enabled, use_local=use_local)
    structured = generate_structured_output(report)
    report["structured_output"] = structured
    return report


@app.post("/convert/")
def convert_file(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(path, "r") as f:
        src = f.read()
    converted = pqc_converter.convert_code_to_pqc(src)
    return {"path": path, "converted": converted}


@app.get("/detect/")
def detect(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    issues = crypto_detector.detect_file(path)
    return {"path": path, "issues": issues}