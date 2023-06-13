import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import geodesic


def filter_if_column_in_range(df, column, min_value, max_value):
    return df[(df[column] >= min_value) & (df[column] <= max_value)]


def filter_if_column_has_value(df, column, values):
    return df[df[column].isin(values)]


def prepare_data(file):
    df = pd.read_csv(file, delimiter=',')
    df.fillna(method='ffill', inplace=True)
    return df


def count_vehicles_by_timestamp(df, min_latitude, max_latitude, min_longitude, max_longitude):
    df_copy = df.copy()
    df_copy = filter_if_column_in_range(df_copy, 'Latitude', min_latitude, max_latitude)
    df_copy = filter_if_column_in_range(df_copy, 'Longitude', min_longitude, max_longitude)
    return df_copy.groupby('Time Stamp').size().reset_index(name='Count')


def calculate_distance(row):
    if row['Trajectory ID'] != row['Shifted Trajectory ID']:
        return 0

    coordinates_1 = (row['Latitude'], row['Longitude'])
    coordinates_2 = (row['Shifted Latitude'], row['Shifted Longitude'])

    distance = 0
    try:
        distance = geodesic(coordinates_1, coordinates_2).km
    except ValueError:
        pass

    return distance


def calculate_average_speed_by_trajectory(df):
    df_copy = df.copy()
    df_copy[['Shifted Trajectory ID']] = df_copy[['Trajectory ID']].shift(-1)
    df_copy[['Shifted Latitude', 'Shifted Longitude']] = df_copy[['Latitude', 'Longitude']].shift(-1)
    df_copy['Distance'] = df_copy.apply(calculate_distance, axis=1)
    df_copy = df_copy.groupby(['Trajectory ID', 'Vehicle Type']).agg(
        {'Time Stamp': 'count', 'Distance': 'sum'}).reset_index()
    df_copy['Time'] = (df_copy['Time Stamp'] - 1) * 0.2 / 3600
    df_copy['Average Speed'] = df_copy['Distance'] / df_copy['Time']
    return df_copy


def calculate_overall_average_speed(cars_df, bikes_df):
    print(cars_df['Average Speed'].mean())
    print(bikes_df['Average Speed'].mean())


def generate_histogram(df, speed_ranges):
    bar_width = (speed_ranges[1] - speed_ranges[0]) * 0.8
    plt.hist(df['Average Speed'], bins=speed_ranges, align='mid', width=bar_width)
    plt.xlabel('Average Speed (km/h)')
    plt.ylabel('Number of Cars')
    plt.title('Histogram of Number of Cars by Average Speed')
    plt.xticks(speed_ranges[:-1] + bar_width / 2,
               [f'[{speed_ranges[i]}, {speed_ranges[i + 1]})' for i in range(len(speed_ranges) - 1)], fontsize=6)
    plt.xlim(speed_ranges[0], speed_ranges[-1])
    plt.show()


def generate_boxplot(cars_df, bikes_df):
    fig, ax = plt.subplots()
    ax.boxplot([cars_df['Average Speed'], bikes_df['Average Speed']])
    ax.set_xticklabels(['Cars', 'Bikes'])
    ax.set_ylabel('Average Speed (km/h)')
    ax.set_title('Boxplot of Average Speed for All Vehicles')
    plt.show()


def generate_time_series_plot(df):
    plt.plot(df['Time Stamp'], df['Count'])
    plt.xlabel('Timestamp')
    plt.ylabel('Number of vehicles')
    plt.title('Number of vehicles in selected area over time')
    plt.show()


def generate_average_speed_result(df, speed_ranges, output_file, calculate_average_speed=True):
    if calculate_average_speed:
        average_speed_df = calculate_average_speed_by_trajectory(df)
        average_speed_df.to_csv(output_file, sep=',', index=False)
    else:
        average_speed_df = prepare_data(output_file)

    cars_average_speed_df = filter_if_column_has_value(average_speed_df, 'Vehicle Type', ['CAR', 'TRUCK'])
    bikes_average_speed_df = filter_if_column_has_value(average_speed_df, 'Vehicle Type', ['BIKE'])

    generate_histogram(cars_average_speed_df, speed_ranges)
    generate_histogram(bikes_average_speed_df, speed_ranges)
    generate_boxplot(cars_average_speed_df, bikes_average_speed_df)

    calculate_overall_average_speed(cars_average_speed_df, bikes_average_speed_df)


def generate_vehicles_count_in_area_result(df, areas_bounds):
    for min_latitude, max_latitude, min_longitude, max_longitude in areas_bounds:
        vehicles_count_df = count_vehicles_by_timestamp(df, min_latitude, max_latitude, min_longitude, max_longitude)

        generate_time_series_plot(vehicles_count_df)


if __name__ == '__main__':
    output_file = 'speed_data_200.txt'
    data = prepare_data('data_200.txt')

    speed_ranges = np.arange(0, 60, 5)
    generate_average_speed_result(data, speed_ranges, output_file, False)

    areas_bounds = [[50.06870, 50.071445, 19.900597, 19.90811]]
    generate_vehicles_count_in_area_result(data, areas_bounds)
