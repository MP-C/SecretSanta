"""Lógica do Amigo Secreto: sorteio, missões, mensagem e armazenamento (JSON, escrita atómica)."""
import json, os, random, re, secrets, tempfile, threading, time
from pathlib import Path
from urllib.parse import quote

DATA = Path(os.getenv("DATA_DIR", "data"))
MODOS = {"sim", "nao", "aleatorio"}
MAX_PESSOAS = 200
_lock = threading.RLock()


def _eq(a, b):
    return secrets.compare_digest(str(a).encode(), str(b).encode())


def _txt(v, n=120):
    """Texto limpo: sem caracteres de controlo (evita injeção de linhas) e com limite de tamanho."""
    return re.sub(r"[\x00-\x1f\x7f]", "", str(v or "")).strip()[:n]


def _modo(v):
    v = _txt(v, 20).lower().replace("ã", "a").replace("ó", "o")
    return v if v in MODOS else "nao"


def normalizar_telefone(t):
    d = re.sub(r"\D", "", _txt(t, 30))
    if d.startswith("00"):
        d = d[2:]
    return os.getenv("INDICATIVO_PAIS", "351") + d if len(d) == 9 else d


def base_url():
    u = (os.getenv("LINK_DOMINIO") or "http://localhost:5000").strip()
    if not u.startswith("http"):
        u = "https://" + u
    return u.rstrip("/") + "/"


def carregar_missoes():
    with open(os.getenv("FICHEIRO_MISSOES", "missaoSecreta.json"), encoding="utf-8") as f:
        return json.load(f)


def sortear(parts, tentativas=5000):
    """Ninguém tira a si próprio nem alguém do mesmo grupo (ex.: casais)."""
    if len(parts) < 3:
        raise ValueError("São precisos pelo menos 3 participantes.")
    for _ in range(tentativas):
        r = parts[:]
        random.shuffle(r)
        if all(a is not b and not (a["grupo"] and a["grupo"] == b["grupo"]) for a, b in zip(parts, r)):
            return r
    raise ValueError("Não foi possível sortear com estes grupos. Reduz o tamanho dos grupos.")


def _guardar(s):
    """Escrita atómica: nunca deixa um ficheiro a meio, mesmo com pedidos simultâneos."""
    DATA.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(s, fh, ensure_ascii=False, indent=1)
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    os.replace(tmp, DATA / f"{s['id']}.json")


def criar_sorteio(cfg, participantes):
    if not isinstance(participantes, list) or len(participantes) > MAX_PESSOAS:
        raise ValueError(f"Lista inválida (máximo {MAX_PESSOAS} participantes).")
    ps = []
    for p in participantes:
        if not isinstance(p, dict):
            raise ValueError("Participante inválido.")
        nome, tel = _txt(p.get("nome"), 60), normalizar_telefone(p.get("telefone"))
        if not nome or not 8 <= len(tel) <= 15:
            raise ValueError(f"Participante inválido: '{nome or '(sem nome)'}'. Indica nome e telefone válidos.")
        ps.append({"nome": nome, "telefone": tel, "modo": _modo(p.get("missao")),
                   "grupo": _txt(p.get("grupo"), 40).lower(), "amigo": None, "missao": None})
    receptores = sortear(ps)
    for p, r in zip(ps, receptores):
        p["amigo"] = r["nome"]
    pool = carregar_missoes()
    random.shuffle(pool)
    sid = secrets.token_hex(4)
    for p in ps:
        p["token"] = f"{sid}.{secrets.token_urlsafe(12)}"
        quer = p["modo"] == "sim" or (p["modo"] == "aleatorio" and random.random() < 0.5)
        if quer and pool:
            m = pool.pop()
            p["missao"] = {"missao": _txt(m.get("missao"), 400), "exemplo": _txt(m.get("exemplo"), 400)}
    s = {"id": sid, "admin_token": f"{sid}.{secrets.token_urlsafe(16)}", "criado": time.strftime("%Y-%m-%d %H:%M"),
         "config": {k: _txt(cfg.get(k), 120) for k in ("local", "valor", "data", "contacto")}, "participantes": ps}
    with _lock:
        _guardar(s)
        with open(os.getenv("FICHEIRO_CONTROLO", "ficheiro_controlo.txt"), "a", encoding="utf-8") as f:
            f.write("\n" + controlo_texto(s))
    return s


def controlo_texto(s):
    linhas = [f"=== Sorteio {s['id']} ({s['criado']}) ==="]
    linhas += [f"Sorteio:{p['nome']} --> {p['amigo']}. Missão:{bool(p['missao'])} - "
               f"{p['missao']['missao'] if p['missao'] else 'N/A'}" for p in s["participantes"]]
    return "\n".join(linhas) + "\n"


def ler(sid):
    if not re.fullmatch(r"[0-9a-f]{8}", sid or ""):
        return None
    f = DATA / f"{sid}.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def por_participante(token):
    token = token or ""
    s = ler(token.split(".")[0])
    for p in (s or {}).get("participantes", []):
        if _eq(p["token"], token):
            return s, p
    return None, None


def por_admin(token):
    token = token or ""
    if "." in token:
        s = ler(token.split(".")[0])
        return s if s and _eq(s["admin_token"], token) else None
    for f in DATA.glob("*.json"):  # tokens antigos (sem id)
        s = json.loads(f.read_text(encoding="utf-8"))
        if _eq(s["admin_token"], token):
            return s
    return None


def apagar(token):
    s = por_admin(token)
    if s:
        with _lock:
            (DATA / f"{s['id']}.json").unlink(missing_ok=True)
    return bool(s)


def marcar_visto(token):
    with _lock:
        s = ler((token or "").split(".")[0])
        for p in (s or {}).get("participantes", []):
            if _eq(p["token"], token) and not p.get("visto"):
                p["visto"] = time.strftime("%d/%m %H:%M")
                _guardar(s)


def ler_lista():
    f = os.getenv("FICHEIRO_NOMES", "listNames.json")
    if not os.path.exists(f):
        return []
    with open(f, encoding="utf-8") as fh:
        return [{"nome": _txt(p.get("nome"), 60), "telefone": _txt(p.get("telefone"), 30),
                 "missao": _modo(p["missao"]) if "missao" in p else "aleatorio", "grupo": _txt(p.get("grupo"), 40)}
                for p in json.load(fh)]


def link(p):
    return f"{base_url()}s/{p['token']}"


def mensagem(p, s):
    """Só usa símbolos de 1 caractere Unicode (BMP): os emojis "grandes" costumam estragar-se no URL do WhatsApp."""
    c = s["config"]
    contacto = c["contacto"] or "o encarregado desta mensagem"
    return (f"Olá, {p['nome']}! Bem vind@ à ✉️ Missão de Natal.\n"
            "Esta mensagem, apesar de enviada de um número pessoal, é o teu aviso oficial de Amigo Secreto!\n"
            f"A tua missão é presentear o amigo-secreto: (consultar link) ➡️ {link(p)}\n"
            "✨ Os Detalhes do Jogo:\n"
            f"Preço: Aproximadamente {c['valor']} (Sem exageros!)\n"
            f"Data de Entrega: {c['data']}, em {c['local']}.\n"
            "⭐ A Regra de Ouro: A entrega será feita num divertido jogo estilo \"Pictionary de Comportamento\":\n"
            "Antes de entregar o presente, terás de imitar um comportamento, gesto, mania ou expressão típica "
            "da pessoa que o irá receber.\n"
            "Só após ser adivinhado é que o presente pode ser entregue. O teu Amigo Secreto terá, por sua vez, "
            "de repetir a proeza para a pessoa que o presenteou.\n"
            f"❓ Dúvidas e Contactos: {contacto}.")


def whatsapp_url(p, s):
    return f"https://api.whatsapp.com/send?phone={p['telefone']}&text={quote(mensagem(p, s), safe='')}"
