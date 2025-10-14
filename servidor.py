from flask import Flask, request, jsonify


app = Flask(__name__)




@app.route("/api/veiculos", methods=["GET"])
def get_veiculos():
    return jsonify({"veiculos": ["Carro", "Moto", "Caminhão"]})




if __name__ == '__main__':
    app.run(debug=True)
