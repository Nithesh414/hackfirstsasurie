from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import YieldPredictionRequest, YieldPredictionResponse, PredictionHistory, AdminStats
from database import init_db, save_prediction, get_history, get_stats, get_all_predictions, delete_prediction, delete_all_predictions, get_market_price, get_all_market_prices
from yield_model import predict_yield, get_yield_rating
from chatbot import generate_analysis

# Initialize database
init_db()

app = FastAPI(
    title="AI Yield Prediction System",
    description="Intelligent agricultural assistant for crop yield prediction and AI-powered analysis",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@app.get("/")
async def root():
    """Root endpoint - serves the frontend"""
    index_path = os.path.join(BASE_DIR, "frontend", "index.html")
    return FileResponse(index_path)


@app.get("/style.css")
async def serve_css():
    """Serve CSS file"""
    css_path = os.path.join(BASE_DIR, "frontend", "style.css")
    return FileResponse(css_path, media_type="text/css")


@app.get("/script.js")
async def serve_js():
    """Serve JavaScript file"""
    js_path = os.path.join(BASE_DIR, "frontend", "script.js")
    return FileResponse(js_path, media_type="application/javascript")


@app.get("/crops")
async def get_crops():
    """Get list of available crops"""
    from yield_model import get_available_crops
    return {"crops": get_available_crops()}


@app.post("/predict", response_model=YieldPredictionResponse)
async def predict_yield_endpoint(request: YieldPredictionRequest):
    """
    Predict crop yield and get AI-powered analysis
    
    Args:
        request: YieldPredictionRequest with crop, area, soil_type, fertility, water, season
    
    Returns:
        YieldPredictionResponse with predicted yield and AI analysis
    """
    try:
        # Validate area
        if request.area <= 0:
            raise HTTPException(status_code=400, detail="Area must be greater than 0")
        
        # Validate crop
        if not request.crop or not request.crop.strip():
            raise HTTPException(status_code=400, detail="Crop name cannot be empty")
        
        # Get predicted yield
        predicted_yield = predict_yield(
            crop=request.crop,
            area=request.area,
            soil_type=request.soil_type,
            fertility=request.fertility,
            water=request.water,
            season=request.season
        )
        
        # Get yield rating
        yield_rating = get_yield_rating(predicted_yield, request.crop)
        
        # Get AI analysis
        analysis_data = generate_analysis(
            crop=request.crop,
            area=request.area,
            soil_type=request.soil_type,
            fertility=request.fertility,
            water=request.water,
            season=request.season,
            predicted_yield=predicted_yield
        )
        
        # Override yield_rating from AI if available
        if analysis_data.get("yield_rating"):
            yield_rating = analysis_data["yield_rating"]
        
        # Save to database
        save_prediction(
            crop=request.crop,
            area=request.area,
            soil_type=request.soil_type,
            fertility=request.fertility,
            water=request.water,
            season=request.season,
            predicted_yield=predicted_yield
        )
        
        # Create response
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        return YieldPredictionResponse(
            predicted_yield=predicted_yield,
            yield_rating=yield_rating,
            analysis=analysis_data.get("analysis", "Analysis not available"),
            improvement_suggestions=analysis_data.get("improvement_suggestions", "No suggestions available"),
            sustainability_advice=analysis_data.get("sustainability_advice", "No sustainability advice available"),
            timestamp=timestamp
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prediction: {str(e)}")


@app.get("/history", response_model=List[PredictionHistory])
async def get_prediction_history(limit: int = Query(5, ge=1, le=20)):
    """
    Get prediction history
    
    Args:
        limit: Number of records to return (default 5, max 20)
    
    Returns:
        List of prediction history
    """
    try:
        history = get_history(limit=limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@app.get("/stats", response_model=AdminStats)
async def get_statistics():
    """
    Get admin statistics
    
    Returns:
        AdminStats with total predictions, most common crop, average yield
    """
    try:
        stats = get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@app.get("/export")
async def export_predictions():
    """
    Export all predictions as CSV
    
    Returns:
        CSV content of all predictions
    """
    try:
        predictions = get_all_predictions()
        
        # Create CSV content
        csv_content = "ID,Crop,Area (ha),Soil Type,Fertility,Water,Season,Predicted Yield (tonnes),Timestamp\n"
        
        for p in predictions:
            csv_content += f"{p.id},{p.crop},{p.area},{p.soil_type},{p.fertility},{p.water},{p.season or 'N/A'},{p.predicted_yield},{p.timestamp}\n"
        
        return JSONResponse(
            content={"csv": csv_content},
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


@app.delete("/history/{prediction_id}")
async def delete_single_prediction(prediction_id: int):
    """
    Delete a specific prediction by ID
    """
    try:
        deleted = delete_prediction(prediction_id)
        if deleted:
            return {"message": f"Prediction {prediction_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Prediction not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting prediction: {str(e)}")


@app.delete("/history")
async def delete_all_history():
    """
    Delete all prediction history
    """
    try:
        delete_all_predictions()
        return {"message": "All predictions deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting history: {str(e)}")


@app.get("/market-price/{crop}")
async def get_crop_market_price(crop: str):
    """
    Get market price for a specific crop
    """
    try:
        price = get_market_price(crop)
        return {
            "crop": crop,
            "min_price": price["min"],
            "max_price": price["max"],
            "avg_price": price["avg"],
            "best_price": price["max"],
            "unit": price["unit"],
            "currency": "INR"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market price: {str(e)}")


@app.get("/market-prices")
async def get_all_prices():
    """
    Get all market prices
    """
    try:
        prices = get_all_market_prices()
        result = {}
        for crop, price in prices.items():
            result[crop] = {
                "min_price": price["min"],
                "max_price": price["max"],
                "avg_price": price["avg"],
                "best_price": price["max"],
                "unit": price["unit"],
                "currency": "INR"
            }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market prices: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Yield Prediction System"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)