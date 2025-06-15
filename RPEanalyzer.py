import json
import chart as ch


def beatToTimeT(beat: list[int, int, int], line):
    return (beat[0]+(beat[1]/beat[2])) * 32

def convertType(RPE_Type:int) -> int:
    if RPE_Type == 2:
        return 3
    elif RPE_Type == 3:
        return 4
    elif RPE_Type == 4:
        return 2
    return 1


def analyzeJson(jsonFile: str):
    f = open(jsonFile, encoding="utf-8")
    chart_ = json.load(f)
    chart = ch.Chart()
    chart.RPE_Chart = True
    f.close()

    chart.bpm = float(chart_["BPMList"][0]["bpm"])

    for line_ in chart_["judgeLineList"]:
        bpm = float(line_["bpmfactor"]) * chart.bpm
        line = ch.Line(bpm)

        # speed event
        for event in line_["eventLayers"][0]["speedEvents"]:
            line.speed.addPeriod(
                float(beatToTimeT(event["startTime"], line)),
                float(beatToTimeT(event["endTime"], line)),
                float(event["start"])*2/9,
                float(event["end"])*2/9,
            )

        # move event
        for event in line_["eventLayers"][0]["moveXEvents"]:
            line.move1.addPeriod(
                float(beatToTimeT(event["startTime"], line)),
                float(beatToTimeT(event["endTime"], line)),
                float(event["start"])/1350+0.5,
                float(event["end"])/1350+0.5,
            )
        for event in line_["eventLayers"][0]["moveYEvents"]:
            line.move2.addPeriod(
                float(beatToTimeT(event["startTime"], line)),
                float(beatToTimeT(event["endTime"], line)),
                float(event["start"])/900+0.5,
                float(event["end"])/900+0.5,
            )

        # rotate event
        for event in line_["eventLayers"][0]["rotateEvents"]:
            line.rotate.addPeriod(
                float(beatToTimeT(event["startTime"], line)),
                float(beatToTimeT(event["endTime"], line)),
                360-float(event["start"]),
                360-float(event["end"]),
            )

        # alpha event
        for event in line_["eventLayers"][0]["alphaEvents"]:
            line.alpha.addPeriod(
                float(beatToTimeT(event["startTime"], line)),
                float(beatToTimeT(event["endTime"], line)),
                float(event["start"])/255,
                float(event["end"])/255,
            )

            # note
        if "notes" in line_:
            for note_ in line_["notes"]:
                timeT_1 = beatToTimeT(note_['startTime'], line)
                timeT_2 = beatToTimeT(note_['endTime'], line)
                above = True if note_['above'] else False
                floorPos = line.pos(timeT_1)
                floorPosT = line.pos(timeT_2)

                note = ch.Note(
                    above=above,
                    floorPos=floorPos,
                    time_=timeT_1,
                    holdTime=timeT_2 - timeT_1,
                    type_=convertType(int(note_["type"])),
                    speed=float(note_["speed"]),
                    posX=float(note_["positionX"])/75.951,
                )
                if note.type_ == 3:
                    note.floorPosT = floorPosT

                line.addNote(note)
        
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
    chart = analyzeJson("D:/phigros/谱面/领土战争AT/29519800.json")
    f = open("chart.json", "w", encoding="utf-8")
    f.write(chart.toJson())
    f.close()
