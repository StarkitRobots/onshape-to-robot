import json, re, os
import numpy as np

def multmatrix_parse(parameters):
    matrix = np.matrix(json.loads(parameters), dtype=float)
    matrix[0, 3] /= 1000.0
    matrix[1, 3] /= 1000.0
    matrix[2, 3] /= 1000.0
    return matrix

def cube_parse(parameters):
    results = re.findall(r'^size = (.+), center = (.+)$', parameters)
    if len(results) != 1:
        print("! Can't parse CSG cube parameters: "+parameters)
        exit()
    return np.array(json.loads(results[0][0]), dtype=float)/1000.0

def cylinder_parse(parameters):
    results = re.findall(r'h = (.+), r1 = (.+), r2', parameters)
    if len(results) != 1:
        print("! Can't parse CSG cylinder parameters: "+parameters)
        exit()
    result = results[0]
    return np.array([result[0], result[1]], dtype=float)/1000.0

def sphere_parse(parameters):
    results = re.findall(r'r = (.+)$', parameters)
    if len(results) != 1:
        print("! Can't parse CSG sphere parameters: "+parameters)
        exit()
    return float(results[0])/1000.0

def extract_node_parameters(line):
    line = line.strip()
    parts = line.split('(', 1)
    node = parts[0]
    parameters = parts[1]
    if parameters[-1] == ';':
        parameters = parameters[:-2]
    if parameters[-1] == '{':
        parameters = parameters[:-3]
    return node, parameters

def parse_csg(data):
    shapes = []
    lines = data.split("\n")
    matrices = []
    for line in lines:
        line = line.strip()
        if line != '':
            if line[-1] == '{':
                node, parameters = extract_node_parameters(line)
                if node == 'multmatrix':
                    matrix = multmatrix_parse(parameters)
                else:
                    matrix = np.matrix(np.identity(4))
                matrices.append(matrix)
            elif line[-1] == '}':
                matrices.pop()
            else:
                node, parameters = extract_node_parameters(line)
                transform = np.matrix(np.identity(4))
                for entry in matrices:
                    transform = transform*entry
                if node == 'cube':
                    shapes.append({
                        'type': 'cube',
                        'parameters': cube_parse(parameters),
                        'transform': transform
                    })
                if node == 'cylinder':
                    shapes.append({
                        'type': 'cylinder',
                        'parameters': cylinder_parse(parameters),
                        'transform': transform
                    })
                if node == 'sphere':
                    shapes.append({
                        'type': 'sphere',
                        'parameters': sphere_parse(parameters),
                        'transform': transform
                    })
    return shapes

def process(filename):
    os.system('openscad '+filename+' -o /tmp/data.csg')
    f = open('/tmp/data.csg')
    data = f.read()
    f.close()

    return parse_csg(data)

# print(process('urdf/motorcase.scad'))