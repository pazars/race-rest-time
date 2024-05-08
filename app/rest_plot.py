import gpxpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd

from pathlib import Path
from analyze_gpx import determine_stop_info

if __name__ == "__main__":
    GPX_PATHS = [
        (
            Path("C:/Users/davis/iCloudDrive/Documents/ultra-gravel-lv/GPX/PAZARS.gpx"),
            "Pazars",
        ),
        (
            Path(
                "C:/Users/davis/iCloudDrive/Documents/ultra-gravel-lv/GPX/SNEIDERS.gpx"
            ),
            "Šneiders",
        ),
    ]

    fig, ax = plt.subplots()
    for path, label in GPX_PATHS:
        with open(path, "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            stops = determine_stop_info(gpx)
            start_dt = pd.Timestamp(year=2024, month=5, day=4, hour=10, minute=0)
            x = start_dt + pd.to_timedelta(stops["Elapsed time"], unit="s")
            y = stops["Stop time"].cumsum() / 60

            df1 = pd.DataFrame({"Elapsed time": x, "Stop time": y})
            df2 = pd.DataFrame(
                {"Elapsed time": x - pd.Timedelta(seconds=1), "Stop time": y.shift(1)}
            )
            df = pd.concat([df1, df2]).sort_values(by="Elapsed time")

            ax.plot(df["Elapsed time"], df["Stop time"], label=label)

    ax.grid()
    ax.legend()
    ax.set_ylabel("Atpūtas minūtes")
    locator = ticker.MultipleLocator(10)
    ax.yaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %H:%M"))
    plt.show()
