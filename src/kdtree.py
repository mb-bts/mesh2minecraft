class KDNode:
    """Node for KD tree"""

    def __init__(self, value):
        """
        Initializes a node for the KD tree

        Args:
        - value (tuple): tuple of length k specifying the coordinates of a point
        """
        self.value = value
        self.left = None
        self.right = None

class KDTree:
    """Class for KD tree"""
        
    def __init__(self, points):
        """
        Initializes KDTree

        Args:
        - points (list): list of length k tuples each containing the coordinates of a point

        Raises:
        - ValueError: if points list is empty
        """
        if not points:
            raise ValueError("Invalid input, points can't be empty")
        k = len(points[0]) # k is dimension of input data
        self.root = self.build_kd_tree(points, k, 0)
        self.k = k

    def build_kd_tree(self, points, k, depth):
        """
        Builds KD tree recursively

        Args:
        - points (list): list of length k tuples each containing the coordinates of a point
        - k (int): dimensions of input points
        - depth (int): current tree depth

        Returns:
        - node (KDNode): root node of tree
        """
        if not points:
            return None

        # sort points based on the value at the index corresponding to the tree's current depth
        points.sort(key = lambda point: point[depth % k]) 
        median_index = len(points) // 2

        node = KDNode(points[median_index])
        node.left = self.build_kd_tree(points[:median_index], k, depth + 1)
        node.right = self.build_kd_tree(points[median_index + 1:], k, depth + 1)

        return node

    def distance(self, point1, point2):
        """
        Finds Euclidean distance between two points

        Args:
        - point1 (tuple): coordinates of first point
        - point2 (tuple): coordinates of second point

        Returns:
        - float: Euclidean distance between the points
        """
        return sum(((point1[i] - point2[i]) ** 2) for i in range(self.k)) ** 0.5

    def get_nearest_point(self, point):
        """
        Gets nearest point in tree to the given point

        Args:
        - point (tuple): coordinates of the point for which a nearest point will be found

        Returns:
        - KDNode: closest point to the given point
        """
        return self.get_nearest_point_helper(self.root, point, 0, None)

    def get_nearest_point_helper(self, node, point, depth, closest_node):
        """
        Helper for getting nearest point in tree to the given point

        Args:
        - node (KDNode): current node
        - point (tuple): coordinates of the point for which a nearest point will be found
        - depth (int): current depth of tree
        - closest_node (KDNode): nearest point found so far

        Returns:
        - KDNode: closest point to the given point
        """
        if not node: 
            return closest_node

        # if the current node is the closest so far
        if not closest_node or self.distance(node.value, point) < self.distance(closest_node.value, point):
            closest_node = node

        index = depth % self.k
        node_val = node.value[index]
        point_val = point[index]

        if point_val < node_val:
            next_node = node.left
        else:
            next_node = node.right

        return self.get_nearest_point_helper(next_node, point, depth + 1, closest_node)