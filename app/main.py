from fastapi import FastAPI
from app.api.v1.hmm_router import router as hmm_router
from app.api.v1.trend_router import router as trend_router
from app.api.v1.iv_rank_router import router as iv_rank_router

app = FastAPI(title="Quant Sight Core API", version="1.0.0");

app.include_router(hmm_router, prefix="/v1/hmm", tags=["HMM Regime Detection"])
app.include_router(trend_router, prefix="/v1/trend-bias", tags=["Trend Bias Detection"])
app.include_router(iv_rank_router, prefix="/v1/iv", tags=["IV Metrics"])