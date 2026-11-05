# Ghost-Fuzz

> Web application fuzzer - directory brute-force, parameter fuzzing, and virtual host enumeration.

```
  GHOST-FUZZ  v1.0.0  |  Web Application Fuzzer
  By Gh0st-Bx1        |  github.com/Ghost-Bx1
```

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey?style=flat-square)
![Category](https://img.shields.io/badge/Category-Web%20Fuzzing-red?style=flat-square)

---

## Overview

Ghost-Fuzz covers the three core web fuzzing workflows: directory and file brute-force with smart 404 baseline detection, single-parameter fuzzing with built-in payloads for the most common injection classes, and virtual host enumeration via Host header manipulation.

| Module  | Description                                                        |
|---------|--------------------------------------------------------------------|
| `dir`   | Directory and file brute-force with intelligent 404 baseline       |
| `param` | Parameter fuzzing - LFI, SSTI, SSRF, XSS, SQLi, path traversal    |
| `vhost` | Virtual host enumeration via Host header manipulation              |

---

## Requirements

```
Python 3.7+
requests
```

```bash
pip install requests
```

---

## Installation

```bash
git clone https://github.com/Ghost-Bx1/ghost-fuzz
cd ghost-fuzz
pip install requests
```

---

## Usage

### Directory brute-force

```bash
# Default wordlist (common)
python ghost-fuzz.py dir -u https://target.com

# WordPress wordlist with extensions
python ghost-fuzz.py dir -u https://target.com -w wp -e php,html,bak

# Custom wordlist
python ghost-fuzz.py dir -u https://target.com --wordlist /path/list.txt -e php

# Filter by status code
python ghost-fuzz.py dir -u https://target.com --filter-status 200,301,302

# Exclude specific response sizes
python ghost-fuzz.py dir -u https://target.com --filter-size 1024
```

### Parameter fuzzing

```bash
# LFI
python ghost-fuzz.py param -u "https://target.com/page.php?file=FUZZ" -t lfi

# SSTI
python ghost-fuzz.py param -u "https://target.com/render?template=FUZZ" -t ssti

# SSRF
python ghost-fuzz.py param -u "https://target.com/fetch?url=FUZZ" -t ssrf

# SQLi
python ghost-fuzz.py param -u "https://target.com/user?id=FUZZ" -t sqli

# With session cookie
python ghost-fuzz.py param -u "https://target.com/view?file=FUZZ" -t lfi --cookie "session=abc123"
```

### Virtual host enumeration

```bash
# Default built-in wordlist
python ghost-fuzz.py vhost -u https://target.com -d target.com

# Custom wordlist
python ghost-fuzz.py vhost -u https://target.com -d target.com --wordlist /path/subdomains.txt
```

### Common options

```bash
# Proxy (Burp Suite)
python ghost-fuzz.py dir -u https://target.com --proxy http://127.0.0.1:8080

# JSON output
python ghost-fuzz.py dir -u https://target.com --output result.json

# Custom thread count and timeout
python ghost-fuzz.py dir -u https://target.com --threads 20 --timeout 5
```

---

## Built-in wordlists

| Name      | Contents                                              |
|-----------|-------------------------------------------------------|
| `common`  | 70+ generic paths (admin, login, api, uploads...)     |
| `wp`      | WordPress paths (wp-admin, xmlrpc, plugins, themes)   |
| `api`     | REST/GraphQL endpoints (v1, v2, swagger, graphql)     |
| `php`     | PHP files (config, info, shell, debug)                |
| `devops`  | Infrastructure panels (jenkins, gitlab, grafana, k8s) |

## Built-in payloads

| Type            | Count | Notes                                               |
|-----------------|-------|-----------------------------------------------------|
| `lfi`           | 35+   | Includes php://filter, zip://, data:// wrappers     |
| `ssti`          | 25+   | Jinja2, Twig, Freemarker, Smarty, Pebble            |
| `ssrf`          | 30+   | AWS IMDSv1/v2, GCP, Azure, localhost bypass         |
| `xss`           | 20+   | script, svg, img, event handlers                    |
| `sqli`          | 30+   | Error-based, time-based blind, UNION                |
| `path_traversal`| 15+   | Encoded path traversal variants                     |

---

## Reference

### `dir` flags

| Flag              | Description                                       |
|-------------------|---------------------------------------------------|
| `-u URL`          | Target URL                                        |
| `-w WORDLIST`     | Built-in wordlist: common, wp, api, php, devops   |
| `--wordlist FILE` | Custom wordlist file (overrides -w)               |
| `-e EXT`          | Extensions to append (e.g. php,html,bak)          |
| `--filter-status` | Keep only these status codes (e.g. 200,301)       |
| `--filter-size N` | Ignore responses of exactly N bytes               |
| `--threads N`     | Concurrent threads (default: 10)                  |
| `--timeout N`     | Per-request timeout in seconds (default: 5)       |
| `--proxy URL`     | HTTP/HTTPS proxy                                  |
| `--cookie`        | Session cookie (e.g. session=abc123)              |
| `--header`        | Custom header (e.g. "X-Api-Key: token")           |
| `--output FILE`   | Save results to JSON                              |
| `--verbose`       | Show all results including 404s                   |

### `param` flags

| Flag              | Description                                       |
|-------------------|---------------------------------------------------|
| `-u URL`          | URL with FUZZ marker                              |
| `-t TYPE`         | Payload type: lfi, ssti, ssrf, xss, sqli, path_traversal |
| `--method`        | HTTP method: GET or POST (default: GET)           |
| `--data DATA`     | POST body with FUZZ marker                        |
| `--threads N`     | Concurrent threads (default: 5)                   |
| `--timeout N`     | Per-request timeout (default: 5)                  |
| `--proxy URL`     | HTTP/HTTPS proxy                                  |
| `--cookie`        | Session cookie                                    |
| `--output FILE`   | Save results to JSON                              |

### `vhost` flags

| Flag              | Description                                       |
|-------------------|---------------------------------------------------|
| `-u URL`          | Target URL                                        |
| `-d DOMAIN`       | Base domain (e.g. target.com)                     |
| `--wordlist FILE` | Custom subdomain wordlist                         |
| `--threads N`     | Concurrent threads (default: 10)                  |
| `--timeout N`     | Per-request timeout (default: 5)                  |
| `--proxy URL`     | HTTP/HTTPS proxy                                  |
| `--output FILE`   | Save results to JSON                              |

---

## Ghost Toolkit

| Tool | Description |
|------|-------------|
| [ghost-ad](https://github.com/Ghost-Bx1/ghost-ad) | Active Directory - LDAP, Kerberoasting, AS-REP Roasting, BloodHound-lite |
| [ghost-cloud](https://github.com/Ghost-Bx1/ghost-cloud) | Cloud Security - AWS, Azure and GCP misconfiguration scanner |
| [ghost-fuzz](https://github.com/Ghost-Bx1/ghost-fuzz) | Web Fuzzing - directory brute-force, parameter fuzzing, vhost enumeration |
| [ghost-osint](https://github.com/Ghost-Bx1/ghost-osint) | OSINT - domain, email and IP intelligence from public sources |
| [ghost-privesc](https://github.com/Ghost-Bx1/ghost-privesc) | Privilege Escalation - Linux privesc checker, 17 vectors, GTFOBins |
| [ghost-recon](https://github.com/Ghost-Bx1/ghost-recon) | Reconnaissance - DNS, SSL, WAF, subdomain enumeration, email security |
| [ghost-report](https://github.com/Ghost-Bx1/ghost-report) | Reporting - pentest report generator from any ghost-* JSON output |
| [ghost-scan](https://github.com/Ghost-Bx1/ghost-scan) | Port Scanner - async TCP/UDP scanner with banner grabbing and CVE correlation |
| [ghost-shell](https://github.com/Ghost-Bx1/ghost-shell) | Payload Generation - reverse shell and web shell generator, 25+ languages |
| [ghost-spray](https://github.com/Ghost-Bx1/ghost-spray) | Credential Attacks - password spraying, stuffing, default credential testing |
| [ghost-wifi](https://github.com/Ghost-Bx1/ghost-wifi) | WiFi Attacks - monitor mode, deauth, WPA/WPA2 capture, PMKID, WPS, Evil Twin |

---

## Disclaimer

For use in authorized environments only. Penetration testing, CTF competitions, and offensive security research with explicit permission from the environment owner. The author is not responsible for misuse.

---

**By [Gh0st-Bx1](https://github.com/Ghost-Bx1)**
