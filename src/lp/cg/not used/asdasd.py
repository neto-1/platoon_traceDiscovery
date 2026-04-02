import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from math import sqrt, sin, cos, tan, atan, pi
import numpy as np
from numpy.linalg import norm
from scipy.spatial import ConvexHull


def mirrorPoint(x, s, t):
    # v_st is the vector between s and t
    v_st = np.subtract(t, s)
    # v_st_hat is the normalized vector between s and t
    v_st_hat = v_st / norm(v_st)
    # v_st_orth_hat is orthogonal to v_st and normalized
    v_st_orth_hat = [-v_st_hat[1], v_st_hat[0]]
    # v_sx is the vector between s and x
    v_sx = np.subtract(x, s)
    # proj is the projection from vector v_sx onto vector v_st_orth
    proj = np.multiply(v_sx.dot(v_st_orth_hat), v_st_orth_hat)
    # return the mirror point of x relative to the line through s and t
    return np.subtract(x, proj * 2)


def calculateAngle(v):
    cosang = np.dot([0, -1], v)
    sinang = norm(np.cross([0, -1], v))
    return np.arctan2(sinang, cosang)


def ellipseRadiusToCenter(p1, p2, len):
    # vector from p1 to p2
    v_p1_p2 = np.subtract(p2, p1)
    # angle between [0, -1] and v_p1_p2
    angle = calculateAngle(v_p1_p2)
    # vector from p1 to the center between p1 and p2 (equals the center of the ellipse)
    v_p1_to_center = np.multiply(.5, v_p1_p2)
    # vector length
    v_p1_to_center_len = norm(v_p1_to_center)
    # center of the ellipse
    center = np.add(p1, v_p1_to_center)
    # width of the ellipse (pythagoras)
    width = 2 * sqrt(len * len / 4 + v_p1_to_center_len * v_p1_to_center_len)
    # height equals the length of the ellipse
    height = len
    return center, width, height, angle


def ellipsePoints(centerX, centerY, width, height, angle, n):
    # points before rotation
    points = []
    # calculate points for the third quadrant
    for i in range(1, n + 1):
        # magic!
        theta = pi / 2 * i / (n + 1)
        fi = pi / 2 - atan(tan(theta) * width / height)
        x = centerX + width / 2 * cos(fi)
        y = centerY + height / 2 * sin(fi)
        points.append([x, y])

    # mirror the points to the other quadrants
    for point in points[:]:
        firstQuadrantPoint = [point[0], 2 * centerY - point[1]]
        secondQuadrantPoint = [2 * centerX - point[0], 2 * centerY - point[1]]
        thirdQuadrantPoint = [2 * centerX - point[0], point[1]]
        points.extend([firstQuadrantPoint, secondQuadrantPoint, thirdQuadrantPoint])

    # add points on the right, left, top and bottom
    points.append([centerX + width / 2, centerY])
    points.append([centerX - width / 2, centerY])
    points.append([centerX, centerY + height / 2])
    points.append([centerX, centerY - height / 2])

    # rotation matrix
    r = [[cos(angle), -sin(angle)], [sin(angle), cos(angle)]]
    # points after rotation
    rotatedPoints = []
    for point in points:
        # rotate points around center
        rotatedPoints.append(np.add(np.dot(r, np.subtract(point, [centerX, centerY])), [centerX, centerY]))

    return rotatedPoints


# choose drawing mode
mode = 2  # 0 = standard, 1 = mirror, 2 = ellipse

# create graph
G = nx.DiGraph()
edges = [
    [1, 2],
    [2, 3],
    [3, 4],
    [1, 5],
    [5, 6],
    [6, 4]
]
pos = {
    1: [2, 0],
    2: [0, 1],
    3: [0, 2],
    4: [1, 3],
    5: [4, 1],
    6: [4, 2]
}
for edge in edges:
    x_diff = pos[edge[1]][0] - pos[edge[0]][0]
    y_diff = pos[edge[1]][1] - pos[edge[0]][1]
    edge.append({'w': sqrt(x_diff * x_diff + y_diff * y_diff)})

G.add_edges_from(edges)
s = 1
t = 4

# find shortest path and his length
path = nx.shortest_path(G, source=s, target=t, weight='w')
path_len = nx.shortest_path_length(G, source=s, target=t, weight='w')

# calculate direction between s and t
direction = np.subtract(pos[t], pos[s])

# normalize the direction
direction = direction / norm(direction)

# --- calculate linear hull ---#
# convert path to numpy array of positions
points = np.array([pos[x] for x in path])
# gather points for the linear hull in newPoints
newPoints = []
for point in points:
    # move the point in orthogonal directions to the direction between s and t
    newPoints.append(np.add(point, np.multiply(.1 * path_len, [-direction[1], direction[0]])))
    newPoints.append(np.add(point, np.multiply(.1 * path_len, [direction[1], -direction[0]])))
if mode == 1:
    # go through a copy newPoints to avoid infinite loop and add the mirrorPoints
    for point in newPoints[:]:
        newPoints.append(mirrorPoint(point, pos[s], pos[t]))
# add the points above and below s and t
newPoints.append(np.add(pos[s], np.multiply(-.1 * path_len, direction)))
newPoints.append(np.add(pos[t], np.multiply(.1 * path_len, direction)))

# convert to array of points
newPoints = np.array(newPoints)

# calculate the convex hull
hull = ConvexHull(newPoints)

# draw linear hull
fig = plt.figure()
ax = plt.gca()

# plot all nodes
plt.plot([x for (x, y) in pos.values()], [y for (x, y) in pos.values()], 'o')

# plot all edges
for edge in edges:
    plt.plot([pos[edge[0]][0], pos[edge[1]][0]], [pos[edge[0]][1], pos[edge[1]][1]], 'k-')

# plot the linear hull
for simplex in hull.simplices:
    plt.plot(newPoints[simplex, 0], newPoints[simplex, 1], 'k--')

# draw ellipse
if mode == 2:
    # <-- IMPORTANT
    # data for ellipse
    p1 = [49.308048, 7.273803]#pos[s]
    p2 = [49.441013,  6.615298]#pos[t]
    ellipse_len = 1.1 * 58.793#path_len
    # convert ellipse definition
    center, width, height, angle = ellipseRadiusToCenter(p1, p2, ellipse_len)
    # calculate points
    points_per_quadrant = 10
    points = ellipsePoints(center[0], center[1], width, height, angle, points_per_quadrant)
    # IMPORTANT -->

    plt.plot([points[-4][0], points[-3][0]], [points[-4][1], points[-3][1]], 'k:')
    plt.plot([points[-2][0], points[-1][0]], [points[-2][1], points[-1][1]], 'k:')

    plt.plot([x for (x, y) in points], [y for (x, y) in points], 'k.')

    e = Ellipse(xy=center, width=width, height=height, angle=180 * angle / pi, edgecolor='k', fc='None', ls=':')
    ax.add_patch(e)

# show the plot
plt.show()