from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    """This route's only job is to serve the main HTML page."""
    return render_template('index.html')

# We no longer need a /download route because JavaScript will handle it.
