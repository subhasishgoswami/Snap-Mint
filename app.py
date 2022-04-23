from flask import Flask, Blueprint,jsonify
from flask_cors import CORS
import run
import constants as CONST
from waitress import serve
import os

app = Flask(__name__)
cors = CORS(app)
app.register_blueprint(run.bp, url_prefix='/run')


# endpoint to check service status
@app.route("/status")
def check_status():
    return jsonify({CONST.STATUS: CONST.SUCCESS, CONST.DATA: None})



if __name__ == "__main__":  #Local
    app.run(host="localhost", port="3435", debug=True, use_reloader=True)

else:     #Production (Heroku)
    port = int(os.environ.get('PORT', 33507))
    serve(app,port=port)