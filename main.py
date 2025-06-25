from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Marine Engine Diagnostic API",
    description="AI-powered analysis of 2-stroke marine engines",
    version="0.1.0",
    contact={
        "name": "API Support",
        "email": "2468by4koff@gmail.com"
    },
    license_info={
        "name": "MIT",
    },
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class EngineInfo(BaseModel):
    engine_id: str
    vessel_id: Optional[str] = None
    engine_type: str = "2T"
    manufacturer: Optional[str] = None

class AnalysisResult(BaseModel):
    analysis_id: str
    timestamp: datetime
    engine_info: EngineInfo
    status: str  # "normal", "warning", "critical"
    detected_anomalies: list[str]
    confidence: float
    recommended_actions: list[str]

# Mock ML Analysis (Replace with actual model)
async def analyze_engine_diagram(file: UploadFile, engine_info: EngineInfo) -> AnalysisResult:
    """Mock analysis function to be replaced with actual CNN model"""
    # In production, this would use your trained CNN model
    return AnalysisResult(
        analysis_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        engine_info=engine_info,
        status="warning",
        detected_anomalies=["ring_wear"],
        confidence=0.92,
        recommended_actions=[
            "Check piston ring clearance",
            "Inspect cylinder liner"
        ]
    )

# API Endpoints
@app.post("/api/analyze/indicator-diagram",
          response_model=AnalysisResult,
          summary="Analyze engine indicator diagram",
          tags=["Analysis"])
async def analyze_indicator_diagram(
    file: UploadFile = File(..., description="Indicator diagram image (PNG/JPEG)"),
    engine_info: EngineInfo
):
    """
    Analyze a 2-stroke marine engine's indicator diagram for:
    - Combustion anomalies
    - Ring wear patterns
    - Injector issues
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are supported"
            )

        logger.info(f"Received analysis request for engine {engine_info.engine_id}")

        # Process the file (in production: save to S3/MinIO first)
        result = await analyze_engine_diagram(file, engine_info)

        logger.info(f"Analysis completed for {engine_info.engine_id}. Status: {result.status}")

        return result

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/api/health", tags=["System"])
async def health_check():
    """Service health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Error Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow(),
            "path": request.url.path
        }
    )
