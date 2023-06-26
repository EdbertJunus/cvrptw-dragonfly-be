import numpy as np
import random
import os
from .route_optimization_utils import calculateRouteCost, generateGoogleDistMatrix
from .pso_util import particle_swarm_optimization


def calculatePSO(town_list, town_pos_list, town_demand_list, town_tw_list, town_dist_matrix, speed, vehicle_capacity, gasoline_price):
    SWARM_SIZE = 50
    MIN = 0
    MAX = 1
    ITERATIONS = 100

    town = town_list
    # # Initialize Town Pos
    town_pos = town_pos_list

    # Calculate Distance Matrix
    # town_dist_matrix = generateGoogleDistMatrix(town_pos)

    # Initialize Demands
    town_demand = town_demand_list

    # Time Window
    time_window = town_tw_list

    # number of Vehicle
    num_vehicle = 1

    # vehicle speed
    vehicle_speed = speed

    # Maximum load of the vehicle
    result = particle_swarm_optimization(town_dist_matrix=town_dist_matrix,
                                         time_window=time_window, vehicle_speed=vehicle_speed, gasoline_price=gasoline_price, swarm_size=SWARM_SIZE, col=len(town_pos)-1, min_values=MIN,
                                         max_values=MAX, iterations=ITERATIONS, decay=0, w=0.9, c1=2,
                                         c2=2, target_function=calculateRouteCost)
    # calculateRouteCost(route, town_dist_matrix, time_window, vehicle_speed)

    return result[0:len(result)-1].argsort(), result[-1]
