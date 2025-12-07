import random
import json
import os  # Para verificar a existência de ficheiros e limpeza
from dotenv import load_dotenv

# --- Classes de Modelo de Dados ---

class Participante:
    """Representa um participante do sorteio."""

    def __init__(self, nome: str, telefone: str, missao: str):
        self.nome = nome
        self.telefone = telefone
        self.tem_missao = missao.lower() == "sim"
        self.amigo_secreto = None  # O nome do recetor
        self.missao_atribuida = None  # O objeto de missão (dict)

    def __repr__(self):
        return f"Participante(Nome='{self.nome}', Missão={self.tem_missao})"


class SorteioConfig:
    """Contém configurações globais do evento."""

    def __init__(self, local_jantar: str, valor_presente: str, ficheiro_nomes: str, ficheiro_missoes: str, data_entrega: str, ficheiro_saida: str):
        self.local_jantar = local_jantar
        self.valor_presente = valor_presente
        self.ficheiro_nomes = ficheiro_nomes
        self.ficheiro_missoes = ficheiro_missoes
        self.data_entrega = data_entrega
        self.ficheiro_saida = ficheiro_saida
        print(f"Local jantar: {self.local_jantar}, Valor Presente: {self.valor_presente}, Data Entrega: {self.data_entrega}")

# --- Classe Principal de Lógica ---
class SorteioAmigoSecreto:
    """Gerencia o carregamento de dados, a lógica de sorteio e a geração de mensagens."""
    def __init__(self, config: SorteioConfig):
        self.config = config
        self.participantes = []
        self.missoes_pool = []
        # Os nomes dos ficheiros são acedidos via self.config
        print(f"A iniciar o sorteio de presentes de Natal 2025... - {config.local_jantar}")

    def _carregar_dados(self) -> bool:
        """Carrega os dados dos ficheiros JSON."""
        print("\n--- 1. Carregar Dados ---")

        # 1.1 Carregar Participantes
        try:
            with open(self.config.ficheiro_nomes, "r", encoding="utf-8") as arquivo_nomes:
                data_participantes = json.load(arquivo_nomes)
                self.participantes = [Participante(**p) for p in data_participantes]
                print(
                    f"...Ficheiro Participantes ({self.config.ficheiro_nomes}) carregado. Total: {len(self.participantes)}")
        except FileNotFoundError:
            print(f"ERRO: Ficheiro não encontrado: '{self.ficheiro_participantes}'")
            return False
        except json.JSONDecodeError:
            print(f"ERRO: O ficheiro JSON '{self.ficheiro_participantes}' está mal formatado.")
            return False

        # 1.2 Carregar Missões
        try:
            with open(self.config.ficheiro_missoes, "r", encoding="utf-8") as arquivosecreto:
                self.missoes_pool = json.load(arquivosecreto)  # Lista de dicts
                print(f"...Ficheiro ({self.config.ficheiro_missoes}) carregado. Total: {len(self.missoes_pool)}")
        except FileNotFoundError:
            print(f"ERRO: Ficheiro não encontrado: '{self.config.ficheiro_missoes}'")
            return False
        except json.JSONDecodeError:
            print(f"ERRO: O ficheiro JSON '{self.config.ficheiro_missoes}' está mal formatado.")
            return False
        return True

    def _realizar_sorteio_robusto(self) -> bool:
        """Realiza o sorteio garantindo que ninguém tira o próprio nome."""
        print("\n--- 2. Lógica de Sorteio Robusto ---")

        # Lista de participantes (Recipients) - A ser baralhada
        recetores = self.participantes[:]
        random.shuffle(recetores)

        max_tentativas = len(self.participantes) * 2  # Aumentar tentativas para maior segurança
        tentativas = 0

        while any(self.participantes[i].nome == recetores[i].nome for i in range(len(self.participantes))) and tentativas < max_tentativas:
            # Rotação da lista de recetores (os Amigos Secretos)
            recetores = recetores[1:] + recetores[:1]
            tentativas += 1

        if tentativas >= max_tentativas:
            print("\nAVISO: Não foi possível realizar o sorteio sem auto-atribuição após as tentativas.")
            return False

        total=0
        # Atribuir o amigo secreto a cada participante
        for i in range(len(self.participantes)):
            self.participantes[i].amigo_secreto = recetores[i].nome
            total += 1
            print(f"Sorteio: {self.participantes[i].nome} --> {self.participantes[i].amigo_secreto}")

        print(f"--------------------------------\nSorteio concluído com sucesso. Total: {total}")
        return True

    def _atribuir_missoes(self):
        """Atribui missões aos participantes marcados como 'sim'."""
        # Cria uma cópia da pool de missões para atribuição, garantindo que não se repete
        missoes_disponiveis = list(self.missoes_pool)
        total = 0
        print("\nDistribuir missoes:...")
        for participante in self.participantes:
            if participante.tem_missao:
                if missoes_disponiveis:
                    # Escolher e remover a missão do pool
                    missao_escolhida = random.choice(missoes_disponiveis)
                    participante.missao_atribuida = missao_escolhida
                    missoes_disponiveis.remove(missao_escolhida)
                    total += 1
                    print(f"Missão atribuída a: {participante.nome}")

                else:
                    # Se não houver missões disponíveis, atribui uma mensagem padrão
                    #participante.missao_atribuida = {"missao": "Fica atento", "Exemplo": "Surpresa extra"}
                    print(f"Sem missões disponíveis para: {participante.nome}. Atribuído aviso.")
        print(f"-----------------------------------\nTotal de missoes atribuidas: {total}\n")

    def _gerar_mensagem_secreta(self, participante: Participante) -> str:
        """Gera o bloco de texto 'secreto' (missão ou aviso)."""
        if participante.tem_missao and participante.missao_atribuida:
            missao_texto = participante.missao_atribuida.get("missao", "Missão não especificada")
            exemplo_missao = participante.missao_atribuida.get("Exemplo", "Exemplo não fornecido")

            return f"""\nEste ano há uma variação, e tens uma **missão secreta** associada. O sucesso desta missão depende unicamente de ti.
Tens de: **{missao_texto}**. Exemplo: {exemplo_missao}
Algumas pessoas têm as suas missões, outras não, também tens de descobrir.
Se por acaso, achas que descobriste a missão de alguém. Alinha! e não contes nada.
Assim, quem não descobriu tem tempo, e está em jogo, e quem não tem missão, continua confuso"""
        else:
            return f"""\nEste ano, há surpresas extras...Fica atento"""

    def _gerar_mensagem_completa(self, participante: Participante) -> str:
        """Constrói a mensagem completa para um participante."""
        secreto = self._gerar_mensagem_secreta(participante)

        mensagem = f"""\nOlá, {participante.nome}! Bem vind@ à 💌 Missão de Natal.
Esta mensagem, apesar de enviada de um número pessoal, é o seu aviso oficial de Amigo Secreto!
A sua missão é presentear o amigo-secreto: **{participante.amigo_secreto}**!
🎁 Os Detalhes do Jogo:
Preço: Aproximadamente **{self.config.valor_presente}** (Sem exageros!)
Data de Entrega: **{self.config.data_entrega}**, na **{self.config.local_jantar}**.
🎭 A Regra de Ouro: A entrega será feita num divertido jogo estilo "**Pictionary de Comportamento**":
Antes de entregar o presente, terá de imitar um comportamento, mania ou expressão famosa da pessoa que o irá receber.
Só após ser adivinhado é que pode entregar o presente. O seu Amigo Secreto terá, por sua vez, de repetir a proeza para a pessoa que o presenteou.
❓ Dúvidas e Contactos: Em caso de dúvidas, a Maria Fernanda ou o encarregado desta mensagem terão todo o prazer em ajudar.

Boa criatividade e Divirte-te!
P.S. Mantenham o segredo! Especialmente casais (discrição máxima entre vocês!) e filhos (sejam subtis com os pais!).
P.S. 2. Para os menos íntimos: Não há desculpas! Criatividade é a chave. Desenrasquem-se! 😉
{secreto}
Mário Pedro
---------\n"""
        return mensagem

    def _simular_envio_sms(self, participante: Participante, mensagem: str):
        """Simula a parte de envio de SMS."""
        # Ler diretamente do ambiente
        YOUR_API_KEY = os.getenv('API_KEY', 'default_key')
        YOUR_PHONE_NUMBER = os.getenv('PHONE_NUMBER', '+000000000')

        # A URL de SMS seria construída aqui, mas a chamada requests é omitida
        url_simulada = f"https://api.smsapi.com/v1/sms/send?api_key={YOUR_API_KEY}&to={participante.telefone}&from={YOUR_PHONE_NUMBER}&text=..."

        # Simulação
        print(f"SIMULAÇÃO: SMS seria enviado para {participante.nome} em {participante.telefone}")
        print(f"URL: {url_simulada[:120]}...")

    def executar_sorteio(self):
        """Método principal que orquestra todo o processo."""

        if not self._carregar_dados():
            return

        if not self._realizar_sorteio_robusto():
            return

        self._atribuir_missoes()
        print("--- 3. Geração de Mensagens e Simulação de Envio ---")

        # Limpar o ficheiro anterior
        with open(configuracao.ficheiro_saidaa, "w", encoding="utf-8") as arquivo_saida:
            arquivo_saida.write("--- LISTA DE AMIGOS SECRETOS E MENSAGENS ---\n\n")

        # Gerar mensagens, salvar e simular envio
        for i, participante in enumerate(self.participantes):
            mensagem_completa = self._gerar_mensagem_completa(participante)

            # Adicionar índice de série para o ficheiro
            mensagem_com_indice = f"\n{[i + 1]}){mensagem_completa[1:]}"

            # Escrever no ficheiro de output
            with open(configuracao.ficheiro_saida, "a", encoding="utf-8") as arquivo_saida:
                arquivo_saida.write(mensagem_com_indice)

            # Simular Envio
            self._simular_envio_sms(participante, mensagem_completa)

        print("\n--- FIM DO SORTEIO ---")
        print(f"Verifique o ficheiro '{configuracao.ficheiro_saida}' para as mensagens completas.")


# --- Execução Principal (Ponto de Entrada) ---
if __name__ == "__main__":
    # Carregar as variáveis do ficheiro .env para o ambiente
    load_dotenv()

    print("...Configurações lidas do .env")

    # 1. Configurar o evento, lendo diretamente do ambiente (os.environ ou os.getenv)
    configuracao = SorteioConfig(
        local_jantar=os.getenv("LOCAL_JANTAR"),
        valor_presente=os.getenv("VALOR_PRESENTE"),
        ficheiro_nomes=os.getenv("FICHEIRO_NOMES"),
        ficheiro_missoes=os.getenv("FICHEIRO_MISSOES"),
        data_entrega=os.getenv("DATA_ENTREGA"),
        ficheiro_saida=os.getenv("FICHEIRO_SAIDA")
    )

    # 2. Instanciar e Executar
    sorteio_app = SorteioAmigoSecreto(configuracao)
    sorteio_app.executar_sorteio()