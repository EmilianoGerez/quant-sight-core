from fastapi import FastAPI
from app.api.v1.hmm_router import router as hmm_router

app = FastAPI(title="Quant Sight Core API", version="1.0.0");

app.include_router(hmm_router, prefix="/v1/hmm", tags=["HMM Regime Detection"])