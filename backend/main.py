import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Load environment variables (if needed by the imported classes)
load_dotenv()

# Import the pre-defined classes
from utils.ToolsSelectionAgent import ToolsSelectionAgent
from utils.OpenAIModel import OpenAIModel
from utils.MarkitdownTool import MarkItDownConverter


app = FastAPI()

# Allow CORS (adjust allowed origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the imported classes
tool_agent = ToolsSelectionAgent()
openai_model = OpenAIModel()

# -------------------------------
# Pydantic Models for Requests
# -------------------------------
class EmbeddingRequest(BaseModel):
    text: str

class ToolSelectionRequest(BaseModel):
    context: str
    available_tools: dict  # e.g., {"getBuyerBankStatement": "description", ...}

# -------------------------------
# FastAPI Endpoints
# -------------------------------
@app.post("/embed")
async def embed_text(request: EmbeddingRequest):
    """
    Endpoint to create an embedding for the provided text.
    """
    try:
        embedding = openai_model.create_embedding(request.text)
        return {"embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Endpoint to transcribe an uploaded audio file.
    """
    try:
        # Save the uploaded file temporarily
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        
        transcription = openai_model.transcribe_audio(file_location)
        os.remove(file_location)  # Clean up the temporary file
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/markitdown")
async def convert_pdf(file: UploadFile = File(...)):
    """
    Endpoint to convert an uploaded PDF file to Markdown text using MarkItDown.
    """
    temp_file = f"temp_{file.filename}"
    try:
        # Save the uploaded PDF file temporarily
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Instantiate the converter and perform the conversion
        converter = MarkItDownConverter()
        markdown_text = converter.convert_pdf_to_markdown(temp_file)
        
        # Clean up the temporary file
        os.remove(temp_file)
        return {"markdown": markdown_text}
    
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/select_tool")
async def select_tool(request: ToolSelectionRequest):
    """
    Endpoint to select the most appropriate tool based on the provided context.
    """
    try:
        selected_tool = tool_agent.select_tool(request.context, request.available_tools)
        return {"selected_tool": selected_tool}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# To run the FastAPI server:
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
# -------------------------------
