# input for an arena is gonna be a series of points (vertices). this bounds the shape
# our goal is the following
# 0. check if a given point is inside the polygon
# 1. check if the point is away from all the edges (some radius away)
# 1.1 if away, dont do anything
# 1.2 if not away, find the nearest edge and the reflected direction about it.

import sys

import numpy as np
import numpy.linalg as lin
import pandas as pd

sys.path.append("./dynamic_model/")

from supporting_files.vectors import Vector


def read_vertices_csv(file_dir):
    """
    format will be point number, x, y

    Args:
        file_dir (csv): _description_

    Returns:
        _type_: _description_
    """
    #
    df_vertices = pd.read_csv(file_dir)
    _x_coords = df_vertices["x"]
    _y_coords = df_vertices["y"]
    list_of_vertices = []
    for i, _x in enumerate(_x_coords):
        _y = _y_coords[i]
        point = [_x, _y]
        list_of_vertices.append(point)
    return list_of_vertices


# def find_distance_to_edge(point, edge_points):
if __name__ == "__main__":
    print("ts working ig")
