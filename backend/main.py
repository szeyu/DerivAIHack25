import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
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
from utils.FraudDetection import FraudDetection
from utils.OCRScanner import OCRScanner
from utils.DisputeResolutionPipeline import DisputeResolutionPipeline  # Import your pipeline class
from utils.deepseek_service import DeepSeekService

app = FastAPI()

# Allow CORS (adjust allowed origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the imported classes
tool_agent = ToolsSelectionAgent()
openai_model = OpenAIModel()
deepseek_service = DeepSeekService()

# -------------------------------
# Pydantic Models for Requests and Responses
# -------------------------------

class EmbeddingRequest(BaseModel):
    text: str

class ToolSelectionRequest(BaseModel):
    context: str
    available_tools: dict  # e.g., {"getBuyerBankStatement": "description", ...}

class FraudDetectionRequest(BaseModel):
    text: str
    warning_count: int = 0

class FraudDetectionResponse(BaseModel):
    result: str  # "No Fraud" or "Fraud Detected"
    warning_count: int
    escalate: bool

# Response model for dispute resolution
class DisputeResolutionResponse(BaseModel):
    resolution: str
    selected_tool: str
    escalate: bool

class DisputeRequest(BaseModel):
    conversation: str

class SimilarCaseRequest(BaseModel):
    current_summary: str
    past_cases: list[str]

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

@app.post("/ocrscanner")
async def ocrscanner(file: UploadFile = File(...)):
    """
    Endpoint to convert an uploaded PDF file to Markdown text using OCRScanner.
    This endpoint uses the OCRScanner class which first converts the PDF pages to images 
    (using PyMuPDF, hence avoiding Poppler) and then uses Gemini for OCR extraction.
    """
    temp_file = f"temp_{file.filename}"
    try:
        # Save the uploaded PDF file temporarily
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Instantiate OCRScanner and perform the conversion
        scanner = OCRScanner()
        markdown_text = scanner.convert_pdf_to_markdown(temp_file)
        
        # Clean up the temporary file
        os.remove(temp_file)
        return {"markdown": markdown_text}
    
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fraud_detection_firewall", response_model=FraudDetectionResponse)
async def fraud_detection_firewall(request: FraudDetectionRequest):
    """
    API endpoint that evaluates user input using the FraudDetection system.
    Returns "Fraud Detected" if sensitive content is found, otherwise "No Fraud".
    """
    try:
        # In this example, the llm function is a no-op lambda. Replace with your actual LLM call if needed.
        response_text, warnings, escalate = FraudDetection.process_user_input(
            user_input=request.text,
            warning_count=request.warning_count,
            llm=openai_model.llm  # Use your actual LLM integration
        )
        # Determine the result based on the response text
        result = "Fraud Detected" if response_text.startswith("Warning:") else "No Fraud"
        return FraudDetectionResponse(result=result, warning_count=warnings, escalate=escalate)
    except Exception as e:
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

@app.post("/resolve_dispute", response_model=DisputeResolutionResponse)
async def resolve_dispute_endpoint(
    conversation_chain: str = Form(...),
    pdf_file_user: UploadFile = File(...),
    pdf_file_seller: UploadFile = File(...)
):
    """
    Endpoint to process the dispute using DisputeResolutionPipeline.
    """
    temp_file1 = f"temp_{pdf_file_user.filename}"
    temp_file2 = f"temp_{pdf_file_seller.filename}"
    try:
        # Save the uploaded PDF files temporarily
        with open(temp_file1, "wb") as f1:
            content1 = await pdf_file_user.read()
            f1.write(content1)
        
        with open(temp_file2, "wb") as f2:
            content2 = await pdf_file_seller.read()
            f2.write(content2)
        
        # Instantiate the DisputeResolutionPipeline
        pipeline = DisputeResolutionPipeline(model="gpt-4o")
        
        # Process the dispute
        result = pipeline.process_dispute(conversation_chain, temp_file1, temp_file2)
        
        # Clean up the temporary files
        os.remove(temp_file1)
        os.remove(temp_file2)
        
        return DisputeResolutionResponse(
            resolution=result["resolution"],
            selected_tool=result["selected_tool"],
            escalate=result.get("escalate", False)
        )
    except Exception as e:
        # Clean up the temporary files if they exist
        if os.path.exists(temp_file1):
            os.remove(temp_file1)
        if os.path.exists(temp_file2):
            os.remove(temp_file2)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dispute/summary")
async def get_dispute_summary(request: DisputeRequest):
    """Get AI-generated summary of dispute conversation."""
    try:
        summary = deepseek_service.generate_dispute_summary(request.conversation)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dispute/fraud-analysis")
async def get_fraud_analysis(request: DisputeRequest):
    """Get fraud analysis of dispute conversation."""
    try:
        analysis = deepseek_service.detect_fraud_signals(request.conversation)
        return {"fraud_analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dispute/similar-cases")
async def get_similar_cases(request: SimilarCaseRequest):
    """Get similar past cases."""
    try:
        similar_cases = deepseek_service.find_similar_cases(
            request.current_summary,
            request.past_cases
        )
        return {"similar_cases": similar_cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# To run the FastAPI server:
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
# -------------------------------