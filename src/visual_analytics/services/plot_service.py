import matplotlib

matplotlib.use("Agg")  # Use a non-interactive backend

import matplotlib.pyplot as plt

from io import BytesIO
import base64


def create_plot_from_plt(plt: matplotlib.pyplot) -> str:
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def create_plot_occupancy_trends(trends: dict) -> str:
    x_axis = list(trends.keys())
    y_axis = [sum(counts) / len(counts) for counts in trends.values()]
    plt.figure(figsize=(10, 6))
    plt.plot(x_axis, y_axis, label="Occupancy", color="blue")
    plt.xlabel("Timestamp")
    plt.ylabel("Average Occupancy")
    plt.xticks(rotation=45)
    plt.tight_layout()

    return create_plot_from_plt(plt)

def create_plot_occupancy_per_day(average_per_day: dict) -> str:
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plt.figure(figsize=(14, 6))

    for daytime, week_data in average_per_day.items():
        rates = [week_data.get(tag, 0) for tag in weekdays]
        plt.plot(weekdays, rates, label=daytime)

    # Beschriftungen und Diagramm-Formatierungen
    plt.title('Durchschnittliche Belegungsrate pro Wochentag und Tageszeit')
    plt.xlabel('Wochentag')
    plt.ylabel('Belegungsrate (%)')
    plt.ylim(0, 100)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    return create_plot_from_plt(plt)