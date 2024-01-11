import matplotlib

matplotlib.use("Agg")  # Use a non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from io import BytesIO
import base64


def create_plot_from_plt(plt: matplotlib.pyplot) -> str:
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def create_plot_occupancy_trends(trends_day: dict, trends_night: dict) -> str:
    plt.figure(figsize=(12, 6))

    daten1 = [data[0] for data in trends_day]
    raten1 = [data[1] for data in trends_day]
    daten2 = [data[0] for data in trends_night]
    raten2 = [data[1] for data in trends_night]

    plt.plot(daten1, raten1, "r-", label="07:00-19:00")
    plt.plot(daten2, raten2, "b-", label="19:01-06:59")

    # X-Axis-Ticks limit to 10
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))

    plt.ylim(0, 100)
    plt.title("Durchschnittliche Belegungsrate nach Tageszeit")
    plt.xlabel("Datum")
    plt.ylabel("Belegungsrate (%)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.gcf().autofmt_xdate()

    return create_plot_from_plt(plt)


def create_plot_occupancy_per_day(average_per_day: dict) -> str:
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    plt.figure(figsize=(14, 6))

    for daytime, week_data in average_per_day.items():
        rates = [week_data.get(tag, 0) for tag in weekdays]
        plt.plot(weekdays, rates, label=daytime)

    plt.title("Durchschnittliche Belegungsrate pro Wochentag und Tageszeit")
    plt.xlabel("Wochentag")
    plt.ylabel("Belegungsrate (%)")
    plt.ylim(0, 100)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    return create_plot_from_plt(plt)


def create_plot_occupancy_hours_by_parkingspace(
    occupancy_hours_by_parkingspace: dict,
) -> str:
    plt.figure(figsize=(10, 6))
    plt.bar(
        range(len(occupancy_hours_by_parkingspace)),
        list(occupancy_hours_by_parkingspace.values()),
        align="center",
    )
    plt.xticks(
        range(len(occupancy_hours_by_parkingspace)),
        list(occupancy_hours_by_parkingspace.keys()),
    )
    plt.title("Besetzungsstunden pro Parkplatz")
    plt.xlabel("Parkplatz ID")
    plt.ylabel("Stunden")

    return create_plot_from_plt(plt)
