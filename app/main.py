from fastapi import FastAPI
from app.api.v1.hmm_router import router as hmm_router
from app.api.v1.trend_router import router as trend_router

app = FastAPI(title="Quant Sight Core API", version="1.0.0");

app.include_router(hmm_router, prefix="/v1/hmm", tags=["HMM Regime Detection"])
app.include_router(trend_router, prefix="/v1/trend-bias", tags=["Trend Bias Detection"])