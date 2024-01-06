from flask import Flask, render_template, request

import logging

import services.analysis_service as analysis_service
import services.db_service as db_service

app = Flask(__name__)
app.logger.level = logging.DEBUG

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route("/")
def index() -> str:
    logger.debug("/ called")
    return render_template("index.html")


@app.route("/occupancy_trends")
def occupancy_trends() -> str:
    logger.debug(f"/occupancy_trends called with args {request.args}")
    timedelta_days = request.args.get("timedelta", default=7, type=int)
    base64_plot = analysis_service.occupancy_trends(db_service.get_collection(), timedelta_days)
    return render_template("occupancy_trends.html", plot_url=base64_plot)


if __name__ == "__main__":
    app.run(debug=True)
