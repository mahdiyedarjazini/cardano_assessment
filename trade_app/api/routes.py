import os

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse

from trade_app.services.transaction_processor import background_process_data

router = APIRouter()

# Directory for storing uploaded and processed files
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"


@router.post("/enrich-data/")
async def enrich_data(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...)
):
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    # Generate file paths
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    file_name = file.filename.split('.')[0]
    output_path = os.path.join(OUTPUT_DIR, f"{file_name}_enriched.csv")

    # Save uploaded file
    try:
        with open(input_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    background_tasks.add_task(background_process_data, input_path, output_path)

    return JSONResponse({
        "status": "processing",
        "message": "File uploaded and processing started",
        "result_endpoint": f"/api/results/{file_name}"
    })


@router.get("/results/{file_name}")
async def get_results(file_name: str):
    output_file_name = f"{file_name}_enriched.csv"
    output_path = os.path.join(OUTPUT_DIR, output_file_name)

    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Result not found or still processing")

    return FileResponse(
        path=output_path,
        filename=output_file_name,
        media_type="text/csv"
    )