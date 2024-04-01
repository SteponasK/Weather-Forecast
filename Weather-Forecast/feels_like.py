def feels_like(parameters):

    # Calculations using a formula from the internet.
    c1 = -8.78469475556
    c2 = 1.61139411
    c3 = 2.33854883889
    c4 = -0.14611605
    c5 = -0.012308094
    c6 = -0.0164248277778
    c7 = 0.002211732
    c8 = 0.00072546
    c9 = -0.000003582

    T = float(parameters['temperature'])
    R = float(parameters['relative_humidity'])
    V = float(parameters['wind_speed']) * 3.6 # Convert wind speed to km/h

    heat_index = c1 + c2 * T + c3 * R + c4 * T * R + c5 * pow(T, 2) + c6 * pow(R, 2) + c7 * pow(T, 2) * R + c8 * T * pow(R, 2) + c9 * pow(T, 2) * pow(R, 2)

    wind_chill = 13.12 + 0.6215 * T - 11.37 * pow(V, 0.16) + 0.3965 * T * pow(V, 0.16)

    if wind_chill > T:
        return round(heat_index, 2)
    else:
        return round(wind_chill, 2)