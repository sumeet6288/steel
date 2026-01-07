from typing import Dict, Any, List

class ValidationEngine:
    
    @staticmethod
    def validate_geometry(geometry: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        warnings = []
        
        if not geometry:
            issues.append("No geometry generated")
            return {"is_valid": False, "issues": issues, "warnings": warnings}
        
        if "plate" in geometry:
            plate = geometry["plate"]
            if plate.get("length", 0) <= 0 or plate.get("width", 0) <= 0:
                issues.append("Invalid plate dimensions")
            if plate.get("thickness", 0) <= 0:
                issues.append("Invalid plate thickness")
        
        if "bolts" in geometry:
            bolts = geometry["bolts"]
            if not bolts or len(bolts) == 0:
                issues.append("No bolts defined")
            elif len(bolts) < 2:
                warnings.append("Less than 2 bolts - verify design intent")
        
        if "dimensions" not in geometry:
            warnings.append("Missing dimension summary")
        
        is_valid = len(issues) == 0
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "geometry_type": geometry.get("type", "unknown")
        }
    
    @staticmethod
    def validate_parameters(params: Dict[str, Any], connection_type: str) -> Dict[str, Any]:
        issues = []
        warnings = []
        
        required_params = {
            "single_plate": ["num_bolts", "bolt_diameter", "plate_thickness"],
            "double_angle": ["num_bolts", "bolt_diameter", "angle_size"],
            "end_plate": ["num_bolts_vertical", "num_bolts_horizontal", "plate_thickness"],
            "beam_to_column_shear": ["num_bolts", "bolt_diameter"],
            "beam_to_beam_shear": ["num_bolts", "bolt_diameter"]
        }
        
        required = required_params.get(connection_type, [])
        for param in required:
            if param not in params or params[param] is None:
                issues.append(f"Missing required parameter: {param}")
        
        if "bolt_diameter" in params:
            diameter = params["bolt_diameter"]
            if diameter not in [0.5, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25]:
                warnings.append(f"Non-standard bolt diameter: {diameter} in")
        
        if "plate_thickness" in params:
            thickness = params["plate_thickness"]
            if thickness < 0.1875:
                issues.append(f"Plate thickness {thickness} in is below minimum (3/16 in)")
        
        is_valid = len(issues) == 0
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "warnings": warnings
        }