# Required Libraries
import numpy as np
import random
import pandas as pd
import os
from scipy.special import gamma
from itertools import permutations
from .route_optimization_utils import convertListSetToName, generateDistMatrix, calculateRouteCost, initial_variables, separation_alignment_cohesion, update_food, update_predator, levy_flight, generateGoogleDistMatrix


def calculate(town_list, town_pos_list, town_demand_list, town_tw_list, town_dist_matrix, speed, vehicle_capacity, gasoline_price):
    SIZE = 50
    MAX_ITER = 100

    # Initialize Number of Town
    # town = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    town = town_list
    size_town = len(town)

    # Initialize Depot
    depot_idx = 0  # DEPOT INDEX HAS NOT BEEN SET WHICH ONE FROM THE MAP

    # Initialize Town Pos
    # town_pos = [[5, 7], [10, 9], [0, 20], [4, 5],
    #             [8, 10], [10, 15], [18, 5], [9, 12]]

    town_pos = town_pos_list

    # Calculate Distance Matrix
    # town_dist_matrix = generateDistMatrix(town_pos, len(town_pos))
    # town_dist_matrix = generateGoogleDistMatrix(town_pos)

    # Initialize Demands
    # town_demand = [0, 10, 7, 13, 19, 3, 5, 9]
    town_demand = town_demand_list

    # Time Window
    # time_window = [[7, 19], [8, 12], [9, 12], [
    #     10, 17], [12, 19], [13, 20], [8, 15], [9, 17]]

    time_window = town_tw_list

    # number of Vehicle
    num_vehicle = 1

    # vehicle speed
    # vehicle_speed = 5
    vehicle_speed = speed

    # Maximum load of the vehicle
    # capacity = 100
    capacity = vehicle_capacity

    l = list(permutations(range(1, size_town)))

    # Pick 50 Sets of Permutations
    dragonflies = random.choices(l, k=SIZE)

    # Initialize Population Sets according to Town
    dragonflies_names = convertListSetToName(dragonflies, town)

    # Initialize Radius and Delta Max
    len_col = size_town - 1
    len_row = SIZE

    radius = np.zeros((1, len_col))
    delta_max = np.zeros((1, len_col))

    max_values = 1
    min_values = 0

    for i in range(0, len_col):
        radius[0, i] = (max_values - min_values)/1
        delta_max[0, i] = (max_values - min_values)/1

    dragonflies_val = initial_variables(
        len_row, len_col, min_values, max_values)
    delta_flies_val = initial_variables(
        len_row, len_col, min_values, max_values)
    predator_val = initial_variables(1, len_col, min_values, max_values)
    food_position_val = initial_variables(1, len_col, min_values, max_values)

# Food Position and Predator and Best Dragon

    dragonflies_val_set = []
    cost_val = []

    for i in dragonflies_val:
        temp_dragonfly = i.argsort()
        dragonflies_val_set.append(temp_dragonfly)
        temp_cost = calculateRouteCost(
            temp_dragonfly, town_dist_matrix, time_window, vehicle_speed, gasoline_price)
        cost_val.append(temp_cost)
        temp_food_cost = calculateRouteCost(
            food_position_val[0].argsort(), town_dist_matrix, time_window, vehicle_speed, gasoline_price)
        temp_predator_cost = calculateRouteCost(
            predator_val[0].argsort(), town_dist_matrix, time_window, vehicle_speed, gasoline_price)
        if (temp_cost < temp_food_cost):
            food_position_val[0] = i
        if (temp_cost > temp_predator_cost):
            predator_val[0] = i

        best_dragon = np.copy(food_position_val[0])

    # DA Loop Start

    # Initialize Current Iteration
    curr_iter = 0
    while (curr_iter <= MAX_ITER):

        # Calculate Each Route Fitness / Objective  (Step 3)
        sets_fitness = []
        for i in range(0, SIZE):
            # print("Dragonflies: ", dragonflies_val)
            cost = calculateRouteCost(
                dragonflies_val[i].argsort(), town_dist_matrix, time_window, vehicle_speed, gasoline_price)
            fitness = 1/cost
            sets_fitness.append(fitness)

        for j in range(0, len_col):
            # [TRY TO RESEARCH] - RADIUS RUMUS
            radius[0, j] = (max_values - min_values)*2
            + ((max_values - min_values)*(curr_iter/MAX_ITER)*2)

        weight_inertia = 0.9 - curr_iter*((0.5)/MAX_ITER)
        adjustment_const = 0.1 - curr_iter*((0.1)/(MAX_ITER/2))
        if (adjustment_const < 0):
            adjustment_const = 0

        rand1 = int.from_bytes(os.urandom(
            8), byteorder='big') / ((1 << 64) - 1)
        rand2 = int.from_bytes(os.urandom(
            8), byteorder='big') / ((1 << 64) - 1)
        rand3 = int.from_bytes(os.urandom(
            8), byteorder='big') / ((1 << 64) - 1)
        rand4 = int.from_bytes(os.urandom(
            8), byteorder='big') / ((1 << 64) - 1)
        weight_separation = 2*rand1*adjustment_const  # Seperation Weight
        weight_alignment = 2*rand2*adjustment_const  # Alignment Weight
        weight_cohesion = 2*rand3*adjustment_const  # Cohesion Weight
        weight_food = 2*rand4                  # Food Attraction Weight
        weight_predator = 1*adjustment_const       # Enemy distraction Weight

        # print("Weight Separation: ", weight_separation)
        # print("Weight Alignment: ", weight_alignment)
        # print("Weight Cohesion: ", weight_cohesion)
        # print("Weight Food: ", weight_food)
        # print("Weight Predator: ", weight_predator)

        for i in range(0, len_row):
            separation, alignment, cohesion, neighbors = separation_alignment_cohesion(
                dragonflies_val, radius, i, len_col, len_row)
            food_position_val, dimensions = update_food(
                dragonflies_val, radius, food_position_val, min_values, max_values, i, len_col)
            predator_val = update_predator(
                dragonflies_val, radius, predator_val, min_values, max_values, i, len_col)

            if (dimensions > 0):
                if (neighbors >= 1):
                    for j in range(0, len_col):
                        r1 = int.from_bytes(os.urandom(
                            8), byteorder='big') / ((1 << 64) - 1)
                        r2 = int.from_bytes(os.urandom(
                            8), byteorder='big') / ((1 << 64) - 1)
                        r3 = int.from_bytes(os.urandom(
                            8), byteorder='big') / ((1 << 64) - 1)
                        delta_flies_val[i, j] = np.clip(weight_inertia*delta_flies_val[i, j] + r1*alignment[0, j] +
                                                        r2*cohesion[0, j] + r3*separation[0, j], -delta_max[0, j], delta_max[0, j])
                        dragonflies_val[i, j] = dragonflies_val[i,
                                                                j] + delta_flies_val[i, j]
                elif (neighbors < 1):
                    for k in (0, len_col-1):
                        # print("len_col ", len_col)
                        # print("i", i)
                        # print("k", k)
                        # print("dragonflies: ", dragonflies_val)
                        dragonflies_val[i, k] += levy_flight(len_col+1)
                        delta_flies_val[i, k] = 0
            elif (dimensions == 0):

                for m in range(0, len_col):
                    delta_flies_val[i, m] = np.clip((weight_separation*separation[0, m] + weight_alignment*alignment[0, m] + weight_cohesion*cohesion[0, m] + weight_food *
                                                    food_position_val[0, m] + weight_predator*predator_val[0, m]) + weight_inertia*delta_flies_val[i, m], -delta_max[0, m], delta_max[0, m])
                # Min Values dan Max Values bisa ditentukan lagi
                    dragonflies_val[i, m] = np.clip(
                        dragonflies_val[i, m] + delta_flies_val[i, m], -max_values, max_values)

        for i in range(0, len_row):
            temp_dragon_cost = calculateRouteCost(
                dragonflies_val[i].argsort(), town_dist_matrix, time_window, vehicle_speed, gasoline_price)
            temp_food_cost = calculateRouteCost(
                food_position_val[0].argsort(), town_dist_matrix, time_window, vehicle_speed, gasoline_price)
            temp_predator_cost = calculateRouteCost(
                predator_val[0].argsort(), town_dist_matrix, time_window, vehicle_speed, gasoline_price)
            if (temp_dragon_cost < temp_food_cost):
                for j in range(0, len_col):
                    food_position_val[0, j] = dragonflies_val[i, j]
            if (temp_dragon_cost > temp_predator_cost):
                for j in range(0, len_col):
                    predator_val[0, j] = dragonflies_val[i, j]
            temp_food_cost_2 = calculateRouteCost(
                food_position_val[0].argsort(), town_dist_matrix, time_window, vehicle_speed, gasoline_price)
            # calculateRouteCost(food_position_val[0].argsort(), town_dist_matrix, time_window)
            temp_best_dragon_cost = calculateRouteCost(
                best_dragon.argsort(), town_dist_matrix, time_window, vehicle_speed, gasoline_price)
        if (temp_food_cost_2 < temp_best_dragon_cost):
            best_dragon = np.copy(food_position_val[0])
        else:
            for j in range(0, len_col):
                food_position_val[0, j] = best_dragon[j]
        print("Generation: ", curr_iter)
        print("Best Dragon: ", best_dragon)
        print("------------------")
        curr_iter += 1

    return best_dragon.argsort(), calculateRouteCost(best_dragon.argsort(), town_dist_matrix, time_window, vehicle_speed, gasoline_price)
