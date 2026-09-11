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
    from colorama import Fore, Style
    from pystyle import Colors, Colorate
except ImportError:
    os.system(f'"{sys.executable}" -m pip install colorama pystyle')
    import colorama
    from colorama import Fore, Style
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

DEFAULT_PLATFORMS = ["desktop", "web", "mobile", "console", "vr"]

PLATFORM_PROPERTIES = {
    "desktop": {
        "os": "Windows",
        "browser": "Discord Client",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "browser_version": "124.0.0.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
    },
    "web": {
        "os": "Windows",
        "browser": "Discord Web",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "browser_version": "124.0.0.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
    },
    "mobile": {
        "os": "iOS",
        "browser": "Discord iOS",
        "device": "iPhone16,2",
        "system_locale": "en-US",
        "browser_user_agent": "Discord/268.0 CFNetwork/1474 Darwin/23.0.0",
        "browser_version": "268.0",
        "os_version": "17.4.1",
        "referrer": "",
        "referring_domain": "",
    },
    "ios": {
        "os": "iOS",
        "browser": "Discord iOS",
        "device": "iPhone16,2",
        "system_locale": "en-US",
        "browser_user_agent": "Discord/268.0 CFNetwork/1474 Darwin/23.0.0",
        "browser_version": "268.0",
        "os_version": "17.4.1",
        "referrer": "",
        "referring_domain": "",
    },
    "android": {
        "os": "Android",
        "browser": "Discord Android",
        "device": "Pixel 8",
        "system_locale": "en-US",
        "browser_user_agent": "Discord-Android/214116;ROM:13;Device:Pixel 8",
        "browser_version": "214.116",
        "os_version": "13",
        "referrer": "",
        "referring_domain": "",
    },
    "console": {
        "os": "Console",
        "browser": "Discord Embedded",
        "device": "PlayStation 5",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (PlayStation 5 3.11) AppleWebKit/605.1.15 (KHTML, like Gecko)",
        "browser_version": "",
        "os_version": "",
        "referrer": "",
        "referring_domain": "",
    },
    "xbox": {
        "os": "Console",
        "browser": "Discord Embedded",
        "device": "Xbox Series X",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox Series X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
        "browser_version": "",
        "os_version": "",
        "referrer": "",
        "referring_domain": "",
    },
    "playstation": {
        "os": "Console",
        "browser": "Discord Embedded",
        "device": "PlayStation 5",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (PlayStation 5 3.11) AppleWebKit/605.1.15 (KHTML, like Gecko)",
        "browser_version": "",
        "os_version": "",
        "referrer": "",
        "referring_domain": "",
    },
    "vr": {
        "os": "Console",
        "browser": "Discord VR",
        "device": "VR-Headset",
        "system_locale": "en-US",
        "browser_user_agent": "DiscordVR/12.45",
        "browser_version": "23.7.91",
        "os_version": "10.0.45",
        "referrer": "",
        "referring_domain": "",
    },
}

PLATFORM_LABELS = {
    "desktop": "Desktop (Windows)",
    "web": "Web (Chrome)",
    "mobile": "Mobile (Phone)",
    "ios": "Mobile (iOS)",
    "android": "Mobile (Android)",
    "console": "Console (PlayStation / Xbox)",
    "xbox": "Console (Xbox Series X)",
    "playstation": "Console (PlayStation 5)",
    "vr": "VR (VR Headset)"
}

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
    
    version_text = "Streamy v1.2.0 by Beatsbyluca"
    print(version_text.center(terminal_width))
    print()

def log(msg: str, status: str = "info", tag: str = None):
    timestamp = f"{Fore.LIGHTBLACK_EX}[{time.strftime('%H:%M:%S')}]{Fore.RESET}"
    if status == "info":
        prefix = f"{Fore.BLUE}[INFO]{Fore.RESET}"
    elif status == "success":
        prefix = f"{Fore.GREEN}[SUCCESS]{Fore.RESET}"
    elif status == "error":
        prefix = f"{Fore.RED}[ERROR]{Fore.RESET}"
    elif status == "wait":
        prefix = f"{Fore.YELLOW}[WAIT]{Fore.RESET}"
    elif status == "spoofer":
        prefix = f"{Fore.MAGENTA}[SPOOFER]{Fore.RESET}"
    elif status == "session":
        prefix = f"{Fore.CYAN}[SESSION]{Fore.RESET}"
    else:
        prefix = f"{Fore.BLUE}[INFO]{Fore.RESET}"
    
    if tag:
        tag_str = f"{Fore.LIGHTCYAN_EX}[{tag.upper()}]{Fore.RESET} "
    else:
        tag_str = ""

    print(f"{timestamp} {prefix} {tag_str}{msg}", flush=True)

def mask_token(token: str) -> str:
    if not token or len(token) < 15:
        return "***"
    return f"{token[:8]}...{token[-5:]}"

def load_or_create_config() -> dict:
    default_config = {
        "token": "",
        "stream_title": "₉⁹₉",
        "twitch_url": "",
        "status": "dnd",
        "image": "",
        "auto_reconnect": True,
        "active_platforms": DEFAULT_PLATFORMS
    }

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return default_config

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            updated = False
            for k, v in default_config.items():
                if k not in cfg:
                    cfg[k] = v
                    updated = True
            if updated:
                save_config(cfg)
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
    if "active_platforms" not in config:
        config["active_platforms"] = DEFAULT_PLATFORMS
    save_config(config)
    return config

class PlatformSession:
    def __init__(self, platform_name: str, properties: dict, keeper):
        self.platform_name = platform_name
        self.properties = properties
        self.keeper = keeper
        self.ws = None
        self.send_lock = threading.Lock()
        self.heartbeat_interval = None
        self.heartbeat_thread = None
        self.stop_event = threading.Event()
        self.last_sequence = None
        self.heartbeat_ack_received = True
        self.missed_acks = 0
        self.is_connected = False
        self.session_id = None
        self.thread = None

    def send_json(self, payload: dict) -> bool:
        with self.send_lock:
            if not self.ws:
                return False
            try:
                self.ws.send(json.dumps(payload))
                return True
            except Exception:
                return False

    def build_identify_payload(self) -> dict:
        presence = self.keeper.build_presence_payload()["d"]
        return {
            "op": 2,
            "d": {
                "token": self.keeper.token,
                "capabilities": 30717,
                "properties": self.properties,
                "presence": presence,
                "compress": False
            }
        }

    def heartbeat_worker(self):
        jitter = random.uniform(0.1, 0.7)
        time.sleep(self.heartbeat_interval * jitter)

        while not self.stop_event.is_set() and not self.keeper.stop_event.is_set():
            if not self.heartbeat_ack_received:
                self.missed_acks += 1
                if self.missed_acks >= 2:
                    log("Connection lost (missed ACKs). Reconnecting...", "wait", tag=self.platform_name)
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

    def run_loop(self):
        reconnect_delay = 5

        while not self.keeper.stop_event.is_set():
            self.stop_event.clear()
            self.last_sequence = None
            self.heartbeat_ack_received = True
            self.missed_acks = 0
            self.is_connected = False

            try:
                self.ws = websocket.create_connection(
                    GATEWAY_URL,
                    timeout=25,
                    enable_multithread=True
                )
                self.ws.settimeout(None)
            except Exception as e:
                log(f"Connection failed: {e}", "wait", tag=self.platform_name)
                if not self.keeper.config.get("auto_reconnect", True):
                    break
                time.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay + 5, 60)
                continue

            try:
                while not self.stop_event.is_set() and not self.keeper.stop_event.is_set():
                    try:
                        opcode, raw_bytes = self.ws.recv_data()
                    except (websocket.WebSocketTimeoutException, TimeoutError):
                        continue

                    if opcode == websocket.ABNF.OPCODE_CLOSE:
                        close_code = int.from_bytes(raw_bytes[:2], "big") if len(raw_bytes) >= 2 else None
                        reason = raw_bytes[2:].decode("utf-8", errors="ignore") if len(raw_bytes) > 2 else ""

                        if close_code == 4004:
                            log(f"Auth failed (Invalid token): {reason}", "error", tag=self.platform_name)
                            self.keeper.fatal_error = True
                            return
                        elif close_code == 4008:
                            log("Gateway rate limit reached. Backing off...", "wait", tag=self.platform_name)
                            time.sleep(6)
                        else:
                            log(f"Connection closed ({close_code}): {reason}", "wait", tag=self.platform_name)
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

                        self.send_json(self.build_identify_payload())

                    elif op == 11:
                        self.heartbeat_ack_received = True

                    elif op == 1:
                        self.send_json({"op": 1, "d": self.last_sequence})

                    elif op == 7:
                        log("Discord requested reconnect (OP 7).", "wait", tag=self.platform_name)
                        break

                    elif op == 9:
                        time.sleep(2)
                        break

                    elif op == 0:
                        if event_type == "READY":
                            self.is_connected = True
                            self.session_id = payload.get("session_id")
                            user = payload.get("user", {})
                            self.keeper.on_platform_ready(self.platform_name, user, self.session_id)
                            reconnect_delay = 5

                        elif event_type == "RESUMED":
                            self.is_connected = True
                            log("Session resumed.", "success", tag=self.platform_name)

                        elif event_type == "SESSIONS_REPLACE":
                            sessions = payload if isinstance(payload, list) else []
                            self.keeper.on_sessions_replace(self.platform_name, sessions)

            except (websocket.WebSocketConnectionClosedException, ConnectionResetError, BrokenPipeError):
                pass
            except Exception as e:
                log(f"Socket error: {e}", "wait", tag=self.platform_name)
            finally:
                self.stop_event.set()
                self.is_connected = False
                if self.ws:
                    try:
                        self.ws.close()
                    except Exception:
                        pass

            if not self.keeper.config.get("auto_reconnect", True) or self.keeper.fatal_error:
                break

            time.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay + 5, 60)

    def start(self):
        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass


class DiscordStreamKeeper:
    def __init__(self, config: dict):
        self.config = config
        self.token = config.get("token", "").strip().strip('"').strip("'")
        self.stream_title = config.get("stream_title", "Streaming")
        self.twitch_url = config.get("twitch_url", "https://www.twitch.tv/beatsbylxca")
        self.status = config.get("status", "dnd")
        self.details = config.get("details", "")
        self.image = config.get("image", "")
        
        self.active_platform_keys = config.get("active_platforms", DEFAULT_PLATFORMS)
        if not self.active_platform_keys:
            self.active_platform_keys = DEFAULT_PLATFORMS

        self.sessions = {}
        self.stop_event = threading.Event()
        self.start_time = None
        self.user_info = {}
        self.fatal_error = False
        self.last_sessions_summary = ""
        self.lock = threading.Lock()

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

    def on_platform_ready(self, platform_name: str, user: dict, session_id: str):
        with self.lock:
            if not self.start_time:
                self.start_time = time.time()
            if not self.user_info and user:
                self.user_info = user
                username = user.get("username", "Unknown")
                discrim = user.get("discriminator", "0")
                user_tag = f"{username}#{discrim}" if discrim != "0" else f"@{username}"
                user_id = user.get("id", "Unknown")
                log(f"Authenticated as {Fore.LIGHTMAGENTA_EX}{user_tag}{Fore.RESET} (ID: {user_id})", "success")
                log(f"Streaming: {Fore.CYAN}{self.stream_title}{Fore.RESET} | Twitch: {self.twitch_url}", "info")
                log(f"Status: {Fore.GREEN}{self.status.upper()}{Fore.RESET} | 24/7 Multi-Platform Active!", "success")

            label = PLATFORM_LABELS.get(platform_name, platform_name)
            sid_preview = f"Session: {session_id[:8]}..." if session_id else ""
            log(f"Connected as {label} {Fore.LIGHTBLACK_EX}{sid_preview}{Fore.RESET}", "spoofer", tag=platform_name)

    def on_sessions_replace(self, reporter_platform: str, sessions: list):
        with self.lock:
            active_clients = []
            for s in sessions:
                c_info = s.get("client_info", {})
                client = c_info.get("client", "unknown")
                os_name = c_info.get("os", "")
                label = f"{client.capitalize()} ({os_name.capitalize()})" if os_name else client.capitalize()
                active_clients.append(label)

            unique_clients = sorted(list(set(active_clients)))
            summary = ", ".join(unique_clients)

            if summary and summary != self.last_sessions_summary:
                self.last_sessions_summary = summary
                connected_count = sum(1 for s in self.sessions.values() if s.is_connected)
                total_count = len(self.active_platform_keys)
                log(f"Active Discord Sessions ({connected_count}/{total_count} connected): {Fore.LIGHTGREEN_EX}{summary}{Fore.RESET}", "session")

    def run_forever(self):
        print_header()
        log("Initializing Streamy Multi-Platform Spoofer...", "info")
        log(f"Token: {mask_token(self.token)}", "info")
        log("Configuration loaded successfully.", "success")
        print()

        for key in self.active_platform_keys:
            props = PLATFORM_PROPERTIES.get(key)
            if not props:
                continue
            session = PlatformSession(key, props, self)
            self.sessions[key] = session

        log(f"Starting {len(self.sessions)} platform gateway connections...", "info")
        log("Staggering initial connections by 5.5s (Discord rate limit protection)...", "wait")
        print()

        first = True
        for key, session in self.sessions.items():
            if self.stop_event.is_set() or self.fatal_error:
                break
            if not first:
                time.sleep(5.5)
            first = False
            label = PLATFORM_LABELS.get(key, key)
            log(f"Launching identity: {label}...", "wait", tag=key)
            session.start()

        ticker = 0
        while not self.stop_event.is_set():
            try:
                time.sleep(10)
                ticker += 1

                if self.fatal_error:
                    log("A fatal authentication error occurred. Please check your token.", "error")
                    answer = input("Enter new token? (y/n): ").strip().lower()
                    if answer in ("y", "yes", "j", "ja"):
                        self.config = prompt_user_for_token(self.config)
                        self.token = self.config.get("token", "").strip().strip('"').strip("'")
                        self.fatal_error = False
                        self.stop_all()
                        return self.run_forever()
                    else:
                        break

                if ticker % 6 == 0:
                    connected = sum(1 for s in self.sessions.values() if s.is_connected)
                    total = len(self.sessions)
                    log(f"Status Check: {connected}/{total} platforms online | Uptime: {self.get_uptime()} | Stream: {self.stream_title}", "info")

            except KeyboardInterrupt:
                print()
                log("Shutdown signal received (Ctrl + C)...", "wait")
                break

        self.stop_all()
        log("Streamy stopped cleanly. Goodbye!", "info")

    def stop_all(self):
        self.stop_event.set()
        for s in self.sessions.values():
            s.stop()


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
