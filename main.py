import os
import sys
import time
import json
import random
import signal
import threading
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import colorama
    from colorama import Fore
    from pystyle import Colors, Colorate
except ImportError:
    os.system(f'"{sys.executable}" -m pip install colorama pystyle')
    import colorama
    from colorama import Fore
    from pystyle import Colors, Colorate

try:
    import websocket
except ImportError:
    os.system(f'"{sys.executable}" -m pip install websocket-client')
    import websocket

try:
    colorama.just_fix_windows_console()
except Exception:
    colorama.init(autoreset=True)

CONFIG_FILE = Path(__file__).parent / "config.json"
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"

def print_header():
    os.system("cls" if os.name == "nt" else "clear")
    text = """
███████╗████████╗██████╗ ███████╗ █████╗ ███╗   ███╗██╗   ██╗
██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗ ████║╚██╗ ██╔╝
███████╗   ██║   ██████╔╝█████╗  ███████║██╔████╔██║ ╚████╔╝ 
╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║  ╚██╔╝  
███████║   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║   ██║   
╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝   """

    try:
        terminal_width = os.get_terminal_size().columns
    except Exception:
        terminal_width = 80

    lines = text.strip("\n").splitlines()
    max_len = max(len(line) for line in lines)
    
    centered_lines = []
    for line in lines:
        left_padding = max(0, (terminal_width - max_len) // 2)
        centered_lines.append((" " * left_padding) + line.ljust(max_len))
    
    full_centered_text = "\n".join(centered_lines)
    
    print()
    print(Colorate.Vertical(Colors.purple_to_blue, full_centered_text))
    
    version_text = "Streamy v.1.0.1 by Beatsbyluca"
    print(version_text.center(terminal_width))
    print()

def log(msg: str, status: str = "info"):
    timestamp = f"{Fore.LIGHTBLACK_EX}[{time.strftime('%H:%M:%S')}]{Fore.RESET}"
    if status == "info":
        prefix = f"{Fore.BLUE}[INFO]{Fore.RESET}"
    elif status == "success":
        prefix = f"{Fore.GREEN}[SUCCESS]{Fore.RESET}"
    elif status == "error":
        prefix = f"{Fore.RED}[ERROR]{Fore.RESET}"
    elif status == "wait":
        prefix = f"{Fore.YELLOW}[WAIT]{Fore.RESET}"
    else:
        prefix = f"{Fore.BLUE}[INFO]{Fore.RESET}"
    
    print(f"{timestamp} {prefix} {msg}", flush=True)

def mask_token(token: str) -> str:
    if not token or len(token) < 15:
        return "***"
    return f"{token[:8]}...{token[-5:]}"

def load_or_create_config() -> dict:
    default_config = {
        "token": "",
        "stream_title": "₉⁹₉",
        "twitch_url": "https://www.twitch.tv/beatsbylxca",
        "status": "dnd",
        "image": "https://cdn.beatsbyluca.com/files/907fb3a9-43a6-4921-b86f-ea128f0683fa",
        "auto_reconnect": True
    }

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return default_config

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            for k, v in default_config.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
    except Exception as e:
        log(f"Failed to load {CONFIG_FILE.name}: {e}", "error")
        return default_config

def save_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log(f"Could not save config: {e}", "error")

def prompt_user_for_token(config: dict) -> dict:
    token = ""
    while not token.strip():
        token = input("Discord User Token: ").strip().strip('"').strip("'")
    
    stream_title = input(f"Stream Title [{config.get('stream_title', 'Live')}]: ").strip()
    if not stream_title:
        stream_title = config.get("stream_title", "Live")

    twitch_url = input(f"Twitch URL [{config.get('twitch_url', 'https://www.twitch.tv/beatsbylxca')}]: ").strip()
    if not twitch_url:
        twitch_url = config.get("twitch_url", "https://www.twitch.tv/beatsbylxca")

    config["token"] = token
    config["stream_title"] = stream_title
    config["twitch_url"] = twitch_url
    save_config(config)
    return config

class DiscordStreamKeeper:
    def __init__(self, config: dict):
        self.config = config
        self.token = config.get("token", "").strip().strip('"').strip("'")
        self.stream_title = config.get("stream_title", "Streaming")
        self.twitch_url = config.get("twitch_url", "https://www.twitch.tv/beatsbylxca")
        self.status = config.get("status", "dnd")
        self.details = config.get("details", "")
        self.image = config.get("image", "")
        
        self.ws = None
        self.send_lock = threading.Lock()
        self.heartbeat_interval = None
        self.heartbeat_thread = None
        self.refresh_thread = None
        self.stop_event = threading.Event()
        self.last_sequence = None
        self.heartbeat_ack_received = True
        self.missed_acks = 0
        self.start_time = None
        self.heartbeat_count = 0
        self.is_connected = False
        self.user_info = {}
        self.fatal_error = False

    def get_uptime(self) -> str:
        if not self.start_time:
            return "00:00:00"
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def extract_twitch_username(self) -> str:
        cleaned = self.twitch_url.rstrip("/").split("/")[-1]
        return cleaned if cleaned else "twitch"

    def build_presence_payload(self) -> dict:
        activity = {
            "name": self.stream_title,
            "type": 1,
            "url": self.twitch_url
        }

        if self.details:
            activity["details"] = self.details

        if self.image:
            img_val = str(self.image).strip()
            if img_val.lower() in ("twitch", "auto", "default"):
                tw_user = self.extract_twitch_username()
                activity["application_id"] = "378873147864776704"
                activity["assets"] = {
                    "large_image": f"twitch:{tw_user}"
                }
            elif "cdn.discordapp.com/attachments/" in img_val:
                asset_key = "mp:attachments/" + img_val.split("attachments/")[-1]
                activity["assets"] = {
                    "large_image": asset_key
                }
            elif img_val.startswith("http://") or img_val.startswith("https://"):
                activity["assets"] = {
                    "large_image": img_val
                }
            elif img_val:
                activity["assets"] = {
                    "large_image": img_val
                }

        return {
            "op": 3,
            "d": {
                "since": 0,
                "activities": [activity],
                "status": self.status,
                "afk": False
            }
        }

    def build_identify_payload(self) -> dict:
        presence = self.build_presence_payload()["d"]
        return {
            "op": 2,
            "d": {
                "token": self.token,
                "capabilities": 30717,
                "properties": {
                    "os": "Windows",
                    "browser": "Chrome",
                    "device": "",
                    "system_locale": "de-DE",
                    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                    "browser_version": "128.0.0.0",
                    "os_version": "10.0.22631",
                    "release_channel": "stable",
                    "client_build_number": 344400
                },
                "presence": presence,
                "compress": False
            }
        }

    def send_json(self, payload: dict) -> bool:
        with self.send_lock:
            if not self.ws or not self.ws.connected:
                return False
            try:
                self.ws.send(json.dumps(payload))
                return True
            except Exception as e:
                log(f"Failed to send data: {e}", "wait")
                return False

    def heartbeat_worker(self):
        jitter = random.uniform(0.1, 0.8)
        time.sleep(self.heartbeat_interval * jitter)

        while not self.stop_event.is_set():
            if not self.heartbeat_ack_received:
                self.missed_acks += 1
                if self.missed_acks >= 2:
                    log("Connection lost (missed Heartbeat ACKs). Reconnecting...", "wait")
                    if self.ws:
                        try:
                            self.ws.close()
                        except Exception:
                            pass
                    break
            else:
                self.missed_acks = 0

            self.heartbeat_ack_received = False
            hb_payload = {
                "op": 1,
                "d": self.last_sequence
            }
            if not self.send_json(hb_payload):
                break

            if self.stop_event.wait(timeout=self.heartbeat_interval):
                break

    def periodic_presence_refresher(self):
        while not self.stop_event.is_set():
            if self.stop_event.wait(timeout=600):
                break
            if self.is_connected:
                self.send_json(self.build_presence_payload())

    def connect(self) -> bool:
        self.stop_event.clear()
        self.last_sequence = None
        self.heartbeat_ack_received = True
        self.missed_acks = 0
        self.is_connected = False

        log("Connecting to Discord Gateway...", "info")

        try:
            self.ws = websocket.create_connection(
                GATEWAY_URL,
                timeout=30,
                enable_multithread=True
            )
            self.ws.settimeout(None)
        except Exception as e:
            log(f"Connection failed: {e}", "error")
            return False

        try:
            while not self.stop_event.is_set():
                try:
                    opcode, raw_bytes = self.ws.recv_data()
                except (websocket.WebSocketTimeoutException, TimeoutError):
                    continue

                if opcode == websocket.ABNF.OPCODE_CLOSE:
                    close_code = int.from_bytes(raw_bytes[:2], "big") if len(raw_bytes) >= 2 else None
                    reason = raw_bytes[2:].decode("utf-8", errors="ignore") if len(raw_bytes) > 2 else ""
                    
                    if close_code == 4004:
                        log(f"Authentication failed (Code 4004: {reason})", "error")
                        log(f"Token invalid. Please verify {CONFIG_FILE.name}", "wait")
                        self.fatal_error = True
                    elif close_code == 4008:
                        log("Rate limit reached. Waiting before reconnect...", "wait")
                    else:
                        log(f"Connection closed ({close_code}): {reason}", "wait")
                    break

                if opcode != websocket.ABNF.OPCODE_TEXT:
                    continue

                raw_data = raw_bytes.decode("utf-8")
                data = json.loads(raw_data)
                op = data.get("op")
                seq = data.get("s")
                event_type = data.get("t")
                payload = data.get("d")

                if seq is not None:
                    self.last_sequence = seq

                if op == 10:
                    raw_interval = payload.get("heartbeat_interval", 41250)
                    self.heartbeat_interval = raw_interval / 1000.0

                    self.heartbeat_thread = threading.Thread(target=self.heartbeat_worker, daemon=True)
                    self.heartbeat_thread.start()

                    log(f"Authenticating token {mask_token(self.token)}", "info")
                    self.send_json(self.build_identify_payload())

                elif op == 11:
                    self.heartbeat_ack_received = True
                    self.heartbeat_count += 1
                    log(f"Heartbeat #{self.heartbeat_count} OK | Uptime: {self.get_uptime()}", "info")

                elif op == 1:
                    self.send_json({"op": 1, "d": self.last_sequence})

                elif op == 7:
                    log("Discord requested reconnect (OP 7).", "wait")
                    break

                elif op == 9:
                    can_resume = payload if isinstance(payload, bool) else False
                    log(f"Session invalid (OP 9, resume={can_resume}).", "wait")
                    time.sleep(2)
                    break

                elif op == 0:
                    if event_type == "READY":
                        self.is_connected = True
                        if not self.start_time:
                            self.start_time = time.time()

                        user = payload.get("user", {})
                        self.user_info = user
                        username = user.get("username", "Unknown")
                        discrim = user.get("discriminator", "0")
                        user_tag = f"{username}#{discrim}" if discrim != "0" else f"@{username}"
                        user_id = user.get("id", "Unknown")

                        if not self.refresh_thread or not self.refresh_thread.is_alive():
                            self.refresh_thread = threading.Thread(target=self.periodic_presence_refresher, daemon=True)
                            self.refresh_thread.start()

                        log(f"Logged in as {user_tag} (ID: {user_id})", "success")
                        log(f"Streaming: {self.stream_title} | URL: {self.twitch_url}", "info")
                        log(f"Status: {self.status.upper()} | 24/7 Streamy Active!", "success")

                    elif event_type == "RESUMED":
                        log("Session resumed successfully.", "success")

        except (websocket.WebSocketConnectionClosedException, ConnectionResetError, BrokenPipeError) as e:
            log(f"Connection lost: {e}", "wait")
        except Exception as e:
            log(f"Gateway error: {e}", "error")
        finally:
            self.stop_event.set()
            self.is_connected = False
            if self.ws:
                try:
                    self.ws.close()
                except Exception:
                    pass

        return True

    def run_forever(self):
        print_header()
        log("Initializing Streamy...", "info")
        log("Configuration loaded.", "success")
        reconnect_delay = 5

        while True:
            try:
                self.connect()

                if self.fatal_error:
                    answer = input("Enter new token? (y/n): ").strip().lower()
                    if answer in ("y", "yes", "j", "ja"):
                        self.config = prompt_user_for_token(self.config)
                        self.token = self.config.get("token", "").strip().strip('"').strip("'")
                        self.fatal_error = False
                        continue
                    else:
                        break

                if not self.config.get("auto_reconnect", True):
                    break

                log(f"Reconnecting in {reconnect_delay}s...", "wait")
                time.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay + 5, 60)

            except KeyboardInterrupt:
                print()
                log("Stopped by user (Ctrl + C).", "wait")
                self.stop_event.set()
                if self.ws:
                    try:
                        self.ws.close()
                    except Exception:
                        pass
                break

def main():
    def sig_handler(sig, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)

    config = load_or_create_config()
    token = config.get("token", "").strip()

    if not token or token == "DEIN_DISCORD_TOKEN_HIER" or len(token) < 20:
        config = prompt_user_for_token(config)

    keeper = DiscordStreamKeeper(config)
    keeper.run_forever()

if __name__ == "__main__":
    main()
