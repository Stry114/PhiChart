from libs.chart import *
import libs.analyzer
import libs.autoMatch
from mutagen import File
import os


PATH = r"D:\Projects\PygamePhiChart\charts\愚人节"




def get_audio_duration(file_path):
    try:
        audio = File(file_path)
        duration = audio.info.length  # 单位：秒
        return duration
    except Exception as e:
        print(f"读取失败: {e}")
        return None


def score_before_half(length_second: float, chartFile):
    chart = libs.analyzer.analyzeJson(chartFile)

    count = 0
    total = 0
    for line in chart.lineList:
        for note in line.noteList:
            t = note.time_ / chart.bpm * 1.875
            total += 1
            if t < length_second / 2:
                count += 1

    return round(100_0000 * count / total), total


for i in range(len(os.listdir(PATH))):
    dir = os.listdir(PATH)[-i-1]
    folder = os.path.join(PATH, dir)
    print(folder)
    matcher = libs.autoMatch.Matcher(folder)
    print(matcher.audioFile)
    print(matcher.illuFile)
    print(matcher.chartFile)

    length_second = get_audio_duration(matcher.audioFile)
    print("音频长度：", length_second)
    print("半条分数：", score_before_half(length_second, matcher.chartFile))