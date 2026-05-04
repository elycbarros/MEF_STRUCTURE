from fastapi import APIRouter

from load_combinator import combine_nbr8681
from schemas.loads import LoadCombinationRequest
from radier_utils import sanitize_for_json

router = APIRouter(prefix="/calculate", tags=["Load Combinations"])

@router.post("/load-combinations")
async def calculate_load_combinations(req: LoadCombinationRequest):
    result = combine_nbr8681(
        [action.model_dump() for action in req.actions],
        gamma_g_unfav=req.gamma_g_unfav,
        gamma_g_fav=req.gamma_g_fav,
        gamma_q=req.gamma_q,
        special_situation=req.special_situation
    )
    return sanitize_for_json(result)
