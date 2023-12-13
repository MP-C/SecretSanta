# SecretSanta
To randomise a names list to christmas
Secret Santa

This repository contains a Python code to perform a secret Santa draw for Christmas. The code generates a random list of secret Santas and sends an SMS message to each participant with the name of their secret Santa.

Requirements:

Python 3.6 or higher
random library
requests library

Installation:
To install the required libraries, run the following command:

pip install -r requirements.txt
Usage:
To use the code, follow these steps:

Create a JSON file called listNames.json with a list of participant names.
Edit the secretSanta.py file to specify the SMS API information.
Run the following command to draw the secret Santas and send the SMS messages:
python secretSanta.py
Example of a list of names:

[
"João",
"Maria",
"Pedro",
"Ana",
"José"
]
Example of SMS API information:

api_key = "YOUR_API_KEY"
sender_id = "YOUR_SENDER_ID"
Example of an SMS message:

Hi, [name],

This message is automatic, even though it is sent from a personal number.

The purpose is to inform you who your secret Santa is, who is [name_of_secret_santa].

You must deliver a gift worth +/- 5€ on December 24, 2023, at the Casa da Aldeia.

The gift will be delivered in the form of a game (like Pictionary).

That is, before you can deliver the gift, you must imitate a characteristic/behavior/mannerism/expression and only when it is guessed can it be delivered. Your secret Santa will in turn repeat the feat.

If you have any questions, please contact Maria Fernanda or the person in charge of this message.

Thank you!
