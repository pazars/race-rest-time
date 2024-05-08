import gpxpy
import folium
import analyze_gpx
import geopy.distance

import panel as pn
import pandas as pd

from datetime import datetime, timedelta


pn.extension(notifications=True)


def _display_start_finish(route_map, gpx):
    course = gpx.tracks[0].segments[0]

    start_lat = course.points[0].latitude
    start_lon = course.points[0].longitude

    fin_lat = course.points[-1].latitude
    fin_lon = course.points[-1].longitude

    # Start position marker
    folium.Marker(
        [start_lat, start_lon],
        icon=folium.Icon(icon="play", prefix="fa", color="green"),
    ).add_to(route_map)

    # Finish position marker
    folium.Marker(
        [fin_lat, fin_lon],
        icon=folium.Icon(icon="flag-checkered", prefix="fa", color="red"),
    ).add_to(route_map)


def _display_stops_on_map(route_map, stops_info, gpx):
    start_time = gpx.tracks[0].segments[0].points[0].time

    for _, stop in stops_info.iterrows():
        lat, lon, race_time, elapsed_time, stop_time, merged = stop

        if stop_time < 60:  # 10 minutes
            icon_color = "lightgreen"

        elif stop_time < 5 * 60:  # 5 minutes
            icon_color = "orange"

        else:
            icon_color = "lightred"

        if stop_time < 60:
            rest_time_str = f"{stop_time}s"
        elif stop_time < 3600:
            minutes = stop_time // 60
            seconds = stop_time % 60
            rest_time_str = f"{minutes}min {seconds}s"
        else:
            hours = stop_time // 3600
            minutes = (stop_time % 3600) // 60
            rest_time_str = f"{hours}h {minutes}min"

        if elapsed_time < 60:
            elapsed_time_str = f"{int(elapsed_time)}s"
        elif elapsed_time < 3600:
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            elapsed_time_str = f"{minutes}min {seconds}s"
        else:
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            elapsed_time_str = f"{hours}h {minutes}min"

        text = f"<p>Race time: {race_time.strftime(format='%A %b %d %I:%M %p')}</p><p>Elapsed time: {elapsed_time_str}</p><p>Rest time: {rest_time_str}</p>"
        html = "<div align='center' style='width: fit-content'>" + text + "</div>"

        folium.Marker(
            [lat, lon],
            icon=folium.Icon(color=icon_color),
            popup=folium.Popup(html, max_width=300),
        ).add_to(route_map)


def display_gpx_on_map(route_map, gpx_input):
    if not gpx_input:
        return route_map

    # Parse input .gpx file
    gpx = gpxpy.parse(gpx_input)

    # Display gpx track on map
    coordinates = [
        (point.latitude, point.longitude) for point in gpx.tracks[0].segments[0].points
    ]
    folium.PolyLine(coordinates, weight=6).add_to(route_map)

    # Center the map on the track
    route_map.fit_bounds(route_map.get_bounds(), padding=(30, 30))

    # Display start and finish location markers
    _display_start_finish(route_map, gpx)

    # Gather information about stops
    stops_info = analyze_gpx.determine_stop_info(gpx)

    # Display stop locations on the map
    _display_stops_on_map(route_map, stops_info, gpx)

    return route_map


instruction_md = "### Choose .GPX file"

gpx_input = pn.widgets.FileInput(accept=".gpx")

ctrl_row = pn.Row(instruction_md, gpx_input)

route_map = folium.Map(
    location=[56.945695, 24.120704],
    zoom_start=13,
    tiles="https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png",
    attr='<a href="https://stadiamaps.com/">Stadia Maps</a',
)

gspec = pn.GridSpec(sizing_mode="stretch_both", min_height=800)

gspec[0, :] = ctrl_row
gspec[1:30, :] = pn.bind(display_gpx_on_map, route_map, gpx_input)

# panel serve main.py --autoreload --show
gspec.servable()
