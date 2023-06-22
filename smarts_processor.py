import pandas as pd
import numpy as np
from geopy.distance import geodesic


def read_file(file):
    return pd.read_csv(file, delimiter=',')


def read_data(vehicle_count):
    df = read_file(f'data_{vehicle_count}.txt')
    df.fillna(method='ffill', inplace=True)
    return df


def read_speed_data(vehicle_count, calculate_speed_data=False):
    file = f'speed_data_{vehicle_count}.txt'
    if calculate_speed_data:
        df = read_data(vehicle_count)
        average_speed_df = calculate_average_speed_by_trajectory(df)
        average_speed_df.to_csv(file, sep=',', index=False)
    else:
        average_speed_df = read_file(file)
    return average_speed_df


def filter_if_column_in_range(df, column, min_value, max_value):
    return df[(df[column] >= min_value) & (df[column] <= max_value)]


def filter_if_column_has_value(df, column, values):
    return df[df[column].isin(values)]


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
    return df_copy[['Trajectory ID', 'Time', 'Distance', 'Average Speed']]


def calculate_overall_average_speed(cars_df, bikes_df):
    overall_cars_average_speed = cars_df['Distance'].sum(axis=0) / cars_df['Time'].sum(axis=0)
    overall_bikes_average_speed = bikes_df['Distance'].sum(axis=0) / bikes_df['Time'].sum(axis=0)

    print(f'Overall cars average speed: {overall_cars_average_speed}')
    print(f'Overall bikes average speed: {overall_bikes_average_speed}')


def count_vehicles_in_area(df, min_latitude, max_latitude, min_longitude, max_longitude):
    df_copy = df.copy()
    df_copy = filter_if_column_in_range(df_copy, 'Latitude', min_latitude, max_latitude)
    df_copy = filter_if_column_in_range(df_copy, 'Longitude', min_longitude, max_longitude)

    df_copy = df_copy.groupby('Time Stamp').size().reset_index(name='Count')

    df_copy['Time Stamp'] = df_copy['Time Stamp'].round(1)
    df_empty = pd.DataFrame({'Time Stamp': pd.Index(np.arange(0.0, 3600.2, 0.2))})
    df_empty['Time Stamp'] = df_empty['Time Stamp'].round(1)

    return pd.merge_asof(df_empty, df_copy, on='Time Stamp').fillna(0)


def prepare_speed_data(vehicle_count):
    df = read_speed_data(vehicle_count)

    cars_average_speed_df = filter_if_column_has_value(df, 'Vehicle Type', ['CAR', 'TRUCK'])
    bikes_average_speed_df = filter_if_column_has_value(df, 'Vehicle Type', ['BIKE'])

    cars_average_speed_df['Average Speed'].to_csv(f'data/smarts/cars_speed_{vehicle_count}', sep=',', index=False)
    bikes_average_speed_df['Average Speed'].to_csv(f'data/smarts/bikes_speed_{vehicle_count}', sep=',', index=False)

    calculate_overall_average_speed(cars_average_speed_df, bikes_average_speed_df)


def prepare_area_data(vehicle_count, area_bounds):
    df = read_data(vehicle_count)

    min_latitude, max_latitude, min_longitude, max_longitude = area_bounds
    vehicles_count_df = count_vehicles_in_area(df, min_latitude, max_latitude, min_longitude, max_longitude)

    vehicles_count_df.to_csv(f'data/smarts/area_{vehicle_count}', sep=',', index=False)


if __name__ == '__main__':
    VEHICLE_COUNT = 500

    prepare_speed_data(VEHICLE_COUNT)

    areas_bounds = [50.06870, 50.071445, 19.900597, 19.90811]
    prepare_area_data(VEHICLE_COUNT, areas_bounds)
