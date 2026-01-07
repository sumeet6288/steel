from pydantic import BaseModel
from typing import List, Tuple

class Point3D(BaseModel):
    x: float
    y: float
    z: float

class Bolt(BaseModel):
    position: Point3D
    diameter: float
    grade: str
    hole_type: str = "standard"

class Plate(BaseModel):
    length: float
    width: float
    thickness: float
    material: str
    corner_points: List[Point3D] = []

class Weld(BaseModel):
    start_point: Point3D
    end_point: Point3D
    weld_size: float
    weld_type: str = "fillet"