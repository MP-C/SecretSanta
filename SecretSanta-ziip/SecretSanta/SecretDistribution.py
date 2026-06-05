"""Modo terminal. python SecretDistribution.py [--id ID] [--enviar]
Sem --id: cria um sorteio a partir de FICHEIRO_NOMES. Com --id: usa um sorteio já feito no site.
--enviar: envio automático via WhatsApp Web (pywhatkit): requer o PC ligado, o browser com sessão iniciada e não mexer no teclado."""
import json, os, sys
from dotenv import load_dotenv
load_dotenv()
from secret_santa import core


def main():
    if "--id" in sys.argv:
        s = core.ler(sys.argv[sys.argv.index("--id") + 1]) or sys.exit("Sorteio não encontrado.")
    else:
        with open(os.getenv("FICHEIRO_NOMES", "listNames.json"), encoding="utf-8") as f:
            nomes = json.load(f)
        cfg = {"local": os.getenv("LOCAL_JANTAR"), "valor": os.getenv("VALOR_PRESENTE"),
               "data": os.getenv("DATA_ENTREGA"), "contacto": os.getenv("CONTACTO", "")}
        try:
            s = core.criar_sorteio(cfg, nomes)
        except ValueError as e:
            sys.exit(f"ERRO: {e}")
    for p in s["participantes"]:
        print(f"\n{p['nome']}: {core.whatsapp_url(p, s)}")
        if "--enviar" in sys.argv:
            import pywhatkit
            pywhatkit.sendwhatmsg_instantly(phone_no="+" + p["telefone"], message=core.mensagem(p, s),
                                            tab_close=True, wait_time=25)


if __name__ == "__main__":
    main()
