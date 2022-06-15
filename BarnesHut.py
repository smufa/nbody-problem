import numpy as np
import math


def get_net_force(force_vectors):
    net_force = np.sum(force_vectors, axis=0)

    return net_force


def get_force_vectors(start_point, points_positions, points_masses):
    original_vectors = points_positions - start_point
    weighted_vectors = []
    for i in range(len(original_vectors)):
        weighted_vectors.append(original_vectors[i] * points_masses[i])

    return weighted_vectors


def find_useful_points(parent_index, start_point, theta, useful_points_positions, useful_points_masses):
    for i in range(1, 9):
        index = int('{parent_index}{new_cell_index}'.format(parent_index=parent_index,
                                                            new_cell_index=i))
        cell = all_cells.get(index)
        if cell is not None:
            cell_center_xyz = cell.center_xyz
            width = cell.width
            distance = math.dist(start_point, cell_center_xyz)
            if distance == 0:
                ratio = theta + 1
            else:
                ratio = width / distance

            if ratio <= theta:
                # long-range force
                useful_points_positions.append(cell.cog_xyz)
                useful_points_masses.append(cell.cog_mass)
            else:
                # short-range force
                if cell.has_children:
                    find_useful_points(index, start_point, theta, useful_points_positions, useful_points_masses)
                else:
                    useful_points_positions.append(cell.cog_xyz)
                    useful_points_masses.append(cell.cog_mass)

    useful_points_positions = np.array(useful_points_positions)
    useful_points_masses = np.array(useful_points_masses)

    return useful_points_positions, useful_points_masses


def main(points_positions, points_masses, start_point, theta):
    global all_cells
    all_cells = {}
    num_of_points, _ = points_positions.shape

    # ----- CONSTRUCT OCTREE -----
    # find limits of bounding box
    min_xyz = np.min(points_positions, axis=0)
    max_xyz = np.max(points_positions, axis=0)
    limits = np.array([min_xyz, max_xyz])
    # print("min_xyz: ", min_xyz, ", max_xyz: ", max_xyz)
    # print("limits: ", limits)

    # create root cell
    root_cell = Cell(0, limits, None)
    all_cells[0] = all_cells.get(0, Cell(cell_index=0, limits=limits, parent_index=None))

    # add points
    for point in range(num_of_points):
        root_cell.add_point_to_cell(point_position=points_positions[point], point_mass=points_masses[point])

    """
    # add first point
    print("point: {}".format(points_positions[0]))
    root_cell.add_point_to_cell(points_positions[0])
    print("all_cells: {}".format(all_cells))

    # add second point
    print("point: {}".format(points_positions[1]))
    root_cell.add_point_to_cell(points_positions[1])
    

    for i in all_cells.keys():
        print("cell: {i}, point_inside: {p}, point: {c}, \n"
              "cog_xyz: {cog_xyz}, cog_mass: {cog_mass}".format(i=i,
                                                                p=all_cells.get(i).point_inside,
                                                                c=all_cells.get(i).point_inside_position,
                                                                cog_xyz=all_cells.get(i).cog_xyz,
                                                                cog_mass=all_cells.get(i).cog_mass))

    print("\nnumber of cells: {}".format(len(all_cells)))
    print("\n-------------------------------------\n")
    """

    # remove cells with no points
    keys = list(all_cells.keys())
    for index in keys:
        cell = all_cells.get(index)
        if cell.cog_xyz is None:
            all_cells.pop(index)
    """
    for i in all_cells.keys():
        print("cell: {i}, point_inside: {p}, point: {c}, \n"
              "cog_xyz: {cog_xyz}, cog_mass: {cog_mass}, \n"
              "limits: \n{limits}\n".format(i=i,
                                            p=all_cells.get(i).point_inside,
                                            c=all_cells.get(i).point_inside_position,
                                            cog_xyz=all_cells.get(i).cog_xyz,
                                            cog_mass=all_cells.get(i).cog_mass,
                                            limits=all_cells.get(i).limits))

    print("\nnumber of cells: {}".format(len(all_cells)))
    """

    # ----- ESTIMATE FORCES -----
    # start_point = point where we want to calculate the sum of forces
    # ratio = ratio between cell width and distance from the center of gravity of cell to the start_point
    # theta = determines which forces are long-range and which are short-range
    #       ratio <= theta ... cell is source of long-range force
    #       ratio > theta  ... cell is source of short-range force

    useful_points_positions = []
    useful_points_masses = []

    # find useful points
    useful_points_positions, useful_points_masses = find_useful_points(0, start_point, theta, useful_points_positions,
                                                                       useful_points_masses)

    # print("useful points positions: \n{positions}\nmasses: \n{masses}".format(positions=useful_points_positions,
    #                                                                          masses=useful_points_masses))

    return useful_points_positions, useful_points_masses


class Cell:
    def __init__(self, cell_index, limits, parent_index):
        self.cog_mass = None
        self.cog_xyz = None
        self.cell_index = cell_index
        self.limits = limits
        self.parent_index = parent_index
        self.width = math.fabs(limits[0, 0] - limits[1, 0])
        self.center_xyz = np.mean(self.limits, axis=0)
        # self.level = parent_level + 1
        # self.print_index_and_limits()
        self.point_inside = False
        self.point_inside_position = None
        self.point_inside_mass = None
        self.has_children = False

    def split_cell(self):
        # ----- CREATE 8 SUBCELLS OF CURRENT CELL -----
        # find limits of new cells
        min_x, min_y, min_z = self.limits[0, :]
        middle_x, middle_y, middle_z = np.mean(self.limits, axis=0)
        max_x, max_y, max_z = self.limits[1, :]
        # print("min_x: ", min_x, ", min_y: ", min_y, ", min_z:", min_z)
        # print("middle_x: ", middle_x, ", middle_y: ", middle_y, ", middle_z:", middle_z)
        # print("max_x: ", max_x, ", max_y: ", max_y, ", max_z:", max_z)

        new_limits = np.array([[[min_x, min_y, middle_z], [middle_x, middle_y, max_z]],
                               [[middle_x, min_y, middle_z], [max_x, middle_y, max_z]],
                               [[min_x, min_y, min_z], [middle_x, middle_y, middle_z]],
                               [[middle_x, min_y, min_z], [max_x, middle_y, middle_z]],
                               [[min_x, middle_y, middle_z], [middle_x, max_y, max_z]],
                               [[middle_x, middle_y, middle_z], [max_x, max_y, max_z]],
                               [[min_x, middle_y, min_z], [middle_x, max_y, middle_z]],
                               [[middle_x, middle_y, min_z], [max_x, max_y, middle_z]]])
        for child_number in range(1, 9):
            # setting indexes for the subcells (concatenated parent index and child number 1-8)
            index = int('{parent_index}{new_cell_index}'.format(parent_index=self.cell_index,
                                                                new_cell_index=child_number))
            # print("limits[{}]".format(i-1))
            # print("index : {}".format(index))
            all_cells[index] = all_cells.get(index, Cell(cell_index=index, limits=new_limits[child_number - 1],
                                                         parent_index=self.cell_index))

        # print("all_cells: {}".format(all_cells))

        self.has_children = True

    def print_index_and_limits(self):
        print("Cell index: {index}, limits: \n{limits}\n".format(index=self.cell_index, limits=self.limits))

    def add_point_to_cell(self, point_position, point_mass):
        if not self.point_inside and not self.has_children:
            self.point_inside_position = self.cog_xyz = point_position
            self.point_inside_mass = self.cog_mass = point_mass
            self.point_inside = True
        elif not self.point_inside:
            self.move_point_to_child(point_position, point_mass)
            self.find_center_of_gravity()
        else:
            self.split_cell()
            point_old_position = self.point_inside_position
            point_old_mass = self.point_inside_mass
            self.move_point_to_child(point_old_position, point_old_mass)
            point_new_position = point_position
            point_new_mass = point_mass
            self.move_point_to_child(point_new_position, point_new_mass)
            self.find_center_of_gravity()

    def move_point_to_child(self, point_position, point_mass):
        for child_number in range(1, 9):
            child_index = int('{parent_index}{new_cell_index}'.format(parent_index=self.cell_index,
                                                                      new_cell_index=child_number))
            child = all_cells.get(child_index)

            # print("child.limits: {}".format(child.limits))

            point_x, point_y, point_z = point_position
            child_min_x, child_min_y, child_min_z = child.limits[0, :]
            child_max_x, child_max_y, child_max_z = child.limits[1, :]

            if child_min_x <= point_x <= child_max_x and child_min_y <= point_y <= child_max_y and \
                    child_min_z <= point_z <= child_max_z:
                child.add_point_to_cell(point_position, point_mass)
                self.point_inside = False
                self.point_inside_position = None
                self.point_inside_mass = None
                self.cog_xyz = None
                break

    def find_center_of_gravity(self):
        # ----- FIND CENTER OF GRAVITY FROM 8 SUBCELLS -----
        self.cog_xyz = None
        self.cog_mass = None
        cog_x = cog_y = cog_z = mass = 0

        for child_number in range(1, 9):
            # setting indexes for the subcells (concatenated parent index and child number 1-8)
            index = int('{parent_index}{new_cell_index}'.format(parent_index=self.cell_index,
                                                                new_cell_index=child_number))
            # print("limits[{}]".format(i-1))
            # print("index : {}".format(index))
            cell = all_cells.get(index)
            if cell.cog_xyz is not None:
                cog_x += cell.cog_mass * cell.cog_xyz[0]
                cog_y += cell.cog_mass * cell.cog_xyz[1]
                cog_z += cell.cog_mass * cell.cog_xyz[2]
                mass += cell.cog_mass

        if mass != 0:
            self.cog_xyz = [cog_x / mass, cog_y / mass, cog_z / mass]
            self.cog_mass = mass


if __name__ == "__main__":
    start_point1 = [0, 0, 0]
    start_point2 = [10, 10, 10]
    start_point3 = [0.125, 0.125, 0.125]
    start_point4 = [0.55555555556, 0.55555555556, 0.55555555556]

    theta1 = 1

    input_array = np.array([[-0.125, -0.125, -0.125],
                            [-0.25, -0.25, -0.25],
                            [-1, -1, -1],
                            [0., 0., 0.],
                            [0.125, 0.125, 0.125],
                            [0.25, 0.25, 0.25],
                            [0.375, 0.375, 0.375],
                            [0.5, 0.5, 0.5],
                            [0.625, 0.625, 0.625],
                            [0.75, 0.75, 0.75],
                            [0.875, 0.875, 0.875],
                            [1., 1., 1.]])

    input_array1 = np.array(
        [[1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1], [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
         [0.3, 0.3, 0.3], [0.3, 0.3, -0.3], [0.3, -0.3, 0.3], [0.3, -0.3, -0.3], [-0.3, 0.3, 0.3], [-0.3, 0.3, -0.3],
         [-0.3, -0.3, 0.3], [-0.3, -0.3, -0.3]])

    input_array2 = np.array(
        [[1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1], [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]])

    input_array3 = np.array(
        [[1, 1, 1], [0.5, 0.5, 0.5], [-1, -1, -1]])

    input_array4 = np.array(
        [[10, 10, 10], [-10, -10, -10], [0, 0, 0], [9.9, 9.9, 9.9], [9.8, 9.8, 9.8]])

    input_array5 = np.array(
        [[10, 10, 10], [9.8, 9.8, 9.8], [-10, -10, -10], [-9.8, -9.8, -9.8]])

    input_array6 = np.array([[3.50183652, 2.83372761, -2.52084241], [3.71375405, 4.88892666, -3.42116649],
                             [3.54640005, 3.53167423, 1.97698521]])

    masses6 = [1., 0.2, 0.2]
    masses = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    masses1 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    masses2 = [1, 1, 1, 1, 1, 1, 1, 1]
    masses3 = [3, 2, 3]
    masses4 = [1, 1, 1, 1, 1]
    masses5 = [1, 5, 1, 5]

    # print("Input array: \n", input_array1, "\n\n")
    ena, dva = main(input_array4, masses4, start_point1, theta1)
    print(ena, dva)
