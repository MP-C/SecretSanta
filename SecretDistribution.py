import random
import json
# Importação mantida, mas a URL será simulada
#import requests

localJantar ="Casa da Aldeia"
valor ="2€ - 7€"
print(f"A iniciar o sorteio de presentes de Natal 2023, 2025... - {localJantar}")

# --- 1. Carregar Dados ---
try:
    # 1.1 Carregar lista de participantes (GIVERS)
    with open("listNames.json", "r", encoding="utf-8") as arquivo_nomes:
        participantes = json.load(arquivo_nomes)
        print("...Ficheiro Participantes carregado")

    # 1.2 Carregar missões secretas
    # CORREÇÃO: Usar o handle 'arquivosecreto' correto e não o 'arquivo' anterior.
    with open("missaoSecreta.json", "r", encoding="utf-8") as arquivosecreto:
        missaoSecreta_data = json.load(arquivosecreto)
        print("...Ficheiro Missões carregado")

except FileNotFoundError as e:
    print(
        f"ERRO: Ficheiro não encontrado. Certifique-se de que 'listNames.json' e 'missaoSecreta.json' estão no mesmo diretório. Detalhes: {e}")
    exit()
except json.JSONDecodeError:
    print("ERRO: O ficheiro JSON está mal formatado. Por favor, verifique a sintaxe.")
    exit()

# Lista de participantes (Givers)
print(f"\nParticipantes carregados: {len(participantes)}")
print(f"Missoes carregadas: {len(missaoSecreta_data)}")

# Cria uma cópia da lista de missões para o 'pool'
missao_pool = list(missaoSecreta_data)
print(f"Local: {localJantar}\n")
amigos_secretos = []
missao_texto = ''
exemplo_missao = ''

# --- 2. Lógica de Sorteio Robusto ---
# Sorteio robusto: Garante que ninguém tira o seu próprio nome.
# 1. Criar uma lista de recetores (recipients)
recetores = participantes[:]

# 2. Baralhar a lista de recetores
random.shuffle(recetores)

# 3. Corrigir o sorteio se alguém calhar consigo mesmo (muito importante no Amigo Secreto)
# A rotação garante que a correspondência de nomes próprios é resolvida de forma aleatória.
max_tentativas = len(participantes)
tentativas = 0
while any(participantes[i]['nome'] == recetores[i]['nome'] for i in
          range(len(participantes))) and tentativas < max_tentativas:
    # Roda a lista de recetores por uma posição
    recetores = recetores[1:] + recetores[:1]
    tentativas += 1

if tentativas == max_tentativas:
    print("\nAVISO: Não foi possível realizar o sorteio sem auto-atribuição após várias tentativas. Tente novamente.")
    exit()

# Limpar o ficheiro anterior de amigos secretos
with open("amigos_secretos.txt", "w", encoding="utf-8") as arquivo_saida:
    arquivo_saida.write("--- LISTA DE AMIGOS SECRETOS E MENSAGENS ---\n\n")

# --- 3. Atribuição de Missão e Geração de Mensagens ---
print("Distribuição:")
for i in range(len(participantes)):
    #print("participante:", participantes[i])
    nomeParticipante = participantes[i].get("nome")
    nomeAmigoSecreto = recetores[i].get("nome")  # O recetor é o amigo secreto
    contactoParticipante = participantes[i].get("telefone")
    missaoSimOuNao = participantes[i].get("missão")
    #print("missão", missaoSimOuNao)
    secreto = ""
    print(f"{nomeParticipante} --> {nomeAmigoSecreto} (Missão: {missaoSimOuNao})")

    # Lógica de atribuição de Missão Secreta (apenas se 'sim')
    if missaoSimOuNao == "sim":
        if missao_pool:
            # 1. Escolher uma missão aleatória do pool
            chosen_mission_object = random.choice(missao_pool)
            print("mission_object:",chosen_mission_object)
            # 2. Extrair o texto da missão
            missao_texto = chosen_mission_object.get("missao", "Missão não especificada")
            exemplo_missao = chosen_mission_object.get("Exemplo", "Exemplo não fornecido")

            # 3. Remover a missão do pool para garantir que não se repete
            missao_pool.remove(chosen_mission_object)

            # 4. Construir o bloco secreto
            secreto = f"""\nEste ano há uma variação, e tens uma missão secreta associada. O sucesso desta missão depende unicamente de ti.
Tens de: {missao_texto}. Exemplo: {exemplo_missao}
Algumas pessoas têm as suas missões, outras não, também tens de descobrir.
Se por acaso, achas que descobriste a missão de alguém. Alinha! e não contes nada.
Assim, quem não descobriu tem tempo, e está em jogo, e quem não tem missão, continua confuso"""
        else:
            secreto = f"""Este ano, há supresas extras...Fica atento"""

    # Construção da mensagem
    mensagem = f"""\n{[i + 1]}) Olá, {nomeParticipante}! Bem vind@ à 💌 Missão de Natal.
Esta mensagem, apesar de enviada de um número pessoal, é o seu aviso oficial de Amigo Secreto!\nA sua missão é presentear o amigo-secreto: {nomeAmigoSecreto}!
🎁 Os Detalhes do Jogo:\nPreço: Aproximadamente {valor} (Sem exageros!)\nData de Entrega: 24/12/2025, na {localJantar}.
🎭 A Regra de Ouro: A entrega será feita num divertido jogo estilo "Pictionary de Comportamento":\nAntes de entregar o presente, terá de imitar um comportamento, mania ou expressão famosa da pessoa que o irá receber.
Só após ser adivinhado é que pode entregar o presente. O seu Amigo Secreto terá, por sua vez, de repetir a proeza para a pessoa que o presenteou.
❓ Dúvidas e Contactos: Em caso de dúvidas, a Maria Fernanda ou o encarregado desta mensagem terão todo o prazer em ajudar.\n
Boa criatividade e Divirte-te!
P.S. Mantenham o segredo! Especialmente casais (discrição máxima entre vocês!) e filhos (sejam subtis com os pais!).
P.S. 2. Para os menos íntimos: Não há desculpas! Criatividade é a chave. Desenrasquem-se! 😉
{secreto}
Mário Pedro
---------\n"""

    # Abrir e escrever no ficheiro de output
    with open("amigos_secretos.txt", "a", encoding="utf-8") as arquivo_saida:
        arquivo_saida.write(mensagem)

    # --- 4. Envio de SMS (Simulação) ---
    # A parte do envio de SMS é mantida, mas a URL não é funcional sem a chave.

    YOUR_API_KEY = 'whatsapp/'  # Chave API simulada
    YOUR_PHONE_NUMBER = '+320000000'  # Número simulado

    # Correção: usar o contactoParticipante (que é a string do número) e não a lista
    # Nota: Removido [1] do contactoParticipante, que só daria erro.

    # Construir a URL (Atenção: A API de SMS requer URL encoding, omitido para simplificar)
    url = f"https://api.smsapi.com/v1/sms/send?api_key={YOUR_API_KEY}&to={contactoParticipante}&from={YOUR_PHONE_NUMBER}&text={mensagem}"

    # Apenas simular o envio para evitar erros.
    # #Enviar a solicitação
    # response = requests.post(url)
    # 
    # #Verificar o código de resposta
    # if response.status_code == 200:
    #     print(f"SMS enviado com sucesso para {nomeParticipante}.")
    # else:
    #     print(f"Erro ao enviar SMS para {nomeParticipante}. (Status: {response.status_code})")
    print(f"SIMULAÇÃO: SMS seria enviado para {nomeParticipante} em {contactoParticipante}")

print("\n--- FIM DO SORTEIO ---")
print("Verifique o ficheiro 'amigos_secretos.txt' para as mensagens completas.")