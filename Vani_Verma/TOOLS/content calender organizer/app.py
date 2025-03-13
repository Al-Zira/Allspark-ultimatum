from flask import Flask, render_template
import json

app = Flask(__name__)

# Sample data (you could replace this with your own data processing logic)
data = [
    {"name": "Category A", "value": 30},
    {"name": "Category B", "value": 80},
    {"name": "Category C", "value": 45},
    {"name": "Category D", "value": 60},
]

@app.route("/")
def index():
    # Pass data to the template
    return render_template("index.html", data=json.dumps(data))

if __name__ == "__main__":
    app.run(debug=True)
