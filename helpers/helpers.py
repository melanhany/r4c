

def validate_json_data(data, required_fields):
    missing_fields = required_fields - set(data.keys())
    return missing_fields
