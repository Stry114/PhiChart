import json
import chart as ch


def analyzeJson(jsonFile: str):
    f = open(jsonFile, encoding="utf-8")
    chart_ = json.load(f)
    chart = ch.Chart()
    f.close()

    for line_ in chart_["judgeLineList"]:
        bpm = float(line_["bpm"])
        line = ch.Line(bpm)
        
        # note
        for note_ in line_["notesAbove"]:
            note = ch.Note(
                type_ = int(note_["type"]),
                time_ = float(note_["time"]),
                speed = float(note_["speed"]),
                posX = float(note_["positionX"]),
                holdTime=float(note_["holdTime"]),
                floorPos = float(note_["floorPosition"]),
                above=True
            )
            line.addNote(note)
        for note_ in line_["notesBelow"]:
            note = ch.Note(
                type_ = int(note_["type"]),
                time_ = float(note_["time"]),
                speed = float(note_["speed"]),
                posX = float(note_["positionX"]),
                holdTime=float(note_["holdTime"]),
                floorPos = float(note_["floorPosition"]),
                above=False
            )
            line.addNote(note)

        # speed event
        for event in line_["speedEvents"]:
            line.speed.addPeriod(
                float(event["startTime"]),
                float(event["endTime"]),
                float(event["value"]),
                float(event["value"]),
            )

        # move event
        for event in line_["judgeLineMoveEvents"]:
            line.move1.addPeriod(
                float(event["startTime"]),
                float(event["endTime"]),
                float(event["start"]),
                float(event["end"]),
            )
            line.move2.addPeriod(
                float(event["startTime"]),
                float(event["endTime"]),
                float(event["start2"]),
                float(event["end2"]),
            )

        # rotate event
        for event in line_["judgeLineRotateEvents"]:
            line.rotate.addPeriod(
                float(event["startTime"]),
                float(event["endTime"]),
                float(event["start"]),
                float(event["end"]),
            )
        
        # alpha event
        for event in line_["judgeLineDisappearEvents"]:
            line.alpha.addPeriod(
                float(event["startTime"]),
                float(event["endTime"]),
                float(event["start"]),
                float(event["end"]),
            )
        
        chart.addLine(line)

    # 计算双押
    key = lambda note: note.time_
    chart.noteList.sort(key=key)
    for i in range(len(chart.noteList)-1):
        if chart.noteList[i].time_ == chart.noteList[i+1].time_:
            chart.noteList[i].doubleHit = True
            chart.noteList[i+1].doubleHit = True

    return chart

if __name__ == "__main__":
    chart = analyzeJson("Chart analyze/Chart_AT #4757.json")
    chart.report()