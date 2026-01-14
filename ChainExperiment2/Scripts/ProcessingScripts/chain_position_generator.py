import numpy as np

# parameters from paper; Tuninetti et al 2021.
CHAIN_SPACING = 0.2  # in meters
CHAIN_RADIUS = 0.1  # in meters
NUMBER_OF_CHAINS_IN_BOUNDARIES = 5

# parameters we want to vary
CORRIDOR_WIDTH = 0.4  # in mters


# def find_chain_positions(corridor_width):
#     corridor_width = CORRIDOR_WIDTH

#     # we want to make a cross like chamber; refer to hand drawn diagram in the report :p

#     # base chains; chains that dont change with turn direction

#     # first make a unit square of chains, then copy paste them as required.

#     chain_unit_box_x = np.arange(
#         CHAIN_SPACING,
#         CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES + CHAIN_SPACING,
#         CHAIN_SPACING,
#     )
#     base_chains_x = np.concat(
#         (
#             chain_unit_box_x,
#             chain_unit_box_x
#             + corridor_width
#             + CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES,
#         )
#     )
#     chain_unit_box_y = chain_unit_box_x.copy()
#     base_chains_y = np.concat(
#         (
#             chain_unit_box_y,
#             chain_unit_box_y + CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES,
#             chain_unit_box_y
#             + 2 * CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES
#             + corridor_width,
#         )
#     )

# now make special case for left turn right turn and straight
# what needs to be added
# straight_missing_box_x = base_chains_x.copy()
# straight_missing_box_y = np.arange(
#     CHAIN_SPACING + 2 * CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES,
#     CHAIN_SPACING
#     + 2 * CHAIN_SPACING * NUMBER_OF_CHAINS_IN_BOUNDARIES
#     + corridor_width,
#     CHAIN_SPACING,
# )

# left_missing_box_x =


def generate_chain_positions_given_width(corridor_width, points_x, points_y, turn_type):
    new_points_x = []
    new_points_y = []
    x_additions = [0, 1 + corridor_width]
    y_additions = [0, 1, 2 + corridor_width]
    for i, point_x in enumerate(points_x):
        for x_add in x_additions:
            for y_add in y_additions:
                new_points_x.append(points_x[i] + x_add)
                new_points_y.append(points_y[i] + y_add)
