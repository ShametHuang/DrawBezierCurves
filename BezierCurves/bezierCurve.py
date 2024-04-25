from basicettings import *

STEP_SIZE = 1.0 / 100.0;

class BezierCurve():
    # 是否渲染中间点
    intermediateRendering = False
    # 中间点步长
    intermediateStep = 0.50
    # 中间点颜色调色板
    intermediateColorPalette = ["green", "red", "blue", "cyan", "magenta"]

    def __init__(self, firstPoint):
        # 控制点列表，初始时包含第一个点
        self.points = [firstPoint]
        # 是否需要重新渲染曲线
        self.needsRender = True
        # 是否需要重新渲染中间点
        self.needsIntermediateRender = True
        # 曲线上的点列表
        self.curvePoints = []
        # 中间点列表
        self.intermediatePoints = []

    def render(self, canvas):
        # 绘制控制点之间的虚线
        if len(self.points) > 1:
            drawDashedLine(canvas, self.points, "gray")

        # 绘制实际的贝塞尔曲线
        self.renderCurve(canvas)

        # 绘制控制点
        for point in self.points:
            drawPoint(canvas, point, "black")

        # 绘制中间点
        self.renderIntermediates(canvas)

    # 渲染贝塞尔曲线
    def renderCurve(self, canvas):
        if self.needsRender:
            currentStep = 0.0
            self.curvePoints = []

            while currentStep < 1.0 or areFloatsEqual(currentStep, 1.0):
                pointOnCurve = self.getPointOnCurveAtStep(canvas, self.points, currentStep)
                self.curvePoints.append(pointOnCurve)
                currentStep += STEP_SIZE

            self.curvePoints.append(self.points[-1])
            self.needsRender = False

        drawLine(canvas, self.curvePoints, "black")

    # 获取曲线上指定步长处的点
    def getPointOnCurveAtStep(self, canvas, points, step):
        if len(points) == 1:
            return points[0]
        else:
            intermediatePoints = []

            for i, point in enumerate(points[:-1]):
                newPoint = pointBetweenPoints(point, points[i + 1], step)
                intermediatePoints.append(newPoint)

            return self.getPointOnCurveAtStep(canvas, intermediatePoints, step)

    # 渲染中间点和中间线
    def renderIntermediates(self, canvas):
        if not BezierCurve.intermediateRendering:
            return

        if self.needsIntermediateRender:
            self.intermediatePoints = []
            self.calculateIntermediates(canvas, self.points)
            self.needsIntermediateRender = False

        for intermediates in self.intermediatePoints:
            intermediateColor = BezierCurve.intermediateColorPalette[len(intermediates) % len(BezierCurve.intermediateColorPalette)]

            if len(intermediates) > 1:
                drawLine(canvas, intermediates, intermediateColor)

            for point in intermediates:
                drawPoint(canvas, point, intermediateColor)

    # 计算中间点
    def calculateIntermediates(self, canvas, pointsToRender):
        if len(pointsToRender) <= 0:
            return

        nextIntermediates = []
        for i, point in enumerate(pointsToRender[:-1]):
            newPoint = pointBetweenPoints(point, pointsToRender[i + 1], BezierCurve.intermediateStep)
            nextIntermediates.append(newPoint)

        self.intermediatePoints.append(nextIntermediates)
        self.calculateIntermediates(canvas, nextIntermediates)

    # 设置需要重新渲染
    def setNeedsRender(self):
        self.needsRender = True
        self.setNeedsIntermediateRender()

    # 设置需要重新渲染中间点
    def setNeedsIntermediateRender(self):
        self.needsIntermediateRender = True

    # 添加控制点
    def addPoint(self, point):
        self.points.append(point)
        self.setNeedsRender()

    # 移除最后一个控制点
    def removeLastPoint(self):
        self.points.pop()
        self.setNeedsRender()

    # 获取距离给定点最近的曲线上的点
    def closestPointTo(self, point):
        closestPoint = None
        closestDistance = None

        for curvePoint in self.points:
            distance = curvePoint.distanceTo(point)
            if closestDistance is None or distance < closestDistance:
                closestPoint = curvePoint
                closestDistance = distance

        return (closestPoint, closestDistance)
