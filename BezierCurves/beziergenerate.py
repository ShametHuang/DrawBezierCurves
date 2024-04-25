import time
from tkinter import *

from basicettings import *
from bezierCurve import *
from openpyxl import Workbook
# 一些用于控制行为的常量

WINDOW_WIDTH = 1000  # 窗口宽度
WINDOW_HEIGHT = 600  # 窗口高度

TARGET_FRAME_TIME = 20  # 目标帧时间

MOVEMENT_CLICK_RADIUS = 7  # 移动点击半径
BORDER_MARGIN = 5  # 边界边距

# 跟踪全局状态

STATE_IDLE = 0  # 空闲状态
STATE_PLACING = 1  # 放置状态
STATE_MOVING = 2  # 移动状态
state = STATE_IDLE  # 初始状态为IDLE

# 一些全局变量

bezierCurves = []  # 贝塞尔曲线列表

curveBeingPlaced = None  # 正在放置的曲线
curveBeingMoved = None  # 正在移动的曲线
pointBeingMoved = None  # 正在移动的点

# 创建窗口并添加画布

master = Tk()
master.resizable(width=False, height=False)  # 不允许改变窗口大小
canvas = Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)  # 创建画布
canvas.pack()

# 渲染曲线

def renderAll():
    global canvas
    global bezierCurves

    startTime = time.time()

    canvas.delete("all")  # 清空画布
    all_interpolated_points = []  # 存储所有插值点的列表

    for bezierCurve in bezierCurves:
        bezierCurve.render(canvas)  # 渲染每条贝塞尔曲线
        all_interpolated_points.extend(bezierCurve.curvePoints)  # 将插值点添加到列表中

    # 控制帧速率
    secondsElapsed = time.time() - startTime
    millisecondsElapsed = int(round(secondsElapsed))
    frameTime = max(0, TARGET_FRAME_TIME - millisecondsElapsed)

    # 继续循环渲染
    master.after(frameTime, renderAll)

    # 将插值点写入 Excel 文件
    writeInterpolatedPointsToExcel(all_interpolated_points)

# 将插值点写入 Excel 文件
def writeInterpolatedPointsToExcel(interpolated_points):
    wb = Workbook()
    ws = wb.active

    # 写入表头
    ws.append(['X', 'Y'])

    # 写入插值点
    for point in interpolated_points:
        ws.append([point.x, point.y])

    # 保存 Excel 文件
    wb.save("interpolated_points.xlsx")

# 处理鼠标输入

def mouseClicked(event):
    global state

    clickPoint = Point(event.x, event.y)
    clampPointToBounds(clickPoint, WINDOW_WIDTH, WINDOW_HEIGHT, BORDER_MARGIN)

    if state is STATE_IDLE:
        point, bezierCurve = getNearbyBezierCurve(clickPoint)
        if bezierCurve is not None:
            startMovingPointOnCurve(point, bezierCurve)
        else:
            startPlacingNewBezierCurve(clickPoint)
    elif state is STATE_PLACING:
        continuePlacingNewBezierCurve(clickPoint)
    elif state is STATE_MOVING:
        stopMovingPointOnCurve()

def mouseMoved(event):
    global state
    global curveBeingPlaced
    global curveBeingMoved
    global pointBeingMoved

    mousePos = Point(event.x, event.y)
    clampPointToBounds(mousePos, WINDOW_WIDTH, WINDOW_HEIGHT, BORDER_MARGIN)

    if state is STATE_PLACING:
        curveBeingPlaced.removeLastPoint()
        curveBeingPlaced.addPoint(mousePos)
    elif state is STATE_MOVING:
        pointBeingMoved.set(mousePos)
        curveBeingMoved.setNeedsRender()

# 获取靠近点击位置的曲线上的点

def getNearbyBezierCurve(clickPoint):
    global bezierCurves

    closestCurve = None
    closestDistance = None
    closestPoint = None

    for bezierCurve in bezierCurves:
        point, distance = bezierCurve.closestPointTo(clickPoint)
        if closestDistance is None or distance < closestDistance:
            closestCurve = bezierCurve
            closestDistance = distance
            closestPoint = point

    if closestDistance is not None and closestDistance < MOVEMENT_CLICK_RADIUS:
        return (closestPoint, closestCurve)
    else:
        return (None, None)

# 处理放置新曲线

def startPlacingNewBezierCurve(clickPoint):
    global state
    global bezierCurves
    global curveBeingPlaced

    state = STATE_PLACING

    newCurve = BezierCurve(clickPoint)
    newCurve.addPoint(Point(clickPoint.x, clickPoint.y))

    bezierCurves.append(newCurve)
    curveBeingPlaced = newCurve

def continuePlacingNewBezierCurve(clickPoint):
    global curveBeingPlaced

    curveBeingPlaced.addPoint(Point(clickPoint.x, clickPoint.y))

def placeKeyPressed(event):
    if state is STATE_PLACING:
        stopPlacingNewBezierCurve()

def stopPlacingNewBezierCurve():
    global state
    global curveBeingPlaced

    if curveBeingPlaced is not None:
        curveBeingPlaced.removeLastPoint()

    state = STATE_IDLE
    curveBeingPlaced = None

# 处理移动现有曲线上的点

def startMovingPointOnCurve(point, curve):
    global state
    global pointBeingMoved
    global curveBeingMoved

    state = STATE_MOVING
    pointBeingMoved = point
    curveBeingMoved = curve

def stopMovingPointOnCurve():
    global state
    global curveBeingMoved
    global pointTypeBeingMoved

    state = STATE_IDLE
    curveBeingMoved = None
    pointBeingMoved = None

# 控制是否绘制中间线以及绘制的位置

def toggleIntermediateRendering(event):
    global bezierCurves

    BezierCurve.intermediateRendering = not BezierCurve.intermediateRendering
    for bezierCurve in bezierCurves:
        bezierCurve.setNeedsIntermediateRender()

def moveIntermediates(event):
    if event.keysym == "Right":
        BezierCurve.intermediateStep += 0.01
    elif event.keysym == "Left":
        BezierCurve.intermediateStep -= 0.01

    if BezierCurve.intermediateStep < 0.0:
        BezierCurve.intermediateStep = 0.0;
    elif BezierCurve.intermediateStep > 1.0:
        BezierCurve.intermediateStep = 1.0

    for bezierCurve in bezierCurves:
        bezierCurve.setNeedsIntermediateRender()

# 清空画布和退出程序

def clear(event):
    global bezierCurves

    if state is STATE_IDLE:
        del(bezierCurves[:])

def quit(event):
    master.quit()

# 绑定事件处理函数

master.bind("<Button-1>", mouseClicked)
master.bind("<Motion>", mouseMoved)
master.bind("p", placeKeyPressed)
master.bind("i", toggleIntermediateRendering)
master.bind("<Left>", moveIntermediates)
master.bind("<Right>", moveIntermediates)
master.bind("c", clear)
master.bind("q", quit)

# 开始渲染

master.after(TARGET_FRAME_TIME, renderAll)

mainloop()
