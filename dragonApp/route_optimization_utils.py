import numpy as np
import random
import pandas as pd
import os
from dotenv import load_dotenv
from scipy.special import gamma
from itertools import permutations
import math
import googlemaps
load_dotenv()

API_KEY = os.environ.get('API_KEY')


# Function: Distance Calculations
def euclidean_distance(x, y):
    distance = 0
    for j in range(0, len(x)):
        # distance = (x[j] - y[j])**2 + distance
        distance = math.pow((x[j] - y[j]), 2) + distance
    # return distance**(1/2)
    return math.pow(distance, 1/2)

# Function Generate Distance Matrix


def generateDistMatrix(pos, length):
    distMatrix = []
    for i in range(0, length):
        temp = []
        for j in range(0, length):
            temp.append(euclidean_distance(pos[i], pos[j]))
        distMatrix.append(temp)

    return distMatrix

# Function to Convert List Set To Name Town


def generateGoogleDistMatrix(pos):
    gmaps = googlemaps.Client(key=API_KEY)
    mode = "driving"
    distance_matrix = gmaps.distance_matrix(
        origins=pos, destinations=pos, mode=mode)

    print("Distance Matrix: ", distance_matrix)

    dist_matrix_list = []

    for row in distance_matrix['rows']:
        temp = []
        for item in row['elements']:
            temp.append(item['distance']['value'])
            # print(item['distance']['value'])
        dist_matrix_list.append(temp)
    return dist_matrix_list, distance_matrix


def convertListSetToName(townList, town):
    population_sets = []
    for idx, i in enumerate(townList):
        temp = []
        for idx_j, j in enumerate(i):
            temp.append(town[j])
        population_sets.append(temp)
    return population_sets


def calculateRouteCost(route, town_dist_matrix, time_window, vehicle_speed, gasoline_price):
    length = len(route)
    cost = 0
    time = 7  # jam 7 mulai
    time_list = []
    ser_time = 1  # jam loading barang
    veh_speed = vehicle_speed
    gasoline = gasoline_price  # Rp/liter
    engine = 8  # km/liter
    ct = gasoline / engine  # Rp / km
    cs = 16000  # Rp/jam
    cp = 16000

    for i in range(0, length+1):
        late_flag = 0
        early_flag = 0
        curr_tw = []

        if (i == 0):
            dist = town_dist_matrix[0][route[i]+1]
            curr_tw = time_window[route[i]+1]
        elif i == length:
            dist = town_dist_matrix[route[i-1]+1][0]
            curr_tw = time_window[0]
        else:
            dist = town_dist_matrix[route[i-1]+1][route[i]+1]
            curr_tw = time_window[route[i]+1]

        dist = dist/1000  # ubah ke km
        time += (dist/veh_speed)
        trans_cost = dist * ct
        ser_cost = ser_time * cs

        if (time < curr_tw[0]):
            # print("TOO EARLY")
            early_flag = 1
        elif (time > curr_tw[1]):
            # print("TOO LATE")
            late_flag = 1

        pen_cost = (late_flag * (time + ser_time -
                    curr_tw[1]) + early_flag * (curr_tw[0] - time)) * cp

        # finish service
        time += ser_time
        cost += (trans_cost + ser_cost + pen_cost)

    return cost

# Initialize Variable


def initial_variables(row=5, col=7, min_values=0, max_values=1):
    position = np.zeros((row, col))
    for i in range(0, row):
        for j in range(0, col):
            position[i, j] = random.uniform(min_values, max_values)
    return position


def separation_alignment_cohesion(dragonflies, radius, dragon, len_col, len_row):
    dimensions = 0
    neighbors = 0
    index_list = []
    separation = np.zeros((1, len_col))
    alignment = np.zeros((1, len_col))
    cohesion = np.zeros((1, len_col))
    i = dragon
    for j in range(0, len_row):
        # print("J: ", j)
        if (i != j):
            for k in range(0, len_col):
                x = dragonflies[i, 0:len_col]
                y = dragonflies[j, 0:len_col]
                nd = euclidean_distance(x, y)
                # print("K: ", k)

                # Tentukan Neighbor
                if (nd < radius[0, k]):
                    dimensions = dimensions + 1
                    separation[0, k] += (- dragonflies[i, k]
                                         ) - dragonflies[i, k]
                    alignment[0, k] += dragonflies[j, k]
                    cohesion[0, k] += dragonflies[j, k]
                    # print("Separation: ", separation)
                    # print("Alignment: ", alignment)
                    # print("Cohesion: ", cohesion)
            if (dimensions == len_col):
                neighbors = neighbors + 1
                index_list.append(j)
    if (neighbors > 0):
        alignment = alignment / neighbors
        cohesion = cohesion / neighbors
        for m in range(0, len(index_list)):
            for n in range(0, len_col):
                cohesion[0, n] -= dragonflies[index_list[m], n]

    return separation, alignment, cohesion, neighbors


def update_food(dragonflies, radius, food_position, min_values, max_values, dragon, len_col):
    dimensions = 0
    i = dragon
    x = food_position[0]
    y = dragonflies[i]
    fd = euclidean_distance(x, y)
    for k in range(0, len_col):
        # print("Radius: ", radius[0, k]," FD: ", fd)
        if (fd <= radius[0, k]):
            dimensions += 1
    if (dimensions == len_col):
        # print("Dimensions == lencol")
        # print("Food Position Val: ", food_position)
        for k in range(0, len_col):
            # print("i: ", i, "k: ", k)
            # print("Food position [0, k]: ", food_position[0, k])
            # print("Dragonflies [0, k]: ", dragonflies[i, k])
            food_position[0, k] = np.clip(
                food_position[0, k] - dragonflies[i, k], -max_values, max_values)
    else:
        food_position[0, k] = 0
    # print("--Food Position--: ", food_position)
    return food_position, dimensions


def update_predator(dragonflies, radius, predator, min_values, max_values, dragon, len_col):
    dimensions = 0
    i = dragon
    x = predator[0]
    y = dragonflies[i]
    pd = euclidean_distance(x, y)
    for k in range(0, len_col):
        if (pd <= radius[0, k]):
            dimensions += 1
    if (dimensions == len_col):
        for k in range(0, len_col):
            predator[0, k] = np.clip(
                predator[0, k] + dragonflies[i, k], -max_values, max_values)
    else:
        predator[0, k] = 0

    return predator


def levy_flight(beta=1.5):
    beta = beta
    r1 = int.from_bytes(os.urandom(8), byteorder='big') / ((1 << 64) - 1)
    r2 = int.from_bytes(os.urandom(8), byteorder='big') / ((1 << 64) - 1)
    sig_num = gamma(1+beta)*np.sin((np.pi*beta)/2.0)
    sig_den = gamma((1+beta)/2)*beta*2**((beta-1)/2)
    sigma = (sig_num/sig_den)**(1/beta)
    levy = (0.01*r1*sigma)/(abs(r2)**(1/beta))
    return levy
