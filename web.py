from flask import Flask, render_template, request, redirect
from topsolar import fetch_today

app = Flask("stockChecker")

@app.route("/")
def home():
    result = fetch_today()
    #print(result)
    return render_template("home.html", result=result)

