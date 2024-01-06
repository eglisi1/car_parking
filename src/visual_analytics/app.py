from flask import Flask, render_template, request

import logging
from datetime import datetime, timedelta

import services.analysis_service as analysis_service
import services.util_service as util_service

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route("/")
def index() -> str:
    logger.debug("/ called")
    return render_template("index.html")


@app.route("/occupancy_trends")
def occupancy_trends() -> str:
    logger.debug(f"/occupancy_trends called with args {request.args}")
    date_from = util_service.parse_date(request.args.get("date_from", type=str), datetime.today() - timedelta(days=7))
    date_to = util_service.parse_date(request.args.get("date_to", type=str), datetime.today())
    base64_plot = analysis_service.occupancy_trends(date_from, date_to)
    return render_template("occupancy_trends_result.html", plot_url=base64_plot)


@app.route("/occupancy_per_day")
def occupancy_per_day() -> str:
    logger.debug(f"/occupancy_per_day called with args {request.args}")
    date_from = util_service.parse_date(request.args.get("date_from", type=str), datetime.today() - timedelta(days=7))
    date_to = util_service.parse_date(request.args.get("date_to", type=str), datetime.today())
    base64_plot = analysis_service.occupancy_per_day(date_from, date_to)
    return render_template("occupancy_per_day_result.html", plot_url=base64_plot)

if __name__ == "__main__":
    app.run(debug=True)
