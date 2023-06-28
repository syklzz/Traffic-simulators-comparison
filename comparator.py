import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_histogram(smarts_df, sumo_df, speed_ranges, vehicle_type):
    bar_width = (speed_ranges[1] - speed_ranges[0]) * 0.8
    plt.figure(figsize=(12, 6))
    plt.hist([smarts_df['Average Speed'], sumo_df['Average Speed']], bins=speed_ranges, label=['SMARTS', 'SUMO'])
    plt.xlabel('Average Speed (km/h)')
    plt.ylabel(f'Number of {vehicle_type}')
    plt.title(f'Histogram of Number of {vehicle_type} by Average Speed')
    plt.xticks(speed_ranges[:-1] + bar_width / 2,
               [f'[{speed_ranges[i]}, {speed_ranges[i + 1]})' for i in range(len(speed_ranges) - 1)], fontsize=7)
    plt.xlim(speed_ranges[0], speed_ranges[-1])
    plt.legend()
    plt.show()


def generate_time_series_plot(smarts_df, sumo_df):
    plt.figure(figsize=(12, 6))
    plt.plot(smarts_df['Time Stamp'], smarts_df['Count'], label='SMARTS')
    plt.plot(sumo_df['Time Stamp'], sumo_df['Count'], label='SUMO')
    plt.xlabel('Timestamp')
    plt.ylabel('Number of vehicles')
    plt.title('Number of vehicles in selected area over time')
    plt.legend()
    plt.show()


def generate_average_speed_result(vehicle_count, speed_ranges):
    smarts_cars_average_speed_df = pd.read_csv(f'data/smarts/cars_speed_{vehicle_count}.csv', delimiter=',')
    smarts_bikes_average_speed_df = pd.read_csv(f'data/smarts/bikes_speed_{vehicle_count}.csv', delimiter=',')
    sumo_cars_average_speed_df = pd.read_csv(f'data/sumo/cars_speed_{vehicle_count}.csv', delimiter=',')
    sumo_bikes_average_speed_df = pd.read_csv(f'data/sumo/bikes_speed_{vehicle_count}.csv', delimiter=',')

    generate_histogram(smarts_cars_average_speed_df, sumo_cars_average_speed_df, speed_ranges, 'Cars')
    generate_histogram(smarts_bikes_average_speed_df, sumo_bikes_average_speed_df, speed_ranges, 'Bikes')


def generate_vehicles_count_in_area_result(vehicle_count):
    smarts_vehicle_count_in_area_df = pd.read_csv(f'data/smarts/area_{vehicle_count}.csv', delimiter=',')
    sumo_vehicle_count_in_area_df = pd.read_csv(f'data/sumo/area_{vehicle_count}.csv', delimiter=',')

    generate_time_series_plot(smarts_vehicle_count_in_area_df, sumo_vehicle_count_in_area_df)


if __name__ == '__main__':
    VEHICLE_COUNT = 500

    SPEED_RANGES = np.arange(0, 70, 5)
    generate_average_speed_result(VEHICLE_COUNT, SPEED_RANGES)

    generate_vehicles_count_in_area_result(VEHICLE_COUNT)
