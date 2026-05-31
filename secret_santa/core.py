"""Lógica do Amigo Secreto: sorteio, missões, mensagem e armazenamento em ficheiros JSON."""
import json, os, random, re, secrets, threading, time
from pathlib import Path
from urllib.parse import quote

DATA = Path(os.getenv("DATA_DIR", "data"))
MODOS = {"sim", "nao", "aleatorio"}
_lock = threading.Lock()


def _modo(v):
    """Aceita o formato antigo do listNames.json ("sim" / "" / ausente) e o novo."""
    v = (v or "").strip().lower().replace("ã", "a").replace("ó", "o")
    return v if v in MODOS else "nao"


def normalizar_telefone(t):
    d = re.sub(r"\D", "", t or "")
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


def criar_sorteio(cfg, participantes):
    """Cria o sorteio, atribui missões, guarda tudo e acrescenta ao ficheiro de controlo."""
    ps = []
    for p in participantes:
        nome = str(p.get("nome", "")).strip()
        tel = normalizar_telefone(p.get("telefone"))
        if not nome or len(tel) < 8:
            raise ValueError(f"Participante inválido: '{nome or '(sem nome)'}'. Indica nome e telefone.")
        ps.append({"nome": nome, "telefone": tel, "modo": _modo(p.get("missao")),
                   "grupo": str(p.get("grupo", "")).strip().lower(), "amigo": None, "missao": None})
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
            p["missao"] = {"missao": m.get("missao"), "exemplo": m.get("exemplo")}
    s = {"id": sid, "admin_token": secrets.token_urlsafe(16), "criado": time.strftime("%Y-%m-%d %H:%M"),
         "config": {k: str(cfg.get(k) or "").strip() for k in ("local", "valor", "data", "contacto")},
         "participantes": ps}
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / f"{sid}.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    _controlo(s)
    return s


def _controlo(s):
    linhas = [f"\n=== Sorteio {s['id']} ({s['criado']}) ==="]
    linhas += [f"Sorteio:{p['nome']} --> {p['amigo']}. Missão:{bool(p['missao'])} - "
               f"{p['missao']['missao'] if p['missao'] else 'N/A'}" for p in s["participantes"]]
    with open(os.getenv("FICHEIRO_CONTROLO", "ficheiro_controlo.txt"), "a", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


def ler(sid):
    if not re.fullmatch(r"[0-9a-f]{8}", sid or ""):
        return None
    f = DATA / f"{sid}.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def por_participante(token):
    s = ler((token or "").split(".")[0])
    if s:
        for p in s["participantes"]:
            if secrets.compare_digest(p["token"], token):
                return s, p
    return None, None


def por_admin(token):
    for f in DATA.glob("*.json"):
        s = json.loads(f.read_text(encoding="utf-8"))
        if secrets.compare_digest(s["admin_token"], token or ""):
            return s
    return None


def link(p):
    return f"{base_url()}s/{p['token']}"


def mensagem(p, s):
    c = s["config"]
    contacto = c["contacto"] or "o encarregado desta mensagem"
    return (f"Olá, {p['nome']}! Bem vind@ à 💌 Missão de Natal.\n"
            "Esta mensagem, apesar de enviada de um número pessoal, é o teu aviso oficial de Amigo Secreto!\n"
            f"A tua missão é presentear o amigo-secreto: (consultar link) {link(p)}\n"
            "🎁 Os Detalhes do Jogo:\n"
            f"Preço: Aproximadamente {c['valor']} (Sem exageros!)\n"
            f"Data de Entrega: {c['data']}, em {c['local']}.\n"
            "🎭 A Regra de Ouro: A entrega será feita num divertido jogo estilo \"Pictionary de Comportamento\":\n"
            "Antes de entregar o presente, terás de imitar um comportamento, gesto, mania ou expressão típica "
            "da pessoa que o irá receber.\n"
            "Só após ser adivinhado é que o presente pode ser entregue. O teu Amigo Secreto terá, por sua vez, "
            "de repetir a proeza para a pessoa que o presenteou.\n"
            f"❓ Dúvidas e Contactos: {contacto}.")


def whatsapp_url(p, s):
    return f"https://api.whatsapp.com/send?phone={p['telefone']}&text={quote(mensagem(p, s), safe='')}"


def marcar_visto(token):
    """Regista a primeira vez que a pessoa abriu a etiqueta (o organizador só vê se já viu)."""
    with _lock:
        s = ler((token or "").split(".")[0])
        for p in (s or {}).get("participantes", []):
            if secrets.compare_digest(p["token"], token) and not p.get("visto"):
                p["visto"] = time.strftime("%d/%m %H:%M")
                (DATA / f"{s['id']}.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")


def ler_lista():
    """Pré-preenche o formulário com FICHEIRO_NOMES (listNames.json)."""
    f = os.getenv("FICHEIRO_NOMES", "listNames.json")
    if not os.path.exists(f):
        return []
    with open(f, encoding="utf-8") as fh:
        return [{"nome": p.get("nome", ""), "telefone": p.get("telefone", ""),
                 "missao": _modo(p["missao"]) if "missao" in p else "aleatorio", "grupo": p.get("grupo", "")} for p in json.load(fh)]