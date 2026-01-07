from typing import Dict, Any, List
from .components import Bolt, Plate, Weld, Point3D

class GeometryGenerator:
    
    @staticmethod
    def generate_connection(connection_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if connection_type == "single_plate":
            return GeometryGenerator._generate_single_plate(parameters)
        elif connection_type == "double_angle":
            return GeometryGenerator._generate_double_angle(parameters)
        elif connection_type == "end_plate":
            return GeometryGenerator._generate_end_plate(parameters)
        elif connection_type in ["beam_to_column_shear", "beam_to_beam_shear"]:
            return GeometryGenerator._generate_shear_connection(parameters)
        else:
            return {"error": "Unknown connection type"}
    
    @staticmethod
    def _generate_single_plate(params: Dict[str, Any]) -> Dict[str, Any]:
        num_bolts = params.get('num_bolts', 4)
        bolt_diameter = params.get('bolt_diameter', 0.75)
        bolt_spacing = params.get('bolt_spacing', 3.0)
        edge_distance = params.get('edge_distance', 1.5)
        plate_thickness = params.get('plate_thickness', 0.375)
        plate_width = params.get('plate_width', 5.0)
        
        plate_length = (num_bolts - 1) * bolt_spacing + 2 * edge_distance
        
        plate = Plate(
            length=plate_length,
            width=plate_width,
            thickness=plate_thickness,
            material=params.get('plate_grade', 'A36'),
            corner_points=[
                Point3D(x=0, y=0, z=0),
                Point3D(x=plate_length, y=0, z=0),
                Point3D(x=plate_length, y=plate_width, z=0),
                Point3D(x=0, y=plate_width, z=0)
            ]
        )
        
        bolts = []
        for i in range(num_bolts):
            y_pos = edge_distance + i * bolt_spacing
            bolts.append(Bolt(
                position=Point3D(x=plate_width/2, y=y_pos, z=0),
                diameter=bolt_diameter,
                grade=params.get('bolt_grade', 'A325')
            ))
        
        return {
            "type": "single_plate",
            "plate": plate.model_dump(),
            "bolts": [b.model_dump() for b in bolts],
            "dimensions": {
                "plate_length": plate_length,
                "plate_width": plate_width,
                "plate_thickness": plate_thickness,
                "num_bolts": num_bolts
            }
        }
    
    @staticmethod
    def _generate_double_angle(params: Dict[str, Any]) -> Dict[str, Any]:
        num_bolts = params.get('num_bolts', 4)
        bolt_diameter = params.get('bolt_diameter', 0.75)
        bolt_spacing = params.get('bolt_spacing', 3.0)
        edge_distance = params.get('edge_distance', 1.5)
        angle_size = params.get('angle_size', '4x4x3/8')
        
        angle_length = (num_bolts - 1) * bolt_spacing + 2 * edge_distance
        
        bolts = []
        for i in range(num_bolts):
            y_pos = edge_distance + i * bolt_spacing
            bolts.append(Bolt(
                position=Point3D(x=2, y=y_pos, z=0),
                diameter=bolt_diameter,
                grade=params.get('bolt_grade', 'A325')
            ))
        
        return {
            "type": "double_angle",
            "angle_size": angle_size,
            "angle_length": angle_length,
            "bolts": [b.model_dump() for b in bolts],
            "num_angles": 2,
            "dimensions": {
                "angle_length": angle_length,
                "num_bolts_per_angle": num_bolts
            }
        }
    
    @staticmethod
    def _generate_end_plate(params: Dict[str, Any]) -> Dict[str, Any]:
        num_bolts_vertical = params.get('num_bolts_vertical', 4)
        num_bolts_horizontal = params.get('num_bolts_horizontal', 2)
        bolt_diameter = params.get('bolt_diameter', 0.875)
        bolt_spacing_v = params.get('bolt_spacing_vertical', 3.0)
        bolt_spacing_h = params.get('bolt_spacing_horizontal', 3.5)
        edge_distance = params.get('edge_distance', 1.75)
        plate_thickness = params.get('plate_thickness', 0.5)
        
        plate_length = (num_bolts_vertical - 1) * bolt_spacing_v + 2 * edge_distance
        plate_width = (num_bolts_horizontal - 1) * bolt_spacing_h + 2 * edge_distance
        
        plate = Plate(
            length=plate_length,
            width=plate_width,
            thickness=plate_thickness,
            material=params.get('plate_grade', 'A36'),
            corner_points=[
                Point3D(x=0, y=0, z=0),
                Point3D(x=plate_length, y=0, z=0),
                Point3D(x=plate_length, y=plate_width, z=0),
                Point3D(x=0, y=plate_width, z=0)
            ]
        )
        
        bolts = []
        for i in range(num_bolts_vertical):
            for j in range(num_bolts_horizontal):
                y_pos = edge_distance + i * bolt_spacing_v
                x_pos = edge_distance + j * bolt_spacing_h
                bolts.append(Bolt(
                    position=Point3D(x=x_pos, y=y_pos, z=0),
                    diameter=bolt_diameter,
                    grade=params.get('bolt_grade', 'A490')
                ))
        
        return {
            "type": "end_plate",
            "plate": plate.model_dump(),
            "bolts": [b.model_dump() for b in bolts],
            "dimensions": {
                "plate_length": plate_length,
                "plate_width": plate_width,
                "plate_thickness": plate_thickness,
                "total_bolts": len(bolts)
            }
        }
    
    @staticmethod
    def _generate_shear_connection(params: Dict[str, Any]) -> Dict[str, Any]:
        connection_subtype = params.get('subtype', 'single_plate')
        if connection_subtype == 'single_plate':
            return GeometryGenerator._generate_single_plate(params)
        else:
            return GeometryGenerator._generate_double_angle(params)