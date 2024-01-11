from flask import Flask, render_template, request

import services.check_parking as check_parking

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    if request.method == "GET":
        return render_template("form.html")
    else:
        return check_parking.detect_parking_spaces()


if __name__ == "__main__":
    app.run(debug=True)
