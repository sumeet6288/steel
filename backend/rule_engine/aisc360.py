import math
from typing import Dict, Any, List
from .base import RuleEngine, RuleResult, RuleCheck, RuleStatus

class AISC360RuleEngine(RuleEngine):
    
    def __init__(self):
        self.GAMMA_M0 = 1.0
        
    def validate_connection(self, connection_type: str, parameters: Dict[str, Any]) -> RuleResult:
        checks = []
        
        if connection_type in ["beam_to_column_shear", "beam_to_beam_shear", "single_plate", "double_angle", "end_plate"]:
            checks.extend(self._validate_bolts(parameters))
            checks.extend(self._validate_plate(parameters))
            checks.extend(self._validate_geometry(parameters))
        
        overall_status = RuleStatus.PASS
        for check in checks:
            if check.status == RuleStatus.FAIL:
                overall_status = RuleStatus.FAIL
                break
            elif check.status == RuleStatus.WARNING and overall_status == RuleStatus.PASS:
                overall_status = RuleStatus.WARNING
        
        is_valid = overall_status != RuleStatus.FAIL
        summary = self._generate_summary(checks, overall_status)
        
        return RuleResult(
            overall_status=overall_status,
            checks=checks,
            summary=summary,
            is_valid=is_valid
        )
    
    def _validate_bolts(self, params: Dict[str, Any]) -> List[RuleCheck]:
        checks = []
        
        bolt_diameter = params.get('bolt_diameter', 0.75)
        bolt_grade = params.get('bolt_grade', 'A325')
        num_bolts = params.get('num_bolts', 4)
        bolt_spacing = params.get('bolt_spacing', 3.0)
        edge_distance = params.get('edge_distance', 1.5)
        
        min_spacing = 2.67 * bolt_diameter
        if bolt_spacing >= min_spacing:
            checks.append(RuleCheck(
                rule_id="AISC_J3_3",
                rule_name="Minimum Bolt Spacing",
                status=RuleStatus.PASS,
                message=f"Bolt spacing {bolt_spacing:.2f} in >= {min_spacing:.2f} in (2.67d)",
                code_reference="AISC 360-16 Table J3.3",
                calculated_value=bolt_spacing,
                limit_value=min_spacing
            ))
        else:
            checks.append(RuleCheck(
                rule_id="AISC_J3_3",
                rule_name="Minimum Bolt Spacing",
                status=RuleStatus.FAIL,
                message=f"Bolt spacing {bolt_spacing:.2f} in < {min_spacing:.2f} in (2.67d) - VIOLATION",
                code_reference="AISC 360-16 Table J3.3",
                calculated_value=bolt_spacing,
                limit_value=min_spacing
            ))
        
        max_spacing = min(14 * params.get('plate_thickness', 0.5), 7.0)
        if bolt_spacing <= max_spacing:
            checks.append(RuleCheck(
                rule_id="AISC_J3_5",
                rule_name="Maximum Bolt Spacing",
                status=RuleStatus.PASS,
                message=f"Bolt spacing {bolt_spacing:.2f} in <= {max_spacing:.2f} in",
                code_reference="AISC 360-16 Table J3.5",
                calculated_value=bolt_spacing,
                limit_value=max_spacing
            ))
        else:
            checks.append(RuleCheck(
                rule_id="AISC_J3_5",
                rule_name="Maximum Bolt Spacing",
                status=RuleStatus.WARNING,
                message=f"Bolt spacing {bolt_spacing:.2f} in > {max_spacing:.2f} in - Check required",
                code_reference="AISC 360-16 Table J3.5",
                calculated_value=bolt_spacing,
                limit_value=max_spacing
            ))
        
        hole_diameter = bolt_diameter + 0.125
        min_edge = max(1.5 * hole_diameter, 1.25)
        if edge_distance >= min_edge:
            checks.append(RuleCheck(
                rule_id="AISC_J3_4",
                rule_name="Minimum Edge Distance",
                status=RuleStatus.PASS,
                message=f"Edge distance {edge_distance:.2f} in >= {min_edge:.2f} in",
                code_reference="AISC 360-16 Table J3.4",
                calculated_value=edge_distance,
                limit_value=min_edge
            ))
        else:
            checks.append(RuleCheck(
                rule_id="AISC_J3_4",
                rule_name="Minimum Edge Distance",
                status=RuleStatus.FAIL,
                message=f"Edge distance {edge_distance:.2f} in < {min_edge:.2f} in - VIOLATION",
                code_reference="AISC 360-16 Table J3.4",
                calculated_value=edge_distance,
                limit_value=min_edge
            ))
        
        if num_bolts >= 2:
            checks.append(RuleCheck(
                rule_id="AISC_J3_MIN",
                rule_name="Minimum Number of Bolts",
                status=RuleStatus.PASS,
                message=f"Number of bolts {num_bolts} >= 2",
                code_reference="AISC 360-16 J3",
                calculated_value=float(num_bolts),
                limit_value=2.0
            ))
        else:
            checks.append(RuleCheck(
                rule_id="AISC_J3_MIN",
                rule_name="Minimum Number of Bolts",
                status=RuleStatus.FAIL,
                message=f"Number of bolts {num_bolts} < 2 - VIOLATION",
                code_reference="AISC 360-16 J3",
                calculated_value=float(num_bolts),
                limit_value=2.0
            ))
        
        return checks
    
    def _validate_plate(self, params: Dict[str, Any]) -> List[RuleCheck]:
        checks = []
        
        plate_thickness = params.get('plate_thickness', 0.5)
        plate_grade = params.get('plate_grade', 'A36')
        plate_length = params.get('plate_length', 12.0)
        plate_width = params.get('plate_width', 6.0)
        
        if plate_thickness >= 0.1875:
            checks.append(RuleCheck(
                rule_id="AISC_PLATE_MIN",
                rule_name="Minimum Plate Thickness",
                status=RuleStatus.PASS,
                message=f"Plate thickness {plate_thickness:.3f} in >= 0.1875 in (3/16 in)",
                code_reference="AISC 360-16 J4",
                calculated_value=plate_thickness,
                limit_value=0.1875
            ))
        else:
            checks.append(RuleCheck(
                rule_id="AISC_PLATE_MIN",
                rule_name="Minimum Plate Thickness",
                status=RuleStatus.FAIL,
                message=f"Plate thickness {plate_thickness:.3f} in < 0.1875 in - VIOLATION",
                code_reference="AISC 360-16 J4",
                calculated_value=plate_thickness,
                limit_value=0.1875
            ))
        
        slenderness = plate_length / plate_thickness
        max_slenderness = 25.0
        if slenderness <= max_slenderness:
            checks.append(RuleCheck(
                rule_id="AISC_PLATE_SLENDER",
                rule_name="Plate Slenderness",
                status=RuleStatus.PASS,
                message=f"Plate slenderness {slenderness:.1f} <= {max_slenderness:.1f}",
                code_reference="AISC 360-16 B4",
                calculated_value=slenderness,
                limit_value=max_slenderness
            ))
        else:
            checks.append(RuleCheck(
                rule_id="AISC_PLATE_SLENDER",
                rule_name="Plate Slenderness",
                status=RuleStatus.WARNING,
                message=f"Plate slenderness {slenderness:.1f} > {max_slenderness:.1f} - Check buckling",
                code_reference="AISC 360-16 B4",
                calculated_value=slenderness,
                limit_value=max_slenderness
            ))
        
        return checks
    
    def _validate_geometry(self, params: Dict[str, Any]) -> List[RuleCheck]:
        checks = []
        
        beam_depth = params.get('beam_depth', 12.0)
        connection_depth = params.get('connection_depth', 10.0)
        
        if connection_depth <= beam_depth - 1.0:
            checks.append(RuleCheck(
                rule_id="AISC_GEOM_1",
                rule_name="Connection Depth Check",
                status=RuleStatus.PASS,
                message=f"Connection depth {connection_depth:.1f} in fits within beam depth {beam_depth:.1f} in",
                code_reference="AISC Design Guide 4",
                calculated_value=connection_depth,
                limit_value=beam_depth - 1.0
            ))
        else:
            checks.append(RuleCheck(
                rule_id="AISC_GEOM_1",
                rule_name="Connection Depth Check",
                status=RuleStatus.FAIL,
                message=f"Connection depth {connection_depth:.1f} in exceeds beam depth {beam_depth:.1f} in - VIOLATION",
                code_reference="AISC Design Guide 4",
                calculated_value=connection_depth,
                limit_value=beam_depth - 1.0
            ))
        
        return checks
    
    def _generate_summary(self, checks: List[RuleCheck], status: RuleStatus) -> str:
        total = len(checks)
        passed = sum(1 for c in checks if c.status == RuleStatus.PASS)
        failed = sum(1 for c in checks if c.status == RuleStatus.FAIL)
        warnings = sum(1 for c in checks if c.status == RuleStatus.WARNING)
        
        if status == RuleStatus.PASS:
            return f"All {total} AISC 360-16 checks passed. Connection is code-compliant."
        elif status == RuleStatus.FAIL:
            return f"{failed} critical rule(s) failed. Connection does NOT meet AISC 360-16 requirements. Human review required."
        else:
            return f"{passed} checks passed, {warnings} warning(s). Review recommended before fabrication."