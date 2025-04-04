import os


class Matcher:
    def __init__(self, dir):
        self.chartFile = None
        self.audioFile = None
        self.illuFile = None

        for file in os.listdir(dir):
            if file.endswith(".wav"):
                self.audioFile = os.path.join(dir, file)
            elif file.endswith(".mp3"):
                self.audioFile = os.path.join(dir, file)
            elif file.endswith(".png"):
                self.illuFile = os.path.join(dir, file)
            elif file.endswith(".jpg"):
                self.chartFile = os.path.join(dir, file)
            elif file.endswith(".json"):
                self.chartFile = os.path.join(dir, file)
            elif not "." in file:
                self.chartFile = os.path.join(dir, file)

        if self.chartFile is None:
            raise Exception("No chart file found!")
        if self.audioFile is None:
            raise Exception("No audio file found!")
        if self.illuFile is None:
            raise Exception("No illu file found!")