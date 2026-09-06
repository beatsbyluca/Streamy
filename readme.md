<div align="center">

# Streamy

**24/7 Discord Streaming Status Keeper**

<p>
  <img src="https://img.shields.io/badge/-PYTHON-0d0d0d?style=for-the-badge&labelColor=0d0d0d&color=7c44ff" />
  <img src="https://img.shields.io/badge/-v1.0.1-0d0d0d?style=for-the-badge&labelColor=0d0d0d&color=7c44ff" />
</p>

<img src="https://cdn.beatsbyluca.com/files/7bc0b25f-1ed1-45a0-a5d4-206769f2afda" width="700" />

</div>

---

<p align="center"><img src="https://img.shields.io/badge/-ABOUT-0d0d0d?style=for-the-badge&labelColor=0d0d0d&color=7c44ff" /></p>

**Streamy** keeps a custom "Streaming" activity status active on your Discord account around the clock. It connects directly to the Discord Gateway, handles heartbeats, auto-reconnects on disconnect, and periodically refreshes the presence so it never times out.

- 🔴 Persistent "Streaming" activity with custom title & Twitch URL
- 🔁 Automatic reconnect with backoff on connection loss
- 🖼️ Custom presence image (Twitch preview, Discord CDN, or direct URL)
- ⚙️ Simple JSON config, no code editing required
- 🎨 Colored terminal logging with timestamps

---

<p align="center"><img src="https://img.shields.io/badge/-SETUP-0d0d0d?style=for-the-badge&labelColor=0d0d0d&color=7c44ff" /></p>

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure**

Create a `config.json` (or let the tool generate one on first run):
```json
{
    "token": "",
    "stream_title": "your title",
    "twitch_url": "https://www.twitch.tv/yourname",
    "status": "dnd",
    "image": "auto",
    "auto_reconnect": true
}
```

**3. Run**
```bash
python main.py
```

If no valid token is set, Streamy will prompt you for one on startup and save it to `config.json`.

---

<p align="center"><img src="https://img.shields.io/badge/-CONFIG-0d0d0d?style=for-the-badge&labelColor=0d0d0d&color=7c44ff" /></p>

| Key | Description |
|---|---|
| `token` | Your account token used to authenticate with the Gateway |
| `stream_title` | Text shown as the activity name |
| `twitch_url` | Twitch channel linked in the activity |
| `status` | Presence status (`online`, `idle`, `dnd`, `invisible`) |
| `image` | `"auto"` for Twitch preview, or a direct image URL |
| `auto_reconnect` | Keep reconnecting automatically on disconnect |

<div align="center">

`Streamy v1.0.1` · by **beatsbyluca**

</div>
