from fastapi import APIRouter
from stability_engine import StabilityEngine

router = APIRouter(prefix="/calculate", tags=["UFO - Stability"])

@router.post("/stability")
async def calculate_stability(total_p_kN: float, height: float, m1_kNm: float, 
                              wind_v0: float = 30.0, f1_hz: float = 0.5):
    # Usar o método avançado do StabilityEngine
    res = StabilityEngine.calculate_advanced_stability(
        total_p_kN=total_p_kN, 
        height=height, 
        m1_kNm=m1_kNm, 
        wind_v0=wind_v0, 
        f1_hz=f1_hz
    )
    return {"success": True, "stability": res}
