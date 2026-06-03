"""Backend Flask: API + páginas. Local: python app.py | Produção: gunicorn -w 1 --threads 8 app:app (ou waitress)"""
import mimetypes, os, threading, time
from collections import defaultdict, deque
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, Response, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException
from secret_santa import core

# No Windows o registo do sistema pode dar .js como text/plain; com nosniff o browser recusaria o script.
for _ext, _tipo in ((".js", "text/javascript"), (".css", "text/css"), (".html", "text/html")):
    mimetypes.add_type(_tipo, _ext)

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024
if os.getenv("TRUST_PROXY") == "1":  # só atrás de um proxy HTTPS de confiança
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

CSP = ("default-src 'none'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; base-uri 'none'; "
       "form-action 'none'; frame-ancestors 'none'")
_hits, _hl = defaultdict(deque), threading.Lock()


def excedeu(chave, n, janela):
    agora, k = time.time(), (chave, request.remote_addr)
    with _hl:
        if len(_hits) > 20000: _hits.clear()
        q = _hits[k]
        while q and q[0] < agora - janela: q.popleft()
        if len(q) >= n: return True
        q.append(agora)
        return False


@app.before_request
def limites():
    if request.path.startswith("/api/") and (excedeu("api", 240, 60) or (
            request.method == "POST" and request.path == "/api/sorteios"
            and excedeu("novo", int(os.getenv("MAX_SORTEIOS_HORA", 20)), 3600))):
        return jsonify(erro="Demasiados pedidos. Tenta daqui a pouco."), 429


@app.after_request
def cabecalhos(r):
    r.headers.update({"X-Robots-Tag": "noindex", "Cache-Control": "no-store", "Content-Security-Policy": CSP,
                      "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer",
                      "Permissions-Policy": "camera=(), microphone=(), geolocation=()"})
    if request.is_secure: r.headers["Strict-Transport-Security"] = "max-age=31536000"
    return r


@app.errorhandler(Exception)
def erro(e):
    if not isinstance(e, HTTPException): app.logger.exception(e)
    c = e.code if isinstance(e, HTTPException) else 500
    return jsonify(erro={404: "Não encontrado.", 405: "Pedido não permitido.", 413: "Pedido demasiado grande."}
                   .get(c, "Erro interno.")), c


pagina = lambda f: send_from_directory("static", f)

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
                   contacto=g("CONTACTO", ""), paypal=g("APOIO_PAYPAL", ""), revolut=g("APOIO_REVOLUT", ""),
                   bmc=g("APOIO_KOFI") or g("APOIO_BUYMEACOFFEE", ""))


@app.post("/api/sorteios")
def criar():
    d = request.get_json(silent=True)
    if not isinstance(d, dict): return jsonify(erro="Pedido inválido."), 400
    try:
        s = core.criar_sorteio(d, d.get("participantes", []))
    except ValueError as e:
        return jsonify(erro=str(e)), 400
    return jsonify(admin_token=s["admin_token"]), 201


@app.get("/api/admin/<t>")
def admin(t):
    s = core.por_admin(t)
    if not s: return jsonify(erro="Sorteio não encontrado."), 404
    return jsonify(id=s["id"], config=s["config"], participantes=[
        {"nome": p["nome"], "link": core.link(p), "whatsapp": core.whatsapp_url(p, s),
         "mensagem": core.mensagem(p, s), "visto": p.get("visto")} for p in s["participantes"]])


@app.get("/api/admin/<t>/controlo")
def controlo(t):
    s = core.por_admin(t)
    if not s: return jsonify(erro="Sorteio não encontrado."), 404
    return Response(core.controlo_texto(s), mimetype="text/plain; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="controlo_{s["id"]}.txt"'})


@app.delete("/api/admin/<t>")
def apagar(t):
    return (jsonify(ok=True), 200) if core.apagar(t) else (jsonify(erro="Sorteio não encontrado."), 404)


@app.get("/api/reveal/<t>")
def reveal(t):
    s, p = core.por_participante(t)
    if not p: return jsonify(erro="Link inválido."), 404
    return jsonify(nome=p["nome"], config=s["config"])


@app.post("/api/reveal/<t>/abrir")
def abrir(t):
    s, p = core.por_participante(t)
    if not p: return jsonify(erro="Link inválido."), 404
    core.marcar_visto(t)
    return jsonify(amigo=p["amigo"], missao=p["missao"])


@app.get("/api/participantes")
def participantes():
    """Só com CARREGAR_LISTA=1 e pedido vindo do próprio computador (nunca num site público)."""
    local = request.remote_addr in ("127.0.0.1", "::1") and "X-Forwarded-For" not in request.headers
    return jsonify(core.ler_lista() if os.getenv("CARREGAR_LISTA") == "1" and local else [])


if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 5000)))