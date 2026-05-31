"""Modo terminal (sem site): lê FICHEIRO_NOMES, sorteia, atualiza o ficheiro de controlo e gera os links.
Uso:  python SecretDistribution.py            -> imprime links WhatsApp (wa.me) por pessoa
      python SecretDistribution.py --enviar   -> envia via WhatsApp Web (pywhatkit), um a um
"""
import json, os, sys
from dotenv import load_dotenv
load_dotenv()
from secret_santa import core


def main():
    with open(os.getenv("FICHEIRO_NOMES", "listNames.json"), encoding="utf-8") as f:
        nomes = json.load(f)
    cfg = {"local": os.getenv("LOCAL_JANTAR"), "valor": os.getenv("VALOR_PRESENTE"),
           "data": os.getenv("DATA_ENTREGA"), "contacto": os.getenv("CONTACTO", "")}
    try:
        s = core.criar_sorteio(cfg, nomes)
    except ValueError as e:
        sys.exit(f"ERRO: {e}")
    print(f"Sorteio {s['id']} criado. Controlo em '{os.getenv('FICHEIRO_CONTROLO', 'ficheiro_controlo.txt')}'.")
    for p in s["participantes"]:
        print(f"\n{p['nome']}: {core.whatsapp_url(p, s)}")
        if "--enviar" in sys.argv:
            import pywhatkit
            pywhatkit.sendwhatmsg_instantly(phone_no="+" + p["telefone"], message=core.mensagem(p, s),
                                            tab_close=True, wait_time=25)


if __name__ == "__main__":
    main()
