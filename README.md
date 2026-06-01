# 💌 SecretSanta – Christmas Mission

Website and backend to organize a **Secret Santa with secret missions**. The organizer enters the participants; the draw is done instantly, and each person receives a **personal link** via WhatsApp where they can see their Secret Santa match, their mission, and event details. No one (not even the organizer) can see anyone else's draw.

## Features
- Upload participants from a file (`.json` or `.txt` with `Name; phone; mission; group` lines) directly in your browser.
- Web form: participants (name, phone), location, budget, date, and contact person for questions.
- Mission per person: **with**, **without**, or **random** (50%). Missions are pulled from `missaoSecreta.json` and are never repeated.
- Groups (couples, families): people in the same group won't draw each other. No one draws themselves.
- Ready-to-send WhatsApp message per person (`wa.me`), with a link to their personal page.
- Control file (`ficheiro_controlo.txt`) tracking who drew whom, kept exclusively on the server for the controller.
- Header with links to support the project (Revolut / Buy Me a Coffee).

## Missions: With, Without, or Random
The mission is an extra challenge, randomly chosen from `missaoSecreta.json` and never repeated. **With mission**: always receives one. **Without mission**: never receives one. **Random (50%)**: the system decides at random whether they get one or not. This is independent of who draws whom.

## Structure
```text
app.py                      Flask Backend (API + pages)
secret_santa/core.py        Draw logic, missions, messages, storage
SecretDistribution.py       Terminal mode, no website
static/                     Front-end (index, admin, reveal)
missaoSecreta.json          List of missions (theme, mission, example)
exemplo_participantes.json  Example for terminal mode
.env.example                Configuration (copy to .env)
```
Draw data is stored in `data/` and control data in `ficheiro_controlo.txt`. Both are included in `.gitignore`.

## Installation
```bash
pip install -r requirements.txt
cp .env.example .env      # edit values
python app.py             # http://localhost:5000
```
Production: Run `gunicorn app:app` behind your domain with HTTPS and configure `LINK_DOMINIO`, ensuring the message links are correct.

## Usage
1. Open the website, fill in the event and participant details, and click **Draw and Generate Links**.
2. On the next page, click **Send on WhatsApp** for each person. **Bookmark the page**.
3. Each person opens their link, taps the gift tag, and sees their Secret Santa match and mission.
4. Controller: check `ficheiro_controlo.txt` on the server.

### Terminal Mode (No Website)
Create `listNames.json` (see `exemplo_participantes.json`; `missao`: `sim`, `nao`, or `aleatorio`; `grupo` is optional) and run:
```bash
python SecretDistribution.py            # prints WhatsApp links
python SecretDistribution.py --enviar   # sends via WhatsApp Web (requires pywhatkit)
```

## Configuration (`.env`)
| Variable | Description |
|---|---|
| `LOCAL_JANTAR`, `VALOR_PRESENTE`, `DATA_ENTREGA`, `CONTACTO` | Default values for the form and message |
| `LINK_DOMINIO` | Public domain of the website |
| `INDICATIVO_PAIS` | Country code for 9-digit phone numbers (default `351`) |
| `APOIO_PAYPAL`, `APOIO_REVOLUT`, `APOIO_BUYMEACOFFEE` | Links for the "Support" window in the header (leave empty to hide) |
| `DATA_DIR`, `FICHEIRO_MISSOES`, `FICHEIRO_CONTROLO`, `FICHEIRO_NOMES` | File paths |

## Invite Status
On the admin page, you can see who has tapped their gift tag (and when), without seeing who they drew.

## Links in Messages
`LINK_DOMINIO` must be an address accessible to your guests. `localhost` only works on your computer. For testing, use a tunnel (e.g., Cloudflare Tunnel or ngrok) and put that address in your `.env`.

## Privacy
Each link has a hard-to-guess random token. All data (including phone numbers) stays solely on your server. Delete the `data/` folder after the event.

License: see `LICENSE`.