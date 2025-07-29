import random


class ColorMixer255:
    R = 0
    G = 0
    B = 0
    version = "P0"
    VersionIndex = 0.1
    VersionNumber = "0"

    def __init__(self, R=0, G=0, B=0) -> None:
        self.R = R
        self.G = G
        self.B = B

    def SetRGB6(self, RGB: str) -> None:
        RGB = RGB.lstrip("#")
        R = RGB[0:2]
        G = RGB[2:4]
        B = RGB[4:6]
        self.R = int(R, 16)
        self.G = int(G, 16)
        self.B = int(B, 16)

    def ToRGB(self):
        R = hex(self.R)[2:]
        G = hex(self.G)[2:]
        B = hex(self.B)[2:]
        if len(R) == 1:
            R = "0"+R
        if len(G) == 1:
            G = "0"+G
        if len(B) == 1:
            B = "0"+B
        return "#"+R+G+B

    def brightness(self, brightness):
        if brightness >= 0.5:
            return self.dark(2-brightness*2)
        elif brightness <= 0.5:
            return self.light(brightness*2)
        else:
            return self

    def __rmul__(self, number: float):
        R = min(255, round(self.R*number))
        G = min(255, round(self.G*number))
        B = min(255, round(self.B*number))
        return ColorMixer255(R, G, B)

    def light(self, brightness):
        if brightness > 1:
            brightness = 1
        R = round(self.R*(1-brightness) + 255*brightness)
        G = round(self.G*(1-brightness) + 255*brightness)
        B = round(self.B*(1-brightness) + 255*brightness)
        return ColorMixer255(R, G, B)

    def dark(self, darkness):
        R = round(self.R*darkness)
        G = round(self.G*darkness)
        B = round(self.B*darkness)
        return ColorMixer255(R, G, B)

    def mix(self, other, self_power=0.5):
        other_power = 1-self_power
        R = round(self.R * self_power + other.R * other_power)
        G = round(self.G * self_power + other.G * other_power)
        B = round(self.B * self_power + other.B * other_power)
        return ColorMixer255(R, G, B)

    def __str__(self) -> str:
        return f"<ColorMixer255> Obj: ({self.R},{self.G},{self.B}), {self.ToRGB()}"


def random_light_color():
    symbol1 = list("456789")
    symbol2 = list("9abcde")
    res = ["#"]
    for i in range(6):
        res.append(random.choice(symbol1))
    res[random.choice((1, 3, 5),)] = random.choice(symbol2)
    result = ColorMixer255()
    result.SetRGB6("".join(res))
    return result


if __name__ == "__main__":
    a = random_light_color()
    print(a)
