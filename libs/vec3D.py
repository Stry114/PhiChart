import math


class V3d:

    def __init__(self, x: float, y: float, z: float):
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def __abs__(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def __add__(self, other: "V3d") -> "V3d":
        return V3d(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "V3d") -> "V3d":
        return V3d(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other: "V3d") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __rmul__(self, other: float) -> "V3d":
        return V3d(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other: float) -> "V3d":
        return V3d(self.x / other, self.y / other, self.z / other)

    def __xor__(self, other: "V3d") -> "V3d":
        return V3d(self.y * other.z - self.z * other.y,
                   self.z * other.x - self.x * other.z,
                   self.x * other.y - self.y * other.x)

    @property
    def direction(self) -> "V3d":
        length = abs(self)
        if length == 0:
            return V3d(0, 0, 0)
        return self / length
    
    def __repr__(self) -> str:
        return f"V3d({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def roundStr(self) -> str:
        return f"({self.x:.0f}, {self.y:.0f}, {self.z:.0f})"

    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.z)
    
    @staticmethod
    def from_tuple(t: tuple) -> "V3d":
        return V3d(t[0], t[1], t[2])

    @staticmethod
    def normal(vec1, vec2):
        # 法向量 normal vector
        x = vec1.z * vec2.y - vec1.y * vec2.z
        y = vec1.x * vec2.z - vec1.z * vec2.x
        z = vec1.y * vec2.x - vec1.x * vec2.y
        return V3d(x, y, z)
    
    def distance_to(self, other: "V3d") -> float:
        return abs(self - other)
    
    def angle_with(self, other: "V3d") -> float:
        dot_product = self * other
        lengths_product = abs(self) * abs(other)
        if lengths_product == 0:
            return 0.0
        cos_angle = max(-1.0, min(1.0, dot_product / lengths_product))
        return math.acos(cos_angle)
    
    def project_onto(self, other: "V3d") -> "V3d":
        other_length_squared = other * other
        if other_length_squared == 0:
            return V3d(0, 0, 0)
        projection_scale = (self * other) / other_length_squared
        return projection_scale * other
    
    def reflect(self, normal: "V3d") -> "V3d":
        return self - 2 * (self * normal) * normal


