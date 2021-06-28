from flask import Flask

app = Flask("app")

@app.route("/")
def hello_world():
    return "<p>Hello, World! Sanawarr</p>"

if __name__ == '__main__':
    app.run(debug=True)