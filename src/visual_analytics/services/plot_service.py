import matplotlib

matplotlib.use("Agg")  # Use a non-interactive backend

import matplotlib.pyplot as plt

from io import BytesIO
import base64


def create_plot(trends: dict) -> str:
    x_axis = list(trends.keys())
    y_axis = [sum(counts) / len(counts) for counts in trends.values()]
    plt.figure(figsize=(10, 6))
    plt.plot(x_axis, y_axis, label="Occupancy", color="blue")
    plt.xlabel("Timestamp")
    plt.ylabel("Average Occupancy")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    return base64.b64encode(buf.getbuffer()).decode("ascii")
