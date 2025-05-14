{\rtf1\ansi\ansicpg1252\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww28600\viewh16380\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # main.py\
from fastapi import FastAPI, UploadFile, File\
from fastapi.middleware.cors import CORSMiddleware\
import fitz  # PyMuPDF\
import io\
\
app = FastAPI()\
\
# CORS setup to allow frontend access\
app.add_middleware(\
    CORSMiddleware,\
    allow_origins=["*"],\
    allow_credentials=True,\
    allow_methods=["*"],\
    allow_headers=["*"],\
)\
\
@app.post("/upload-pdf")\
async def upload_pdf(file: UploadFile = File(...)):\
    try:\
        # Read the uploaded file\
        contents = await file.read()\
        pdf_stream = io.BytesIO(contents)\
        doc = fitz.open(stream=pdf_stream, filetype="pdf")\
\
        full_text = ""\
        for page in doc:\
            full_text += page.get_text()\
\
        # Basic transaction summary extraction\
        lines = full_text.split("\\n")\
        transactions = []\
        for line in lines:\
            if any(char.isdigit() for char in line) and ("INR" in line or ".00" in line):\
                transactions.append(line.strip())\
\
        return \{\
            "status": "success",\
            "total_transactions": len(transactions),\
            "raw_transactions": transactions[:20]  # return sample\
        \}\
    except Exception as e:\
        return \{"status": "error", "message": str(e)\}\
}