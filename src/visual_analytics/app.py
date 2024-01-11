from flask import Flask, render_template, request

import logging
from datetime import datetime, timedelta

import services.analysis_service as analysis_service
import services.util_service as util_service

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_request_dates():
    default_from_date = datetime.today() - timedelta(days=7)
    default_to_date = datetime.today()
    date_from = util_service.parse_date(request.args.get("date_from"), default_from_date)
    date_to = util_service.parse_date(request.args.get("date_to"), default_to_date)
    return date_from, date_to

@app.route("/")
def index() -> str:
    logger.debug("/ called")
    return render_template("index.html")


@app.route("/average_occupancy")
def occupancy_trends() -> str:
    logger.debug(f"/occupancy_trends called with args {request.args}")
    date_from, date_to = parse_request_dates()
    base64_plot = analysis_service.occupancy_trends(date_from, date_to)
    return render_template("occupancy_trends_result.html", plot_url=base64_plot)


@app.route("/occupancy_per_day")
def occupancy_per_day() -> str:
    logger.debug(f"/occupancy_per_day called with args {request.args}")
    date_from, date_to = parse_request_dates()
    base64_plot = analysis_service.occupancy_per_day(date_from, date_to)
    return render_template("occupancy_per_day_result.html", plot_url=base64_plot)

@app.route("/occupancy_hours_by_parkingspace")
def occupancy_hours_by_parkingspace() -> str:
    logger.debug(f"/occupancy_hours_by_parkingspace called with args {request.args}")
    date_from, date_to = parse_request_dates()
    base64_plot = analysis_service.occupancy_hours_by_parkingspace(date_from, date_to)
    return render_template("occupancy_hours_by_parkingspace_result.html", plot_url=base64_plot)

@app.route("/capacity_check")
def capacity_check() -> str:
    return render_template("capacity_check.html", result=analysis_service.capacity_check())

if __name__ == "__main__":
    app.run(debug=True)
