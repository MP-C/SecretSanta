print("Start random presents selection to 2023 Christmas - Casa Da Aldeia!")
import random
import json
import requests

# Lista de participantes
participantes = []

# Abrir o arquivo JSON
with open("listNames.json", "r") as arquivo:
    # Ler o conteúdo do arquivo
    participantes = json.load(arquivo)

# Imprimir o conteúdo do arquivo
#print(participantes)

# Lista de amigos secretos
amigos_secretos = []
mensagem ='';

# Sorteio aleatório
for i in range(len(participantes)):
    amigo_secreto = random.choice(participantes)
    while amigo_secreto in amigos_secretos:
        amigo_secreto = random.choice(participantes)
    amigos_secretos.append(amigo_secreto)
    print(f"{participantes[i]} --> {amigos_secretos[i]} ")

    # Abrir o arquivo
    with open("amigos_secretos.txt", "a", encoding="utf-16") as arquivo:
        nomeParticipante = participantes[i].get("nome")
        nomeAmigoSecreto = amigos_secretos[i].get("nome")
        mensagem = f"""
                {[i]}) Olá, {nomeParticipante}!
                Esta mensagem é automática, ainda que enviada por um número pessoal.
                O objetivo é informar quem é o teu amigo secreto, que é {nomeAmigoSecreto}.
                Tens de entregar uma prenda no valor de +/- 5€ no dia 24/12/2023, na casa da Aldeia.
                A entrega da prenda será feita em forma de jogo (tipo 'Pictionary').
                Isto é, antes de entregares a prenda, terás de imitar uma característica/comportamento/maneira de ser/expressão e só quando for adivinhado é que pode ser entregue. O teu amigo secreto terá por sua vez, repetir a proeza.
                Qualquer dúvida, é melhor contactar a Maria Fernanda ou o encarregado desta mensagem.
                Obrigado!
                Mário Pedro
                """
        arquivo.write(mensagem)


print("lista Amigos Secretos:", amigos_secretos)

# Enviar a SMS
for contacto in participantes:
    # Mensagem da SMS
    mensagem = f"""
    Olá, {participantes[i]}!
    Esta mensagem é automática, ainda que enviada por um número pessoal.
    O objetivo é informar quem é o teu amigo secreto, que é {amigos_secretos[i]}.
    Tens de entregar uma prenda no valor de +/- 5€ no dia 24/12/2023, na casa da Aldeia.
    A entrega da prenda será feita em forma de jogo (tipo 'Pictionary').
    Isto é, antes de entregares a prenda, terás de imitar uma característica/comportamento/maneira de ser/expressão e só quando for adivinhado é que pode ser entregue. O teu amigo secreto terá por sua vez, repetir a proeza.
    Qualquer dúvida, é melhor contactar a Maria Fernanda ou o encarregado desta mensagem.
    Obrigado!
    Mário Pedro
    """

    YOUR_API_KEY = 'whatsapp/ '
    YOUR_PHONE_NUMBER = '+320000000'
    # Construir a URL
    url = f"https://api.smsapi.com/v1/sms/send?api_key={YOUR_API_KEY}&to={contacto[1]}&from={YOUR_PHONE_NUMBER}&text={mensagem}"

   #Enviar a solicitação
    response = requests.post(url)

    #Verificar o código de resposta
    if response.status_code == 200:
        print(f"SMS enviado com sucesso para {contacto[0]}.")
    else:
        print(f"Erro ao enviar SMS para {contacto[0]}.")
