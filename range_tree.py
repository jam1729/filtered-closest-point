import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import time

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Node:
    def __init__(self, feature_point, real_point):
        self.feature_point = feature_point
        self.real_point = real_point
    
    def __repr__(self):
        return f"Node({self.feature_point}, {self.real_point})"    


# Class for the 2D Range Tree
class RangeTree2D:
    def __init__(self, points):
        # Initialize the root by building the tree
        self.root = self._build_tree_on_x(points)

    def _build_tree_on_x(self, points):
        # Base case: No points, return None
        if not points:
            return None

        # Sort points by x-coordinate
        points.sort(key=lambda p: p.feature_point.x)
        mid = len(points) // 2

        # Node structure: contains point, left/right children, sorted y-points, and Voronoi diagram
        node = {
            'point': points[mid],
            'left': self._build_tree_on_x(points[:mid]),
            'right': self._build_tree_on_x(points[mid + 1:]),
            'range_tree_on_y': self._build_tree_on_y(points),
            'points_sorted_by_y': sorted(points, key=lambda p: p.feature_point.y),
            'voronoi': self._compute_voronoi(points),
        }
        return node
    
    def _build_tree_on_y(self, points):
        # Base case: No points, return None
        if not points:
            return None

        # Sort points by y-coordinate
        points.sort(key=lambda p: p.feature_point.y)
        mid = len(points) // 2

        # Node structure: contains point, left/right children, and Voronoi diagram
        node = {
            'point': points[mid],
            'left': self._build_tree_on_y(points[:mid]),
            'right': self._build_tree_on_y(points[mid + 1:]),
            'voronoi': self._compute_voronoi(points),
        }
        return node

    def _compute_voronoi(self, points):
        # Compute Voronoi diagram only if there are at least 4 non-collinear points
        if len(points) < 4:
            return None
        try:
            real_points_as_float = [(p.real_point.x, p.real_point.y) for p in points]
            return Voronoi(real_points_as_float)
        except Exception as e:
            print(f"Voronoi diagram could not be computed for points {points}: {e}")
            return None

    def query(self, query_point):
        # Query the tree for a point and visualize relevant Voronoi diagrams
        visited_nodes = []
        self._query_tree(self.root, query_point, visited_nodes)

        print("Visualizing Voronoi diagrams of visited subtrees...")
        for node in visited_nodes:
            self._visualize_voronoi(node['voronoi'], node['points_sorted_by_y'], query_point=query_point)

        # Find the closest point in the last visited subtree
        # nearest_point = self._find_nearest(query_point, visited_nodes[-1]['points_sorted_by_y'])
        # print(f"The nearest point to {query_point} is {nearest_point}")

        # return nearest_point

    def _query_tree(self, node, query_point, visited_nodes):
        # Recursive query to traverse the tree
        if node is None:
            return

        visited_nodes.append(node)

        # Traverse left or right based on x-coordinate
        if query_point.feature_point.x <= node['point'].feature_point.x:
            self._query_tree(node['left'], query_point, visited_nodes)
        else:
            self._query_tree(node['right'], query_point, visited_nodes)

    def _visualize_voronoi(self, vor, points, query_point=None):
        # Visualize the Voronoi diagram for a given node
        
        real_points_as_float = [(p.real_point.x, p.real_point.y) for p in points]
        # feature_points = [p.feature_point for p in points]
        if vor is not None:
            print(f"Visualizing Voronoi diagram for points: {points}")
            voronoi_plot_2d(vor, show_vertices=True, line_colors='orange', line_width=2, point_size=15)
            
            # Overlay the points
            plt.scatter(*zip(*real_points_as_float), color='blue', label='Points')

            # Plot the query point, if provided
            if query_point is not None:
                plt.scatter(query_point.real_point.x, query_point.real_point.y, color='red', label='Query Point', s=100, zorder=5)

            plt.legend()
            plt.title("Voronoi Diagram")
            plt.show()
            time.sleep(2)
        else:
            print(f"No Voronoi diagram for subtree with points: {points}")


    # def _find_nearest(self, query_point, points):
    #     # Find the nearest point to the query_point in the list of points
    #     return min(points, key=lambda p: np.linalg.norm(np.array(query_point) - np.array(p)))


if __name__ == "__main__":
    # Sample points
    # List 1: Randomly distributed non-collinear points
    real_space = [
        (1, 2), (3, 5), (4, 1), (6, 7), (7, 3),
        (2, 8), (8, 4), (5, 6), (9, 1), (0, 3),
        (3, 7), (6, 2), (1, 9), (4, 4), (7, 5)
    ]

    # List 2: Points forming a convex shape (e.g., vertices of a polygon)
    feature_space = [
        (0, 0), (2, 1), (3, 4), (1, 6), (-1, 5),
        (-3, 3), (-2, 0), (1, -2), (3, -1), (4, 2),
        (5, 5), (3, 7), (0, 8), (-3, 6), (-4, 3)
    ]

    # Build the range tree
    points = []
    for i in range(len(feature_space)):
        points.append(Node(Point(feature_space[i][0], feature_space[i][1]), Point(real_space[i][0], real_space[i][1])))
    tree = RangeTree2D(points)

    # Query the tree for a specific point
    query_point = Node(Point(4, 6), Point(4, 6))
    tree.query(query_point)

