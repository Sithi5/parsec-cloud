# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

from flask import Flask, request, redirect, render_template

app = Flask(__name__)
BACKEND_ADDR = "localhost:6888?no_ssl=true"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/google/")
def google():
    return redirect("https://google.com")


@app.route("/api/invite/", methods=["GET", "POST"])
def parsec_get():
    typ = ""
    token = ""
    print("\n\nREQUEST HEADERS = ", request.headers)
    print("\n\nREQUEST = ", request)
    if request.method == "POST":
        print("POST REQUEST")
        data = request.form
        typ = data["type"]
        token = data["token"]
    else:
        print("GET REQUEST")
        typ = request.args.get("type")
        token = request.args.get("token")
    print("Type = " + str(typ) + ". token = " + str(token))
    redirect_url = "parsec://" + BACKEND_ADDR + "/link"
    print("redirecting = " + redirect_url)
    return redirect("parsec://" + BACKEND_ADDR)


@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(500)
def error_404(error):
    return "Error : {}".format(error.code), error.code


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)