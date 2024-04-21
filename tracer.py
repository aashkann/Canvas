import math
import numpy as np

sun = [[x, 0, 100] for x in range(-100, 100, 2)]

def intersect(ray, triangles):
    
    for i in range(0, len(triangles), 3):
        a = triangles[i]
        b = triangles[i + 1]
        c = triangles[i + 2]

        e1 = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
        e2 = [c[0] - a[0], c[1] - a[1], c[2] - a[2]]

        h = cross(ray[1], e2)
        dt = dot(e1, h)

        if dt > -0.00001 and dt < 0.00001:
            continue

        f = 1 / dt
        s = [ray[0][0] - a[0], ray[0][1] - a[1], ray[0][2] - a[2]]
        u = f * dot(s, h)

        if u < 0 or u > 1:
            continue

        q = cross(s, e1)
        v = f * dot(ray[1], q)

        if v < 0 or u + v > 1:
            continue

        t = f * dot(e2, q)

        if t > 0.00001:
            return True

    return False

def cross(v1, v2):
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def dot(v1, v2):
    return sum(v1[i] * v2[i] for i in range(len(v1)))


def normalize(v):
    length = sum([i ** 2 for i in v]) ** 0.5
    return [i / length for i in v]

def sub(v1, v2):
    return [v1[i] - v2[i] for i in range(len(v1))]

def bounding_box(vertices):
    min_x = +1000
    min_y = +1000
    min_z = +1000
    max_x = -1000
    max_y = -1000
    max_z = -1000

    for i in range(len(vertices)):
        if i % 3 == 0:
            x = vertices[i]
            min_x = min(min_x, x)
            max_x = max(max_x, x)
        if i % 3 == 1:
            y = vertices[i]
            min_y = min(min_y, y)
            max_y = max(max_y, y)

        if i % 3 == 2:
            z = vertices[i]
            min_z = min(min_z, z)
            max_z = max(max_z, z)

    return [[min_x, min_y, min_z], [max_x, max_y, max_z]]

def create_triangles(design_meshes, context_meshes):
    triangles = []

    for mesh in design_meshes + context_meshes:
        vertices = mesh.vertices
        faces = mesh.faces

        for i in range(0, len(faces), 3):
            a = vertices[faces[i] * 3 : faces[i] * 3 + 3]
            b = vertices[faces[i + 1] * 3 : faces[i + 1] * 3 + 3]
            c = vertices[faces[i + 2] * 3 : faces[i + 2] * 3 + 3]
            triangles.append(a + b + c)
            

    return triangles


def trace(base_meshes, design_meshes, context_meshes):


    [[min_x, min_y, min_z], [max_x, max_y, max_z]] = bounding_box(base_meshes[0].vertices)

    width = int(math.ceil(max_x) - math.floor(min_x)) / 10
    height = int(math.ceil(max_y) - math.floor(min_y)) / 10 

    sample_points = flatten([[[x, y, max_z] for x in range(math.floor(min_x), math.ceil(max_x), 10)] for y in range(math.floor(min_y), math.ceil(max_y), 10)])

    triangles = groupByThree(flatten(create_triangles(design_meshes, context_meshes)))

    results = [0]*len(sample_points)
    for i in range(len(sample_points)):
        sample_point = sample_points[i]
        for sun_position in sun:
            ray = [sun_position, normalize(sub(sample_point, sun_position))]
            if not intersect(ray, triangles):
                results[i] += 1
    

    return np.array(results, dtype=np.uint8).reshape((14, 14)) / 100 * 255

def flatten(list):
    return [item for sublist in list for item in sublist]

def groupByThree(list):
    return [list[i:i + 3] for i in range(0, len(list), 3)]  
