# main.py
from fastapi import FastAPI, UploadFile, File
from trade_parser import parse_trades_from_csv
import shutil
import uuid

app = FastAPI()

@app.post("/upload")
async def upload_trades(file: UploadFile = File(...)):
    # Save uploaded file to a temporary CSV file
    temp_filename = f"temp_{uuid.uuid4()}.csv"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse and generate portfolio summary
    summary = parse_trades_from_csv(temp_filename)
    return summary