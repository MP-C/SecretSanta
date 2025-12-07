import random
import json
import os  # To check for file existence and cleanup
import time  # Added for pywhatkit delay

from dotenv import load_dotenv
import pywhatkit
import pyautogui
from pynput.keyboard import Key, Controller

# Initialize pynput Controller for keyboard actions
keyboard = Controller()


# --- Data Model Classes ---
class Participant:
    """Represents a participant in the draw."""

    # Note: 'missao' (with accent) is kept for compatibility with the JSON structure
    def __init__(self, nome: str, telefone: str, missao: str):
        self.name = nome
        self.phone = telefone
        self.has_mission = missao.lower() == "sim"
        self.secret_friend = None  # The recipient's name
        self.assigned_mission = None  # The mission object (dict)

    def __repr__(self):
        return f"Participant(Name='{self.name}', HasMission={self.has_mission})"


class DrawConfig:
    """Contains global event settings."""

    def __init__(self, dinner_location: str, gift_value: str, names_file: str, missions_file: str, delivery_date: str,
                 output_file: str):
        self.dinner_location = dinner_location
        self.gift_value = gift_value
        self.names_file = names_file
        self.missions_file = missions_file
        self.delivery_date = delivery_date
        self.output_file = output_file
        print(
            f"Dinner Location: {self.dinner_location}, Gift Value: {self.gift_value}, Delivery Date: {self.delivery_date}")


# --- Main Logic Class ---
class SecretSantaDraw:
    """Manages data loading, draw logic, and message generation."""

    def __init__(self, config: DrawConfig):
        self.config = config
        self.participants = []
        self.missions_pool = []
        # File names are accessed via self.config
        print(f"Starting Secret Santa 2025 draw... - {config.dinner_location}")

    def _load_data(self) -> bool:
        """Loads data from JSON files."""
        print("\n--- 1. Loading Data ---")

        # 1.1 Load Participants
        try:
            with open(self.config.names_file, "r", encoding="utf-8") as name_file_handle:
                participant_data = json.load(name_file_handle)
                # The 'missao' key in JSON must match the constructor argument
                self.participants = [Participant(**p) for p in participant_data]
                print(
                    f"...Participants File ({self.config.names_file}) loaded. Total: {len(self.participants)}")
        except FileNotFoundError:
            print(f"ERROR: File not found: '{self.config.names_file}'")
            return False
        except json.JSONDecodeError:
            print(f"ERROR: The JSON file '{self.config.names_file}' is badly formatted.")
            return False

        # 1.2 Load Missions
        try:
            with open(self.config.missions_file, "r", encoding="utf-8") as secret_file_handle:
                self.missions_pool = json.load(secret_file_handle)  # List of dicts
                print(f"...File ({self.config.missions_file}) loaded. Total: {len(self.missions_pool)}")
        except FileNotFoundError:
            print(f"ERROR: File not found: '{self.config.missions_file}'")
            return False
        except json.JSONDecodeError:
            print(f"ERROR: The JSON file '{self.config.missions_file}' is badly formatted.")
            return False
        return True

    def _perform_robust_draw(self) -> bool:
        """Performs the draw, ensuring no one draws their own name."""
        print("\n--- 2. Robust Distribuition Logic ---")

        # List of recipients - To be shuffled
        recipients = self.participants[:]
        random.shuffle(recipients)

        max_attempts = len(self.participants) * 2
        attempts = 0

        # Rotate the list if any participant matches themselves
        while any(self.participants[i].name == recipients[i].name for i in
                  range(len(self.participants))) and attempts < max_attempts:
            # Rotate the recipients list (the Secret Friends)
            recipients = recipients[1:] + recipients[:1]
            attempts += 1

        if attempts >= max_attempts:
            print("\nWARNING: Could not perform the draw without self-assignment after multiple attempts.")
            return False

        total = 0
        # Assign the secret friend to each participant
        for i in range(len(self.participants)):
            self.participants[i].secret_friend = recipients[i].name
            total += 1
            print(f"Distribuition: {self.participants[i].name} --> {self.participants[i].secret_friend}")

        print(f"--------------------------------\nDistribuition concluded successfully. Total: {total}")
        return True

    def _assign_missions(self):
        """Assigns missions to participants marked with 'sim'."""
        # Create a copy of the mission pool for assignment, ensuring no repetition
        available_missions = list(self.missions_pool)
        total = 0
        print("\nDistributing missions:...")
        for participant in self.participants:
            if participant.has_mission:
                if available_missions:
                    # Choose and remove the mission from the pool
                    chosen_mission = random.choice(available_missions)
                    participant.assigned_mission = chosen_mission
                    available_missions.remove(chosen_mission)
                    total += 1
                    print(f"Mission assigned to: {participant.name}")

                else:
                    # If no missions are available, assign a default message
                    # participant.assigned_mission = {"missao": "Fica atento", "Exemplo": "Surpresa extra"}
                    print(f"No missions available for: {participant.name}. Assigned warning.")
        print(f"-----------------------------------\nTotal missions assigned: {total}\n")

    def _generate_secret_message(self, participant: Participant) -> str:
        """Generates the 'secret' text block (mission or warning)."""
        if participant.has_mission and participant.assigned_mission:
            missao_texto = participant.assigned_mission.get("missao", "missao não especificada")
            exemplo_missao = participant.assigned_mission.get("Exemplo", "Exemplo não fornecido")

            # MANTIDO EM PORTUGUÊS
            return f"""\nEste ano há uma variação, e tens uma **missao secreta** associada. O sucesso desta missao depende unicamente de ti.
Tens de: **{missao_texto}**. Exemplo: {exemplo_missao}
Algumas pessoas têm as suas missões, outras não, também tens de descobrir.
Se por acaso, achas que descobriste a missao de alguém. Alinha! e não contes nada.
Assim, quem não descobriu tem tempo, e está em jogo, e quem não tem missao, continua confuso"""
        else:
            # MANTIDO EM PORTUGUÊS
            return f"""\nEste ano, há surpresas extras...Fica atento"""

    def _generate_full_message(self, participant: Participant) -> str:
        """Constructs the complete message for a participant."""
        secret = self._generate_secret_message(participant)

        # MANTIDO EM PORTUGUÊS
        message = f"""\nOlá, {participant.name}! Bem vind@ à 💌 missao de Natal.
Esta mensagem, apesar de enviada de um número pessoal, é o seu aviso oficial de Amigo Secreto!
A sua missao é presentear o amigo-secreto: {participant.secret_friend}!
🎁 Os Detalhes do Jogo:
Preço: Aproximadamente {self.config.gift_value} (Sem exageros!).
Data de Entrega: {self.config.delivery_date}, na {self.config.dinner_location}.
🎭 A Regra de Ouro: A entrega será feita num divertido jogo estilo "Pictionary de Comportamento":
Antes de entregar o presente, terá de imitar um comportamento, mania ou expressão famosa da pessoa que o irá receber.
Só após ser adivinhado é que pode entregar o presente. O seu Amigo Secreto terá, por sua vez, de repetir a proeza para a pessoa que o presenteou.
❓ Dúvidas e Contactos: Em caso de dúvidas, a Maria Fernanda ou o encarregado desta mensagem terão todo o prazer em ajudar.

Boa criatividade e Divirte-te!
P.S. Mantenham o segredo! Especialmente casais (discrição máxima entre vocês!) e filhos (sejam subtis com os pais!).
P.S. 2. Para os menos íntimos: Não há desculpas! Criatividade é a chave. Desenrasquem-se! 😉
{secret}
---------\n"""
        return message

    def _simulate_sms_sending(self, participant: Participant, message: str):
        """Simulates the SMS sending part (using pywhatkit for WhatsApp simulation)."""
        # Read from the environment (API keys are not used by pywhatkit but kept for context)
        YOUR_API_KEY = os.getenv('API_KEY')
        YOUR_PHONE_NUMBER = os.getenv('PHONE_NUMBER')

        """ To send via browser"""
        print(f"SMS would be sent to {participant.name} at {participant.phone}")
        # pywhatkit.sendwhatmsg(participant.phone, "teste",23,18,25,False,10) # Example of scheduled message
        try:
            # Using sendwhatmsg_instantly for direct message
            pywhatkit.sendwhatmsg_instantly(phone_no=participant.phone, message=message, tab_close=True)

            # pywhatkit needs a few seconds to open WhatsApp web
            time.sleep(10)

            # Use pyautogui to click the send button or area
            pyautogui.click()
            time.sleep(2)

            # Use pynput to press Enter (sending the message)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            print("Message sent!")

        except Exception as e:
            print(f"Error during WhatsApp sending simulation: {str(e)}")

    def run_draw(self):
        """Main method that orchestrates the entire process."""

        if not self._load_data():
            return

        if not self._perform_robust_draw():
            return

        self._assign_missions()
        print("--- 3. Message Generation and Sending Simulation ---")

        # Clear the previous output file
        with open(configuracao.output_file, "w", encoding="utf-8") as output_file_handle:
            output_file_handle.write("--- LISTA DE AMIGOS SECRETOS E MENSAGENS ---\n\n")

        # Generate messages, save, and simulate sending
        for i, participant in enumerate(self.participants):
            full_message = self._generate_full_message(participant)

            # Add serial index for the file
            message_with_index = f"\n{[i + 1]}){full_message[1:]}"

            # Write to the output file
            with open(configuracao.output_file, "a", encoding="utf-8") as output_file_handle:
                output_file_handle.write(message_with_index)

            # Simulate Sending
            self._simulate_sms_sending(participant, full_message)

        print("\n--- END OF DRAW ---")
        print(f"Check the file '{configuracao.output_file}' for the complete messages.")


# --- Main Execution Block (Entry Point) ---
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    print("...Settings read from .env")

    # 1. Configure the event, reading directly from the environment
    configuracao = DrawConfig(
        dinner_location=os.getenv("LOCAL_JANTAR"),
        gift_value=os.getenv("VALOR_PRESENTE"),
        names_file=os.getenv("FICHEIRO_NOMES"),
        missions_file=os.getenv("FICHEIRO_MISSOES"),
        delivery_date=os.getenv("DATA_ENTREGA"),
        output_file=os.getenv("FICHEIRO_SAIDA")
    )

    # 2. Instantiate and Execute
    draw_app = SecretSantaDraw(configuracao)
    draw_app.run_draw()