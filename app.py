"""Backend Flask: API + páginas. Arranque: python app.py  (produção: gunicorn app:app)"""
import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify, request, send_from_directory
from secret_santa import core

app = Flask(__name__, static_folder="static", static_url_path="/static")
pagina = lambda f: send_from_directory("static", f)


@app.after_request
def cabecalhos(r):
    r.headers["X-Robots-Tag"] = "noindex"
    r.headers["Cache-Control"] = "no-store"
    return r


@app.get("/")
def index(): return pagina("index.html")

@app.get("/admin/<t>")
def admin_page(t): return pagina("admin.html")

@app.get("/s/<t>")
def reveal_page(t): return pagina("reveal.html")


@app.get("/api/config")
def config():
    g = os.getenv
    return jsonify(local=g("LOCAL_JANTAR", ""), valor=g("VALOR_PRESENTE", ""), data=g("DATA_ENTREGA", ""),
                   contacto=g("CONTACTO", ""), paypal=g("APOIO_PAYPAL", ""),
                   revolut=g("APOIO_REVOLUT", ""), bmc=g("APOIO_BUYMEACOFFEE", ""))


@app.post("/api/sorteios")
def criar():
    d = request.get_json(silent=True) or {}
    try:
        s = core.criar_sorteio(d, d.get("participantes", []))
    except ValueError as e:
        return jsonify(erro=str(e)), 400
    return jsonify(admin_token=s["admin_token"]), 201


@app.get("/api/admin/<t>")
def admin(t):
    s = core.por_admin(t)
    if not s: return jsonify(erro="Sorteio não encontrado."), 404
    # O organizador vê os links, mas não quem tirou quem (isso fica só no ficheiro de controlo).
    return jsonify(config=s["config"], participantes=[
        {"nome": p["nome"], "link": core.link(p), "whatsapp": core.whatsapp_url(p, s),
         "mensagem": core.mensagem(p, s), "visto": p.get("visto")} for p in s["participantes"]])


@app.get("/api/reveal/<t>")
def reveal(t):
    s, p = core.por_participante(t)
    if not p: return jsonify(erro="Link inválido."), 404
    return jsonify(nome=p["nome"], config=s["config"])  # o amigo só sai quando a pessoa toca na etiqueta


@app.post("/api/reveal/<t>/abrir")
def abrir(t):
    s, p = core.por_participante(t)
    if not p: return jsonify(erro="Link inválido."), 404
    core.marcar_visto(t)
    return jsonify(amigo=p["amigo"], missao=p["missao"])


@app.get("/api/participantes")
def participantes():
    """Só devolve a lista se CARREGAR_LISTA=1 e o pedido vier do próprio computador (nunca num site público)."""
    local = request.remote_addr in ("127.0.0.1", "::1") and "X-Forwarded-For" not in request.headers
    return jsonify(core.ler_lista() if os.getenv("CARREGAR_LISTA") == "1" and local else [])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))