from typing import Dict, Any, Optional

def generate_allocation_explanation(evidence: Dict[str, Any], target_ngo_id: Optional[str] = None) -> str:
    winner_id = evidence.get("winner_ngo_id")
    candidates = evidence.get("candidates", [])
    
    if not winner_id:
        return "No eligible NGO was found for this listing. All candidates either lacked capacity, were unverified, or were too far to reach the food before expiry."
    
    if not target_ngo_id:
        target_ngo_id = winner_id
        
    target_candidate = next((c for c in candidates if c["ngo_id"] == target_ngo_id), None)
    if not target_candidate:
        return "The requested NGO was not considered in this allocation round."
        
    if not target_candidate["is_eligible"]:
        reason = target_candidate.get("rejection_reason", "unknown reasons")
        return f"You were not eligible for this allocation because: {reason}."
        
    if target_ngo_id == winner_id:
        runner_up_id = evidence.get("runner_up_ngo_id")
        if not runner_up_id:
            return "You were matched because you were the only eligible NGO for this listing."
            
        runner_up = next((c for c in candidates if c["ngo_id"] == runner_up_id), None)
        factors = evidence.get("winning_factors", [])
        
        factor_texts = []
        if "urgency" in factors:
            factor_texts.append("you had a larger safety margin against the expiry time")
        if "proximity" in factors:
            dist_diff = max(0, runner_up["distance_km"] - target_candidate["distance_km"])
            factor_texts.append(f"you are {dist_diff:.1f} km closer")
        if "capacity" in factors:
            factor_texts.append("you had more remaining capacity to fit the donation size")
            
        if not factor_texts:
            factor_texts = ["you won the tie-breaker"]
            
        explanation = f"You were matched because " + " and ".join(factor_texts)
        explanation += f". Your total score was {target_candidate['total_score']:.2f}, beating the next option by {(target_candidate['total_score'] - runner_up['total_score']):.2f} points."
        return explanation
    else:
        winner = next((c for c in candidates if c["ngo_id"] == winner_id), None)
        score_diff = winner["total_score"] - target_candidate["total_score"]
        dist_diff = target_candidate["distance_km"] - winner["distance_km"]
        margin_diff = winner.get("margin_min", 0) - target_candidate.get("margin_min", 0)
        
        reasons = []
        if dist_diff > 0:
            reasons.append(f"were {dist_diff:.1f} km closer")
        if margin_diff > 0:
            reasons.append(f"had a {margin_diff:.1f} minute larger safety margin")
        if winner["capacity_meals"] > target_candidate["capacity_meals"]:
            reasons.append("had more remaining capacity")
            
        reason_text = ", and ".join(reasons) if reasons else "scored higher on our tie-breaker logic"
        
        return f"You were not selected for this allocation. The winning NGO (NGO {winner_id}) beat your score by {score_diff:.2f} points. Specifically, they {reason_text}."

def generate_global_explanation(evidence: Dict[str, Any]) -> str:
    winner_id = evidence.get("winner_ngo_id")
    if not winner_id:
        return "No eligible NGO was found for this listing."
    
    winner = next(c for c in evidence["candidates"] if c["ngo_id"] == winner_id)
    return f"Allocated to NGO {winner_id} with a score of {winner['total_score']:.2f}."

