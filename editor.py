from tkinter import *
from tkinter import ttk

import analyzer
import autoMatch
import chart
import tk.timelineEditor


top = Tk()
top.geometry('800x1000')


autoMatcher = autoMatch.Matcher("charts/2085 AT/")
myChart: chart.Chart = analyzer.analyzeJson(autoMatcher.chartFile)
editor: tk.timelineEditor = tk.timelineEditor.TimelineEditor(top, myChart, 0)


mainloop()