def sample_estimate_downtime(hours=1):
    return {"estimate_hours": hours, "notes": "rough estimate"}

FN_REGISTRY = {
    "estimate_downtime": sample_estimate_downtime
}
