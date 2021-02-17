#!/usr/bin/env python3

V    = [       10,       30,       60,       90,       11,      130 ]
NOx  = [     0.55,     0.38,     0.28,     0.30,     0.42,     0.58 ]
PM10 = [ 0.005886, 0.004578, 0.001730, 0.004578, 0.006540, 0.007848 ]
PM25 = [ 0.003114, 0.002422,  0.00173, 0.002422,  0.00346, 0.004152 ]

def compute_emission(speed, rate, distance):
    # Find interval
    i_last = len(V) - 1
    if speed < V[0]:
        i_left, i_right = 0, 0
    elif speed > V[i_last]:
        i_left, i_right = i_last, i_last
    else:
        i = 1
        while not x <= l[i]:
            i += 1
        i_left, i_right = i-1, i

    # Define interpolation
    if i_left != i_right:
        t = (speed - V[i_left]) / (V[i_right] - V[i_left])
    else:
        t = 1 # When speed is ≤ 10 or > 130
    def interpolate(points):
        return t * points[i_left] + (1-t) * points[i_right]
    
    e_NOx = interpolate(NOx) * rate/4 * distance
    e_PM10 = interpolate(PM10) * rate/4 * distance
    e_PM25 = interpolate(PM25) * rate/4 * distance


compute_emission(70, 4, 400)
