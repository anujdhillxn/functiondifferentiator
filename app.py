from flask import Flask, render_template, jsonify,request
from util import Expression
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    input = request.json
    valid = True
    output=""
    try:
        expression = Expression(input=input)
        output = expression.differentiate('x').__str__()
    except:
        valid = False
    return jsonify({"output": output, "valid": valid})

if __name__ == '__main__':
    app.run()