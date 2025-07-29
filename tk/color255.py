from random import random, randint, shuffle

hexSymbList = list("0123456789abcdefABCDEF")
hexToDecDictionary = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "a": 10,
    "b": 11,
    "c": 12,
    "d": 13,
    "e": 14,
    "f": 15,
    "A": 10,
    "B": 11,
    "C": 12,
    "D": 13,
    "E": 14,
    "F": 15,
}

defaultColor = [
    "#FFA500",
    "#008000",
    "#FF69B4",
    "#CD5C5C",
    "#20B2AA",
    "#0000CD",
    "#FF0000",
    "#FF6347",
    "#912CEE",
    "#836FFF",
    "#4169E1",
    "#A0522D",
]


def hexToDec(Hex: str):
    outputValue = 0
    position = len(Hex)
    for i in Hex:
        position -= 1
        outputValue += hexToDecDictionary[i] * (16 ** position)
    return outputValue


def formatHex(Hex: str, minLenth=None):
    Hex = Hex.replace("0x", "")
    if minLenth != None:
        delta = minLenth - len(Hex)
        if delta > 0:
            Hex = "0" * delta + Hex
    return Hex


def confirmColorType(color: str):
    if color[0] == "#" and len(color) == 4:
        for i in color[1:4]:
            if not i in hexSymbList:
                return "not_a_color"
        return "#rgb"
    elif color[0] == "#" and len(color) == 5:
        for i in color[1:5]:
            if not i in hexSymbList:
                return "not_a_color"
        return "#rgba"
    elif color[0] == "#" and len(color) == 7:
        for i in color[1:7]:
            if not i in hexSymbList:
                return "not_a_color"
        return "#rrggbb"
    elif color[0] == "#" and len(color) == 9:
        for i in color[1:9]:
            if not i in hexSymbList:
                return "not_a_color"
        return "#rrggbbaa"
    elif color == "red":
        return "#ff0000ff"
    elif color == "green":
        return "#00ff00ff"
    elif color == "blue":
        return "#0000ffff"
    return "not_a_color"


class Color:
    r = 0
    g = 0
    b = 0
    alpha = 0

    def __init__(self, color: str = None, r=None, g=None, b=None, alpha=1):
        self.r = 0
        self.g = 0
        self.b = 0
        self.alpha = 0

        if r != None and g != None and b != None:
            self.r = r
            self.g = g
            self.b = b
            self.alpha = alpha
            return
        if color is None:
            raise TypeError("'Color' object is missing numeric values for initialization.")
        colorType = confirmColorType(color)
        if colorType == "#rgb":
            self.r = hexToDec(color[1]) * 17
            self.g = hexToDec(color[2]) * 17
            self.b = hexToDec(color[3]) * 17
            self.alpha = 1
        elif colorType == "#rgba":
            self.r = hexToDec(color[1]) * 17
            self.g = hexToDec(color[2]) * 17
            self.b = hexToDec(color[3]) * 17
            self.alpha = hexToDec(color[4]) / 15
        elif colorType == "#rrggbb":
            self.r = hexToDec(color[1:3])
            self.g = hexToDec(color[3:5])
            self.b = hexToDec(color[5:7])
            self.alpha = 1
        elif colorType == "#rrggbbaa":
            self.r = hexToDec(color[1:3])
            self.g = hexToDec(color[3:5])
            self.b = hexToDec(color[5:7])
            self.alpha = hexToDec(color[7:9]) / 255
        elif colorType == "not_a_color":
            raise ValueError(f'"{color}" is not a valid RGB color.')
        else:
            self.r = hexToDec(colorType[1:3])
            self.g = hexToDec(colorType[3:5])
            self.b = hexToDec(colorType[5:7])
            self.alpha = hexToDec(colorType[7:9]) / 255

    def toAutoString(self):
        if self.alpha == 1:
            if self.r % 17 == 0 and self.g % 17 == 0 and self.b % 17 == 0:
                return self.toRGB()
            else:
                return self.toRRGGBB()
        else:
            if self.r % 17 == 0 and self.g % 17 == 0 and self.b % 17 == 0:
                return self.toRGBA()
            else:
                return self.toRRGGBBAA()

    def __add__(self, other):
        r = self.r + other.r
        g = self.g + other.g
        b = self.b + other.b
        a = self.alpha + other.alpha
        if (r > 255) or (g > 255) or (b > 255) or (a > 1):
            raise ValueError("Some value is out of range. Please check that the operation logic is correct.")
        if (r < 0) or (g < 0) or (b < 0) or (a < 0):
            raise ValueError("Some value is negative. Please check that the operation logic is correct.")
        return Color(r=r, g=g, b=b, alpha=a)

    def __mul__(self, other: float):
        r = round(self.r * other)
        g = round(self.g * other)
        b = round(self.b * other)
        if (r > 255) or (g > 255) or (b > 255):
            raise ValueError("Some value is out of range. Please check that the operation logic is correct.")
        if (r < 0) or (g < 0) or (b < 0):
            raise ValueError("Some value is negative. Please check that the operation logic is correct.")
        return Color(r=r, g=g, b=b, alpha=self.alpha)

    def __rmul__(self, other: float):
        return self.__mul__(other)

    def mul(self, other: float, doAlphaCalculated=True):
        r = int(self.r * other)
        g = int(self.g * other)
        b = int(self.b * other)
        if doAlphaCalculated:
            a = self.alpha * other
        else:
            a = self.alpha
        if (r > 255) or (g > 255) or (b > 255) or (a > 1):
            raise ValueError("Some value is out of range. Please check that the operation logic is correct.")
        if (r < 0) or (g < 0) or (b < 0) or (a < 0):
            raise ValueError("Some value is negative. Please check that the operation logic is correct.")
        return Color(r=r, g=g, b=b, alpha=a)

    def mix(self, other, selfWeight=1, otherWeight=1):
        totalWeight = selfWeight + otherWeight
        return self.mul(selfWeight / totalWeight) + other.mul(otherWeight / totalWeight)

    def toRGB(self):
        outputResult = "#"
        outputResult += formatHex(hex(int(self.r / 16)))
        outputResult += formatHex(hex(int(self.g / 16)))
        outputResult += formatHex(hex(int(self.b / 16)))
        return outputResult

    def toRGBA(self):
        outputResult = "#"
        outputResult += formatHex(hex(int(self.r / 16)))
        outputResult += formatHex(hex(int(self.g / 16)))
        outputResult += formatHex(hex(int(self.b / 16)))
        outputResult += formatHex(hex(round(15 * self.alpha)))
        return outputResult

    def toRRGGBB(self):
        outputResult = "#"
        outputResult += formatHex(hex(self.r), 2)
        outputResult += formatHex(hex(self.g), 2)
        outputResult += formatHex(hex(self.b), 2)
        return outputResult

    def toRRGGBBAA(self):
        outputResult = "#"
        outputResult += formatHex(hex(self.r), 2)
        outputResult += formatHex(hex(self.g), 2)
        outputResult += formatHex(hex(self.b), 2)
        outputResult += formatHex(hex(round(255 * self.alpha)), 2)
        return outputResult

    def __str__(self) -> str:
        return f"<Color {self.toRRGGBBAA()}>"

    def __repr__(self) -> str:
        return f"<Color id={id(self)}>"


RED = Color("#f00")
BLUE = Color("#00f")
GREEN = Color("#0f0")
WHITE = Color("#fff")
BLACK = Color("#000")
YELLOW = Color("#ff0")
TIANYI = Color("#6cf")

GOLD = Color("#ffd700")
MIKU = Color("#39c5bb")

def randomColor() -> Color:
    return Color(
        r=randint(1, 255),
        g=randint(1, 255),
        b=randint(1, 255)
    )


def getColor() -> str:
    if len(defaultColor) != 0:
        shuffle(defaultColor)
        color = defaultColor[0]
        defaultColor.pop(0)
        return color
    else:
        return randomColor().toRRGGBB()