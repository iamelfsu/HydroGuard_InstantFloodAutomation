def clean_input_string(raw_text: str) -> str:
    return " ".join(raw_text.strip().split())

def parse_and_validate_discharge(raw_value) -> float:

    try:
        if isinstance(raw_value, list) and raw_value:
            actual_value = raw_value[0]
        else:
            actual_value = raw_value
            
        discharge_float = float(actual_value)

        if discharge_float < 0:
            return 0.0

        return discharge_float
    except (ValueError, TypeError, IndexError):
        return 0.0

def evaluate_flood_hazard(discharge_rate: float) -> str:

    if discharge_rate >= 5.0:
        return "CRITICAL"
    elif discharge_rate >= 2.5:
        return "WARNING"
    return "SAFE"
