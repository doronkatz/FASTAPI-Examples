from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
from pathlib import Path

app = FastAPI()

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...)
):
    with open(f"uploads/{file.filename}", "wb") as buffer:
        #“uses shutil.copyfileobj to copy the file content from the UploadFile object to the new file.”
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@app.get("/download/{filename}", response_class=FileResponse)
async def download_file(filename: str):
    if not Path(f"uploads/{filename}").exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(f"uploads/{filename}")
