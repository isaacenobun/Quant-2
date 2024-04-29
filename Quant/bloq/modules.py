## Imports

import ezdxf # - Main Library that parses .DXF files
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re
import math

from django.conf import settings
import os

## Functions

def get_line_length(line):
    '''
    Calculates the length of a DXF line object.

    Parameters:
        line[Dxf line object] : The dxf line object to be measured.

    Returns:
        float: The magnitude of the line.
    '''
    return (line.dxf.end - line.dxf.start).magnitude

def separate_lines(lines, threshold):
    '''
    Creates a list of lines that are longer than a threshold.

    Parameters:
        lines[list]:  A list of dxf line objects.
        threshold[float]: Width of the wall/block.

    Returns:
        list: List of dxf line objects that are longer than the threshold.
    '''
    return [line for line in lines if get_line_length(line) > threshold]

def group_Vlines(lines, distance_threshold):
    '''
    Groups vertical lines that are close to each other based on a distance threshold.

    Parameters:
        lines (list): List of DXF lines to be grouped.
        distance_threshold (float): Maximum horizontal distance between lines to be considered part of the same group.

    Returns:
        list: A list of groups, where each group contains DXF lines that are close to each other horizontally.
    '''

    # Sort the lines by length from longest to shortest
    lines = sorted(lines, key=lambda line: abs(line.dxf.start[1] - line.dxf.end[1]), reverse=True)
    groups = []
    
    while len(lines) > 0:
        current_line = lines.pop(0)
        span_start = min(current_line.dxf.start[1], current_line.dxf.end[1])
        span_end = max(current_line.dxf.start[1], current_line.dxf.end[1])
        group = [current_line]
        remaining_lines = []
        for line in lines:
            if (min(line.dxf.start[1], line.dxf.end[1]) >= span_start and max(line.dxf.start[1], line.dxf.end[1]) <= span_end) or \
               (min(line.dxf.start[1], line.dxf.end[1]) <= span_start and max(line.dxf.start[1], line.dxf.end[1]) >= span_start) or \
               (min(line.dxf.start[1], line.dxf.end[1]) <= span_end and max(line.dxf.start[1], line.dxf.end[1]) >= span_end):
                if 50 < abs(current_line.dxf.start[0] - line.dxf.start[0]) < distance_threshold:
                    group.append(line)
                else:
                    remaining_lines.append(line)
            else:
                remaining_lines.append(line)
        groups.append(group)
        
        # Check if the group has only one line
        if len(group) == 1:
            single_line = group[0]
            for line in lines:
                if 50 < abs(single_line.dxf.start[0] - line.dxf.start[0]) < distance_threshold:
                    group.append(line)
                    remaining_lines.remove(line)  # Remove line from remaining lines
            groups.pop()  # Remove the single-line group
        
        lines = remaining_lines
    
    return groups

def group_Hlines(lines, distance_threshold):
    '''
    Groups horizontal lines that are close to each other based on a distance threshold.

    Parameters:
        lines (list): List of DXF lines to be grouped.
        distance_threshold (float): Maximum vertical distance between lines to be considered part of the same group.

    Returns:
        list: A list of groups, where each group contains DXF lines that are close to each other vertically.
    '''

    # Sort the lines by length from longest to shortest
    lines = sorted(lines, key=lambda line: abs(line.dxf.start[0] - line.dxf.end[0]), reverse=True)
    groups = []
    
    while len(lines) > 0:
        current_line = lines.pop(0)
        span_start = min(current_line.dxf.start[0], current_line.dxf.end[0])
        span_end = max(current_line.dxf.start[0], current_line.dxf.end[0])
        group = [current_line]
        remaining_lines = []
        for line in lines:
            if (min(line.dxf.start[0], line.dxf.end[0]) >= span_start and max(line.dxf.start[0], line.dxf.end[0]) <= span_end) or \
               (min(line.dxf.start[0], line.dxf.end[0]) <= span_start and max(line.dxf.start[0], line.dxf.end[0]) >= span_start) or \
               (min(line.dxf.start[0], line.dxf.end[0]) <= span_end and max(line.dxf.start[0], line.dxf.end[0]) >= span_end):
                if 50 < abs(current_line.dxf.start[1] - line.dxf.start[1]) < distance_threshold:
                    group.append(line)
                else:
                    remaining_lines.append(line)
            else:
                remaining_lines.append(line)
        groups.append(group)
        
        # Check if the group has only one line
        if len(group) == 1:
            single_line = group[0]
            for line in lines:
                if 50 < abs(single_line.dxf.start[1] - line.dxf.start[1]) < distance_threshold:
                    group.append(line)
                    remaining_lines.remove(line)  # Remove line from remaining lines
            groups.pop()  # Remove the single-line group
        
        lines = remaining_lines
    
    return groups

def find_walls(file_path, layer_name, threshold):
    '''
    Finds walls in a DXF file based on the specified layer name and threshold.

    Parameters:
        file_path (str): The path to the DXF file.
        layer_name (str): The name of the layer containing the walls.
        threshold (int): The minimum length threshold for considering a line as a wall. 

    Returns:
        tuple: A tuple containing two lists:
            - A list of horizontal walls represented by DXF lines.
            - A list of vertical walls represented by DXF lines.
    '''

    horizontal_walls = []
    vertical_walls = []
    dwg = ezdxf.readfile(file_path)
    modelspace = dwg.modelspace()

    # Get all lines in the specified layer
    lines = list(modelspace.query(f'LINE[layer=="{layer_name}"]'))

    # Separate lines into horizontal and vertical
    horizontal_lines = [line for line in lines if abs(line.dxf.start[0] - line.dxf.end[0]) > abs(line.dxf.start[1] - line.dxf.end[1])]
    vertical_lines = [line for line in lines if line not in horizontal_lines]

    # ------------------------Debugger--------------------------------
    # print("Total number of lines:", len(lines))
    # print("\nNumber of horizontal lines:", len(horizontal_lines))
    # print("Number of vertical lines:", len(vertical_lines))
    #  ----------------------------------------------------------------

    # Discard lines shorter than threshold
    horizontal_lines = separate_lines(horizontal_lines, threshold)
    vertical_lines = separate_lines(vertical_lines, threshold)

    # ------------------------Debugger--------------------------------
    # print("\nNumber of horizontal lines after filtering:", len(horizontal_lines))
    # print("Number of vertical lines after filtering:", len(vertical_lines))
    #  ----------------------------------------------------------------

    # Group horizontal lines
    horizontal_groups = group_Hlines(horizontal_lines, threshold)

    # ------------------------Debugger--------------------------------
    # print("\nNumber of horizontal groups:", len(horizontal_groups))
    # for i, group in enumerate(horizontal_groups, start=1):
    #     print(f"Horizontal Group {i}: {len(group)} lines")
    #  ----------------------------------------------------------------

    # Group vertical lines
    vertical_groups = group_Vlines(vertical_lines, threshold)

    # ------------------------Debugger--------------------------------
    # print("\nNumber of vertical groups:", len(vertical_groups))
    # for i, group in enumerate(vertical_groups, start=1):
    #     print(f"Vertical Group {i}: {len(group)} lines")
    #  ----------------------------------------------------------------

    # Pick the longest line from each group to represent a wall
    for group in horizontal_groups:
        horizontal_walls.append(max(group, key=get_line_length))

    for group in vertical_groups:
        vertical_walls.append(max(group, key=get_line_length))

    return horizontal_walls, vertical_walls

def walls_output(file_path,layer_name,threshold):
    '''
    Determines the total number of walls in a DXF file based on the specified layer name and threshold.

    Parameters:
        file_path (str): The path to the DXF file.
        layer_name (str): The name of the layer containing the walls.
        threshold (int): The minimum length threshold for considering a line as a wall.

    Returns:
        int: The total number of walls found in the DXF file.
    '''
    
    # Find horizontal and vertical walls
    horizontal_walls, vertical_walls = find_walls(file_path, layer_name, threshold)

    total_walls = len(horizontal_walls) + len(vertical_walls)

    return total_walls

def get_walls_length(file_path,layer_name,threshold):
    '''
    Calculates the total length of walls in a DXF file based on the specified layer name and threshold.

    Parameters:
        file_path (str): The path to the DXF file.
        layer_name (str): The name of the layer containing the walls.
        threshold (int): The minimum length threshold for considering a line as a wall.

    Returns:
        float: The total length of walls found in the DXF file.
    '''
    
    threshold=320
    # Find horizontal and vertical walls
    horizontal_walls, vertical_walls = find_walls(file_path, layer_name, threshold)
    
    horizontal_wall_length = 0
    for wall in horizontal_walls:
        horizontal_wall_length+=get_line_length(wall)
    
    vertical_wall_length = 0
    for wall in vertical_walls:
        vertical_wall_length+=get_line_length(wall)

    total_length = horizontal_wall_length+vertical_wall_length

    return total_length

def calculate_nodes(dxf_path, layer):
    '''
    Calculates the number of nodes in a DXF file based on the specified layer.

    Parameters:
        dxf_path (str): The path to the DXF file.
        layer (str): The name of the layer containing the entities.

    Returns:
        int: The number of nodes found in the DXF file.
    '''
    
    # Store all coordinates of vertices in the DXF file
    vertices = []
    dwg = ezdxf.readfile(dxf_path)
    # Get all lines in the specified layer
    for entity in dwg.entities:
        if entity.dxftype() == 'LINE' and entity.dxf.layer == layer:
            start_x = round(entity.dxf.start[0], 2)
            start_y = round(entity.dxf.start[1], 2)
            end_x = round(entity.dxf.end[0], 2)
            end_y = round(entity.dxf.end[1], 2)
            vertices.append((start_x, start_y))
            vertices.append((end_x, end_y))

    vertices = set(vertices)

    squares = []
    squares_vertices = []

    # Iterate over all combinations of four vertices
    for vertex1 in vertices:
        for vertex2 in vertices:
            if vertex1 != vertex2:
                x1, y1 = vertex1
                x2, y2 = vertex2
                # Check if the difference in x-coordinates is equal to the difference in y-coordinates
                if abs(x1 - x2) == abs(y1 - y2):
                    # Check if the other two vertices of the potential square are present in vertices
                    if (x1, y2) in vertices and (x2, y1) in vertices:
                        # Append the vertices of the square to the squares list
                        squares_vertices.append(vertex1)
                        squares_vertices.append(vertex2)
                        squares_vertices.append((x1, y2))
                        squares_vertices.append((x2, y1))
                        # Append the square itself to the squares list
                        squares.append(squares_vertices)
                        # Remove the vertices of the square from the vertices list
                        for square_vertex in squares_vertices:
                            vertices.remove(square_vertex)
                        # Clear the squares_vertices list for the next square
                        squares_vertices = []

    nodes = 0
    # Create a copy of vertices to iterate over
    for current_vertex in vertices.copy():
        x1, y1 = current_vertex
        for vertex in vertices.copy():
            if vertex == current_vertex:
                continue
            x2, y2 = vertex
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if distance < 320:
                angle = math.atan2(y2 - y1, x2 - x1)
                angle_degrees = math.degrees(angle) % 360
                if angle_degrees in (45, 135, 225, 315):
                    vertices.remove(vertex)
                    vertices.remove(current_vertex)
                    nodes += 1
                    break  # Exit inner loop if a node is found
    return nodes

def get_layers_in_dxf(file_path):
    '''
    Retrieves the names of all layers in a DXF file.

    Parameters:
        file_path (str): The path to the DXF file.

    Returns:
        list: A list containing the names of all layers in the DXF file.
    '''

    layers = []
    dwg = ezdxf.readfile(file_path)
    for layer in dwg.layers:
        layers.append(layer.dxf.name)
    return layers

def save_wall_door_layer_plot(file_path, output_file, destination_folder):
    '''
    Saves a plot of wall and door entities from a DXF file.

    Parameters:
        file_path (str): The path to the DXF file.
        output_file (str): The name of the output plot file.
        destination_folder (str): The path to the folder where the plot file will be saved.
    '''

    # Read the DXF file
    dwg = ezdxf.readfile(file_path)

    layers = get_layers_in_dxf(file_path)

    # Find layers containing 'WALL' or 'DOOR' in their names using regex
    wall_pattern = re.compile(r'\bWALL\b', re.IGNORECASE)
    door_pattern = re.compile(r'\bDOOR\b', re.IGNORECASE)
    wall_layers = [layer for layer in layers if re.search(wall_pattern, layer)]
    door_layers = [layer for layer in layers if re.search(door_pattern, layer)]

    # Create plot
    fig, ax = plt.subplots()

    # Plot entities for WALL layers
    for layer in wall_layers:
        wall_entities = [entity for entity in dwg.modelspace() if entity.dxf.layer == layer]
        for entity in wall_entities:
            if entity.dxftype() == 'LINE':
                start = (entity.dxf.start[0], entity.dxf.start[1])
                end = (entity.dxf.end[0], entity.dxf.end[1])
                ax.plot([start[0], end[0]], [start[1], end[1]], color='black', alpha=1.0, label='WALL')
            elif entity.dxftype() == 'POLYLINE':
                vertices = [(vertex[0], vertex[1]) for vertex in entity.points()]
                x, y = zip(*vertices)
                ax.plot(x, y, color='black', alpha=1.0, label='WALL')
            elif entity.dxftype() == 'ARC':
                center = (entity.dxf.center[0], entity.dxf.center[1])
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                arc = plt.Arc(center, radius*2, radius*2, theta1=start_angle, theta2=end_angle, color='black', alpha=1.0)
                ax.add_patch(arc)
            elif entity.dxftype() == 'CIRCLE':
                center = (entity.dxf.center[0], entity.dxf.center[1])
                radius = entity.dxf.radius
                circle = plt.Circle(center, radius, color='black', alpha=1.0)
                ax.add_patch(circle)

    # Plot entities for DOOR layers
    for layer in door_layers:
        door_entities = [entity for entity in dwg.modelspace() if entity.dxf.layer == layer]
        for entity in door_entities:
            if entity.dxftype() == 'INSERT':
                ax.text(entity.dxf.insert[0], entity.dxf.insert[1], 'Door', fontsize=6.5, color='blue', ha='center', va='center')

    # Customize plot appearance
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    # os.makedirs(destination_folder, exist_ok=True)

    # Save the plot in the specified folder
    plt.savefig(os.path.join(destination_folder, output_file), bbox_inches='tight', pad_inches=0, dpi=300)
    plt.close()

def count_doors_in_layer(file_path):
    '''
    Counts the number of door entities in each layer of a DXF file, containing 'Door' in their name.

    Parameters:
        file_path (str): The path to the DXF file.

    Returns:
        int: The total number of door entities found.
    '''

    entitytype_count = 0
    dwg = ezdxf.readfile(file_path)
    layers = get_layers_in_dxf(file_path)
    door_pattern = re.compile(r'.*DOOR$', re.IGNORECASE)
    door_layers = [layer for layer in layers if re.search(door_pattern, layer)]
    for layer in door_layers:
        door_entities = [entity for entity in dwg.modelspace() if entity.dxf.layer == layer]
        for entity in door_entities:
            if entity.dxftype() == 'INSERT':
                entitytype_count += 1
    return entitytype_count

def get_door_info(doors,height):
    '''
    Calculates information about doors including total door count, total door area, and total door space.

    Parameters:
        doors (list): A list of door objects containing information about each door.
        height (float): The height of the doors.

    Returns:
        tuple: A tuple containing the following information:
            - Total number of doors.
            - Total area covered by doors.
            - Total space occupied by doors.
    '''

    input_door_no,door_area,door_space = 0,0,0
    for door in doors:
        input_door_no+=door.quantity
        door_area+=door.width*door.height*door.quantity
        door_space+=door.width*height*door.quantity
        return input_door_no,door_area,door_space