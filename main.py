import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from datetime import datetime

app = FastAPI(title="GlassWindow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExplainRequest(BaseModel):
    query: str = Field(..., description="What to explain or analyze")
    mode: str = Field("expert", description="beginner | expert")


class ExplainResponse(BaseModel):
    mode: str
    summary: str
    key_points: List[str]
    confidence: float
    sources: List[str] = []


@app.get("/")
def read_root():
    return {"service": "GlassWindow Backend", "status": "ok"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


@app.get("/api/market/overview")
def market_overview():
    """Lightweight sample data for the dashboard preview and heatmap."""
    now = datetime.utcnow().isoformat() + "Z"
    sectors = [
        {
            "name": "Layer 1s",
            "change24h": 2.4,
            "volume": 18_200_000_000,
            "assets": [
                {"symbol": "BTC", "change24h": 1.2, "marketCap": 1_250_000_000_000},
                {"symbol": "ETH", "change24h": 2.9, "marketCap": 450_000_000_000},
            ],
        },
        {
            "name": "DeFi",
            "change24h": -1.1,
            "volume": 4_800_000_000,
            "assets": [
                {"symbol": "UNI", "change24h": -0.8, "marketCap": 8_900_000_000},
                {"symbol": "AAVE", "change24h": -2.1, "marketCap": 1_500_000_000},
            ],
        },
        {
            "name": "NFT / Gaming",
            "change24h": 0.6,
            "volume": 980_000_000,
            "assets": [
                {"symbol": "IMX", "change24h": 1.8, "marketCap": 3_400_000_000},
                {"symbol": "APE", "change24h": -0.3, "marketCap": 650_000_000},
            ],
        },
    ]

    heatmap = [
        {"id": "BTC", "value": 1.2},
        {"id": "ETH", "value": 2.9},
        {"id": "SOL", "value": 3.8},
        {"id": "BNB", "value": -0.7},
        {"id": "ARB", "value": 1.1},
        {"id": "OP", "value": 0.5},
    ]

    return {"updatedAt": now, "sectors": sectors, "heatmap": heatmap}


@app.post("/api/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest):
    """Placeholder AI explanation endpoint.
    This synthesizes a structured response deterministically for the demo.
    """
    if not req.query or len(req.query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query is too short")

    style = "Beginner" if req.mode.lower() == "beginner" else "Expert"

    points = [
        "Price action concentrated around key liquidity zones",
        "Funding rates normalizing after recent spikes",
        "Net exchange outflows suggest accumulation",
        "Derivatives skew implies moderate upside bias",
    ]

    return ExplainResponse(
        mode=style.lower(),
        summary=f"{style} view: {req.query.strip()} likely driven by liquidity rotation, macro risk appetite, and exchange flow dynamics.",
        key_points=points,
        confidence=0.72,
        sources=[
            "CeFi spot feeds",
            "On-chain exchange flows",
            "Derivatives funding + OI",
        ],
    )


@app.get("/api/reports")
def list_reports():
    """Sample reports list for the Reports Hub."""
    return {
        "items": [
            {
                "id": "weekly-crypto-outlook",
                "title": "Weekly Crypto Outlook",
                "period": "Week 46",
                "createdAt": datetime.utcnow().isoformat() + "Z",
            },
            {
                "id": "macro-brief",
                "title": "Macro Brief: Rates + Liquidity",
                "period": "This Week",
                "createdAt": datetime.utcnow().isoformat() + "Z",
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
