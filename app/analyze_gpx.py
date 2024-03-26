import gpxpy
import geopy.distance

import pandas as pd

from pathlib import Path


def determine_stop_info(gpx):
    course = gpx.tracks[0].segments[0]

    tracking_rest = False

    rest_lat = None
    rest_lon = None
    rest_race_time = None
    elapsed_time = 0
    rest_time = 0
    stop_separation = 0

    # If the stop time in seconds is less than the threshold, stop is ignored
    rest_threshold = 10

    # If distance between stops is less than the threshold, stops are counted as one
    spatial_threshold = 20  # meters

    stop_columns = [
        "Latitude",
        "Longitude",
        "Race time",
        "Elapsed time",
        "Stop time",
        "Merged stop",
    ]
    # Merged stop is when 2 different stops were below the spatial_threshold and are counted as 1
    stops_info = []

    start_time = course.points[0].time

    for idx, point in enumerate(course.points[1:]):
        # Since we start from 2nd point, enumerate idx is already lagging by 1
        previous_point = course.points[idx]
        dt = point.time - previous_point.time

        dlat = point.latitude - previous_point.latitude
        dlon = point.longitude - previous_point.longitude

        if dt.seconds > rest_threshold:
            elapsed_time = (previous_point.time - start_time).total_seconds()
            stops_info.append(
                [
                    previous_point.latitude,
                    previous_point.longitude,
                    previous_point.time,
                    elapsed_time,
                    dt.seconds,
                    False,
                ]
            )

        elif dlat == 0 and dlon == 0:
            if not tracking_rest:
                tracking_rest = True
                elapsed_time = (previous_point.time - start_time).total_seconds()
                rest_lat = previous_point.latitude
                rest_lon = previous_point.longitude
                rest_race_time = previous_point.time

            rest_time += dt.seconds

        elif rest_time > rest_threshold and len(stops_info) == 0:
            stops_info.append(
                [rest_lat, rest_lon, rest_race_time, elapsed_time, rest_time, False]
            )

        elif rest_time != 0 and len(stops_info) > 0:
            # Distance between this and previous stop
            previous_stop = stops_info[-1]
            prev_stop_coords = tuple(previous_stop[:2])
            stop_separation = geopy.distance.distance(
                prev_stop_coords, (rest_lat, rest_lon)
            ).meters

            if rest_time > rest_threshold and stop_separation < spatial_threshold:
                previous_stop[4] += rest_time
                previous_stop[5] = True
                stops_info[-1] = previous_stop
            elif rest_time > rest_threshold:
                stops_info.append(
                    [rest_lat, rest_lon, rest_race_time, elapsed_time, rest_time, False]
                )

            rest_lat, rest_lon, rest_race_time = None, None, None
            rest_time, elapsed_time, stop_separation = 0, 0, 0
            tracking_rest = False

    stops_info_df = pd.DataFrame(stops_info, columns=stop_columns)

    return stops_info_df


if __name__ == "__main__":
    GPX_PATH = Path("C:/Users/davis.pazars/Documents/everesting.gpx")

    with open(GPX_PATH.as_posix(), "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    stops = determine_stop_info(gpx)
    haha = True
