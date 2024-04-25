import math

# 全局变量
POINT_RADIUS = 3

class Point:
    """用于存储和操作二维坐标点的类"""

    def __init__(self, x, y):
        """初始化点的x和y坐标"""
        self.x = x
        self.y = y

    def set(self, otherPoint):
        """设置当前点的坐标为另一个点的坐标"""
        self.x = otherPoint.x
        self.y = otherPoint.y

    def distanceTo(self, otherPoint):
        """计算当前点到另一个点的距离"""
        return math.sqrt((self.x - otherPoint.x) ** 2 + (self.y - otherPoint.y) ** 2)

def drawPoint(canvas, point, color):
    """在画布上绘制一个点"""
    canvas.create_oval(point.x - POINT_RADIUS, point.y - POINT_RADIUS,
                       point.x + POINT_RADIUS, point.y + POINT_RADIUS,
                       outline=color, fill="white")

def drawLine(canvas, points, color):
    """在画布上绘制一条由多个点组成的连续线"""
    pointCoords = buildCoordinatesListFromPoints(points)
    canvas.create_line(pointCoords, fill=color)

def drawDashedLine(canvas, points, color):
    """在画布上绘制一条由多个点组成的虚线"""
    pointCoords = buildCoordinatesListFromPoints(points)
    canvas.create_line(pointCoords, dash=(4, 4), fill=color)

def buildCoordinatesListFromPoints(points):
    """根据点列表构建坐标列表（用于绘制线条）"""
    pointCoords = []
    for point in points:
        pointCoords.extend([point.x, point.y])
    return pointCoords

def pointBetweenPoints(point1, point2, proportion):
    """返回两个点之间的比例点"""
    xDifference = point2.x - point1.x
    yDifference = point2.y - point1.y
    xOffset = xDifference * proportion
    yOffset = yDifference * proportion
    return Point(point1.x + xOffset, point1.y + yOffset)

def clampPointToBounds(point, boundX, boundY, margin):
    """确保点不超出给定的边界"""
    point.x = max(margin, min(point.x, boundX - margin))
    point.y = max(margin, min(point.y, boundY - margin))

def areFloatsEqual(float1, float2):
    """比较两个浮点数是否相等（考虑浮点误差）"""
    return abs(float1 - float2) < 0.001
