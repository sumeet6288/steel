from typing import Dict, Any
import json

class TeklaExporter:
    
    @staticmethod
    def export_connection(connection_data: Dict[str, Any], geometry: Dict[str, Any]) -> str:
        tekla_object = {
            "connection_type": "parametric_shear_connection",
            "connection_name": connection_data.get("name", "Unnamed"),
            "connection_id": connection_data.get("id", ""),
            "aisc_compliant": connection_data.get("validation_results", {}).get("is_valid", False),
            "disclaimer": "ADVISORY OUTPUT - Engineering review and approval required. Not stamped.",
            "parameters": connection_data.get("parameters", {}),
            "geometry": geometry,
            "tekla_properties": TeklaExporter._generate_tekla_properties(geometry),
            "audit_trail": {
                "generated_by": "SteelConnect AI",
                "ai_assisted": connection_data.get("ai_suggested", False),
                "rule_checks_passed": connection_data.get("validation_results", {}).get("is_valid", False)
            }
        }
        
        return json.dumps(tekla_object, indent=2)
    
    @staticmethod
    def _generate_tekla_properties(geometry: Dict[str, Any]) -> Dict[str, Any]:
        properties = {
            "editable": True,
            "manual_adjustment_allowed": True
        }
        
        if "plate" in geometry:
            plate = geometry["plate"]
            properties["plate"] = {
                "length": plate.get("length"),
                "width": plate.get("width"),
                "thickness": plate.get("thickness"),
                "material": plate.get("material", "A36")
            }
        
        if "bolts" in geometry:
            bolts = geometry["bolts"]
            if bolts:
                properties["bolts"] = {
                    "count": len(bolts),
                    "diameter": bolts[0].get("diameter"),
                    "grade": bolts[0].get("grade"),
                    "positions": [b.get("position") for b in bolts]
                }
        
        return properties