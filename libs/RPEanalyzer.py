import json
import libs.chart as ch


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
    chart.offset = float(chart_["META"]["offset"])

    for line_ in chart_["judgeLineList"]:
        bpm = float(line_["bpmfactor"]) * chart.bpm
        line = ch.RPELine(bpm)

        if "attachUI" in line_:
            line.attachUI = line_["attachUI"]

        for i in range(len(line_["eventLayers"])):

            # 读取并创建事件层
            layer_ = line_["eventLayers"][i]
            if layer_ is None:
                continue
            layer = ch.EventLayer(bpm)
            line.eventLayers.append(layer)

            # speed event
            if "speedEvents" in line_["eventLayers"][i]:
                for event in line_["eventLayers"][i]["speedEvents"]:
                    layer.speed.addPeriod(
                        float(beatToTimeT(event["startTime"], line)),
                        float(beatToTimeT(event["endTime"], line)),
                        float(event["start"])*2/9,
                        float(event["end"])*2/9,
                    )

            # move event
            if "moveXEvents" in line_["eventLayers"][i]:
                for event in line_["eventLayers"][i]["moveXEvents"]:
                    layer.move1.addPeriod(
                        float(beatToTimeT(event["startTime"], line)),
                        float(beatToTimeT(event["endTime"], line)),
                        float(event["start"])/1350+0.5,
                        float(event["end"])/1350+0.5,
                        int(event["easingType"]),
                    )
            if "moveYEvents" in line_["eventLayers"][i]:
                for event in line_["eventLayers"][i]["moveYEvents"]:
                    layer.move2.addPeriod(
                        float(beatToTimeT(event["startTime"], line)),
                        float(beatToTimeT(event["endTime"], line)),
                        float(event["start"])/900+0.5,
                        float(event["end"])/900+0.5,
                        int(event["easingType"]),
                    )

            # rotate event
            if "rotateEvents" in line_["eventLayers"][i]:
                for event in line_["eventLayers"][i]["rotateEvents"]:
                    layer.rotate.addPeriod(
                        float(beatToTimeT(event["startTime"], line)),
                        float(beatToTimeT(event["endTime"], line)),
                        360-float(event["start"]),
                        360-float(event["end"]),
                        int(event["easingType"]),
                    )

            # alpha event
            if "alphaEvents" in line_["eventLayers"][i]:
                for event in line_["eventLayers"][i]["alphaEvents"]:
                    layer.alpha.addPeriod(
                        float(beatToTimeT(event["startTime"], line)),
                        float(beatToTimeT(event["endTime"], line)),
                        float(event["start"])/255,
                        float(event["end"])/255,
                        int(event["easingType"]),
                    )

        # scale X event
        if "scaleXEvents" in line_["extended"]:
            for event in line_["extended"]["scaleXEvents"]:
                line.scaleX.addPeriod(
                    float(beatToTimeT(event["startTime"], line)),
                    float(beatToTimeT(event["endTime"], line)),
                    float(event["start"]),
                    float(event["end"]),
                    int(event["easingType"]),
                )

        # scale Y event
        if "scaleYEvents" in line_["extended"]:
            for event in line_["extended"]["scaleYEvents"]:
                line.scaleY.addPeriod(
                    float(beatToTimeT(event["startTime"], line)),
                    float(beatToTimeT(event["endTime"], line)),
                    float(event["start"]),
                    float(event["end"]),
                    int(event["easingType"]),
                )

        # scale Y event
        if "colorEvents" in line_["extended"]:
            for event in line_["extended"]["colorEvents"]:
                line.color.addPeriod(
                    float(beatToTimeT(event["startTime"], line)),
                    float(beatToTimeT(event["endTime"], line)),
                    event["start"],
                    event["end"],
                    int(event["easingType"]),
                )

        # note
        if "notes" in line_:
            for note_ in line_["notes"]:
                timeT_1 = beatToTimeT(note_['startTime'], line)
                timeT_2 = beatToTimeT(note_['endTime'], line)
                above = True if note_['above']==1 else False
                floorPos = line.pos(timeT_1, True)
                floorPosT = line.pos(timeT_2, True)

                note = ch.Note(
                    above=above,
                    floorPos=floorPos,
                    time_=timeT_1,
                    holdTime=timeT_2 - timeT_1,
                    type_=convertType(int(note_["type"])),
                    speed=float(note_["speed"]),
                    posX=float(note_["positionX"])/75.951,
                )
                note.alpha = note_["alpha"]
                if note.type_ == 3:
                    note.floorPosT = floorPosT

                line.addNote(note)

        # Controls 控制器
        for i in range(len(line_["alphaControl"]) - 1):
            x1 = line_["alphaControl"][i]["x"]
            x2 = line_["alphaControl"][i+1]["x"]
            v1 = line_["alphaControl"][i]["alpha"]
            v2 = line_["alphaControl"][i+1]["alpha"]
            easing = line_["alphaControl"][i]["easing"]
            line.alphaControl.addPeriod(x1, v1, x2, v2, easing)

        for i in range(len(line_["sizeControl"]) - 1):
            x1 = line_["sizeControl"][i]["x"]
            x2 = line_["sizeControl"][i+1]["x"]
            v1 = line_["sizeControl"][i]["size"]
            v2 = line_["sizeControl"][i+1]["size"]
            easing = line_["sizeControl"][i]["easing"]
            line.sizeControl.addPeriod(x1, v1, x2, v2, easing)

        for i in range(len(line_["posControl"]) - 1):
            x1 = line_["posControl"][i]["x"]
            x2 = line_["posControl"][i+1]["x"]
            v1 = line_["posControl"][i]["pos"]
            v2 = line_["posControl"][i+1]["pos"]
            easing = line_["posControl"][i]["easing"]
            line.posControl.addPeriod(x1, v1, x2, v2, easing)

        for i in range(len(line_["yControl"]) - 1):
            x1 = line_["yControl"][i]["x"]
            x2 = line_["yControl"][i+1]["x"]
            v1 = line_["yControl"][i]["y"]
            v2 = line_["yControl"][i+1]["y"]
            easing = line_["yControl"][i]["easing"]
            line.sizeControl.addPeriod(x1, v1, x2, v2, easing)
        
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
