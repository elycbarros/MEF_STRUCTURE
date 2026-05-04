"""
routes/phd.py — Router para funcionalidades M5-PhD.
"""
from fastapi import APIRouter, HTTPException
from typing import Any, Dict
from pydantic import BaseModel
from radier_lab_v24 import LabConfig

router = APIRouter(tags=["PhD Autonomous Engine"])

class MLPredictionRequest(BaseModel):
    Lx: float; Ly: float; h: float; kv: float; q: float

@router.post("/phd/predict_fast")
async def predict_fast(req: MLPredictionRequest):
    """Predição ultra-rápida via ML Surrogate (PhD)."""
    try:
        from ml_surrogate import StructuralSurrogate
        surrogate = StructuralSurrogate()
        # Treino rápido com dados sintéticos se não houver modelo (apenas para o demo)
        df = surrogate.generate_training_data(100)
        surrogate.train(df)
        res = surrogate.predict(req.Lx, req.Ly, req.h, req.kv, req.q)
        if "w_max_mm_pred" in res:
            res["max_settlement_mm"] = res["w_max_mm_pred"]
        if "q_max_kPa_pred" in res:
            res["avg_pressure_kPa"] = res["q_max_kPa_pred"]
        return {"success": True, "prediction": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/phd/auto_design")
async def run_auto_design(config: Dict[str, Any]):
    """Inicia um Agente Autônomo para otimizar o design (PhD)."""
    try:
        from autonomous_agent import AutonomousDesignAgent
        from radier_lab_v24 import LabConfig
        
        cfg = LabConfig(**config)
        agent = AutonomousDesignAgent()
        result = agent.run_design_cycle(cfg, max_iterations=3)
        return {"success": True, "agent_history": result['history'], "final_design": str(result['final_config'])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phd/distributed_status")
async def get_distributed_status():
    """Status do cluster de resolução distribuída (PhD)."""
    from distributed_engine import DistributedAssembler
    engine = DistributedAssembler(n_total_dofs=1_000_000, n_partitions=16)
    return {"success": True, "cluster_summary": engine.solve_distributed()}
