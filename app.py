from flask import Flask, render_template, request, jsonify
import threading
import time
import random
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

candles = []
auto_mode = {"active": False}
ultima_decisao = ""

def gerar_candles():
    base = 30000
    while True:
        if len(candles) > 60:
            candles.pop(0)
        candles.append({
            "timestamp": time.strftime('%H:%M:%S'),
            "close": round(base + random.uniform(-200, 200), 2)
        })
        time.sleep(5)

def gerar_decisao_ia(closes):
    prompt = (
        f"Com base nos últimos 20 preços de fechamento: {closes}, "
        "a IA deve decidir se devemos COMPRAR, VENDER ou MANTER. "
        "Forneça a decisão e o raciocínio técnico em português."
    )
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return resposta["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro na IA: {e}"

def estrategia_ia():
    global ultima_decisao
    while True:
        if auto_mode["active"] and len(candles) >= 20:
            closes = [c["close"] for c in candles][-20:]
            decisao = gerar_decisao_ia(closes)
            ultima_decisao = decisao
            print("🤖 IA DECISÃO:", decisao)
        time.sleep(15)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/candles")
def get_candles():
    return jsonify({
        "timestamps": [c["timestamp"] for c in candles],
        "closes": [c["close"] for c in candles]
    })

@app.route("/api/auto", methods=["POST"])
def toggle_auto():
    auto_mode["active"] = not auto_mode["active"]
    return jsonify({"status": "ok", "auto": auto_mode["active"]})

@app.route("/api/ia")
def get_ia_decision():
    return jsonify({"decisao": ultima_decisao})

threading.Thread(target=gerar_candles, daemon=True).start()
threading.Thread(target=estrategia_ia, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
