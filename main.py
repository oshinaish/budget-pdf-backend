from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from openai import OpenAI
import json

app = FastAPI()

client = OpenAI(api_key="Birbal")

# CORS setup
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
        reader = PdfReader(file.file)
        lines = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                lines.extend(line.strip() for line in text.splitlines() if line.strip())

        if not lines:
            return {"status": "error", "message": "No text found in PDF."}

        # Prepare GPT prompt
        prompt = (
            "Categorize these bank transactions by category (Dining, Travel, Groceries, etc.) in JSON format:\n\n"
            + "\n".join(lines[:50])
        )

        response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}])
        )

        gpt_output = response.choices[0].message.content
        try:
            categorized = json.loads(gpt_output)
        except json.JSONDecodeError:
            categorized = {"Uncategorized": lines}

        return {
            "status": "success",
            "total_transactions": len(lines),
            "raw_transactions": lines,
            "categorized": categorized
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
