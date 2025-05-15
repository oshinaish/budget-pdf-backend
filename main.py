from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        pdf_stream = io.BytesIO(contents)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")

        full_text = ""
        for page in doc:
            full_text += page.get_text()

        lines = full_text.split("\n")
        transactions = []
        for line in lines:
            if any(char.isdigit() for char in line) and ("INR" in line or ".00" in line):
                transactions.append(line.strip())

        return {
            "status": "success",
            "total_transactions": len(transactions),
            "raw_transactions": transactions[:20]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
