# Ghost-Fuzz

> By Gh0st-Bx1 | [github.com/Ghost-Bx1](https://github.com/Ghost-Bx1)

Web application fuzzer completo para pentest e bug bounty. Realiza brute-force de diretorios, fuzzing de parametros (LFI/SSTI/SSRF/XSS/SQLi) e virtual host enumeration.

---

## Funcionalidades

| Modulo | Descricao |
|---|---|
| `dir` | Brute-force de diretorios e arquivos com baseline 404 inteligente |
| `param` | Fuzzing de parametro unico com payloads LFI/SSTI/SSRF/XSS/SQLi/Path Traversal |
| `vhost` | Enumeracao de virtual hosts via manipulacao do header Host |

---

## Wordlists e Payloads embutidos

### Wordlists (`dir`)
- `common` - 70+ paths genericos (admin, login, api, uploads, backup...)
- `wp` - WordPress (wp-admin, xmlrpc, plugins, themes...)
- `api` - Endpoints REST/GraphQL (v1, v2, swagger, graphql...)
- `php` - Arquivos PHP (config, info, shell, debug...)
- `devops` - Ferramentas de infraestrutura (jenkins, gitlab, grafana, k8s...)

### Payloads (`param`)
- `lfi` - 35+ payloads LFI incluindo wrappers php://filter, zip://, data://
- `ssti` - 25+ payloads para Jinja2, Twig, Freemarker, Smarty, Pebble
- `ssrf` - 30+ endpoints cloud (AWS IMDS v1/v2, GCP, Azure, localhost bypass)
- `xss` - 20+ payloads XSS refletido (script, svg, img, event handlers)
- `sqli` - 30+ payloads SQLi (error-based, time-based blind, UNION)
- `path_traversal` - 15+ variantes de encoding de path traversal

---

## Instalacao

```bash
pip install requests
```

Python 3.7+ com apenas `requests` como dependencia.

---

## Uso

```bash
# Brute-force de diretorios (wordlist common)
python ghost-fuzz.py dir -u https://alvo.com

# Wordlist especifica + extensoes
python ghost-fuzz.py dir -u https://alvo.com -w wp -e php,html,bak

# Wordlist customizada
python ghost-fuzz.py dir -u https://alvo.com --wordlist /path/lista.txt -e php

# Filtrar por status code
python ghost-fuzz.py dir -u https://alvo.com --filter-status 200,301,302

# Filtrar fora de tamanhos de resposta especificos
python ghost-fuzz.py dir -u https://alvo.com --filter-size 1024

# Fuzzing de parametro - LFI
python ghost-fuzz.py param -u "https://alvo.com/page.php?file=FUZZ" -t lfi

# Fuzzing de parametro - SSTI
python ghost-fuzz.py param -u "https://alvo.com/render?template=FUZZ" -t ssti

# Fuzzing de parametro - SSRF
python ghost-fuzz.py param -u "https://alvo.com/fetch?url=FUZZ" -t ssrf

# Fuzzing de parametro - SQLi
python ghost-fuzz.py param -u "https://alvo.com/user?id=FUZZ" -t sqli

# Fuzzing com cookie de sessao
python ghost-fuzz.py param -u "https://alvo.com/view?file=FUZZ" -t lfi --cookie "session=abc123"

# Enumeracao de virtual hosts
python ghost-fuzz.py vhost -u https://alvo.com -d alvo.com

# Vhost com wordlist customizada
python ghost-fuzz.py vhost -u https://alvo.com -d alvo.com --wordlist /path/subdomains.txt

# Com proxy (Burp Suite)
python ghost-fuzz.py dir -u https://alvo.com --proxy http://127.0.0.1:8080

# Output JSON
python ghost-fuzz.py dir -u https://alvo.com --output resultado.json

# Threads e timeout customizados
python ghost-fuzz.py dir -u https://alvo.com --threads 20 --timeout 5
```

---

## Saida exemplo

```
   _____ _               _     ______
  / ____| |             | |   |  ____|
 | |  __| |__   ___  ___| |_  | |__ _   _ ________
 ...

  Ghost-Fuzz v1.0.0  |  Web Application Fuzzer

  [=] DIRECTORY BRUTE-FORCE
  [+] 200 [1234B] /admin
  [+] 301 [0B]    /backup -> /backup/
  [+] 200 [567B]  /api/v1
  [!] 403 [89B]   /wp-admin
  [-] 404         /nonexistent (filtrado)

  [=] RESUMO
  Encontrados: 4  |  Filtrados: 156  |  Erros: 0
```

---

## Opcoes completas

### `dir` - Brute-force de diretorios

```
opcoes:
  -u URL                URL alvo (https://alvo.com)
  -w WORDLIST           Wordlist: common, wp, api, php, devops (padrao: common)
  --wordlist FILE       Wordlist customizada (substitui -w)
  -e EXT                Extensoes a testar (ex: php,html,bak)
  --filter-status LISTA Status codes a manter (ex: 200,301,302,403)
  --filter-size N       Ignorar respostas com exatamente N bytes
  --threads N           Threads concorrentes (padrao: 10)
  --timeout N           Timeout por requisicao em segundos (padrao: 5)
  --proxy URL           Proxy HTTP/HTTPS
  --cookie COOKIE       Cookie de sessao (ex: session=abc123)
  --header HEADER       Header customizado (ex: "X-Api-Key: token")
  --output FILE         Salvar resultados em JSON
  --verbose             Mostrar todos os resultados (incluindo 404)
```

### `param` - Fuzzing de parametros

```
opcoes:
  -u URL                URL com marcador FUZZ (ex: https://alvo.com?file=FUZZ)
  -t TIPO               Tipo de payload: lfi, ssti, ssrf, xss, sqli, path_traversal
  --method METODO       HTTP method: GET ou POST (padrao: GET)
  --data DATA           Corpo POST com marcador FUZZ (ex: "search=FUZZ")
  --threads N           Threads concorrentes (padrao: 5)
  --timeout N           Timeout por requisicao (padrao: 5)
  --proxy URL           Proxy HTTP/HTTPS
  --cookie COOKIE       Cookie de sessao
  --header HEADER       Header customizado
  --output FILE         Salvar resultados em JSON
```

### `vhost` - Virtual host brute-force

```
opcoes:
  -u URL                URL alvo (https://alvo.com)
  -d DOMINIO            Dominio base (ex: alvo.com)
  --wordlist FILE       Wordlist de subdomains customizada
  --threads N           Threads concorrentes (padrao: 10)
  --timeout N           Timeout por requisicao (padrao: 5)
  --proxy URL           Proxy HTTP/HTTPS
  --output FILE         Salvar resultados em JSON
```

---

## Aviso Legal

Uso exclusivo para pesquisa de seguranca, pentest autorizado e fins educacionais. O uso nao autorizado contra sistemas de terceiros e ilegal. Os autores nao se responsabilizam pelo uso indevido.
