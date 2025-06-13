#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import argparse
import hashlib
import re
import socket
import whois
from urllib.parse import urljoin, urlparse
from pyfiglet import Figlet
from termcolor import colored

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# ─── Banner ─────────────────────────────────────────────
def banner():
    f = Figlet(font='slant')
    print(colored(f.renderText('site-find'), 'cyan'))
    print(colored('Advanced Website Scanner by You', 'yellow', attrs=['bold']))

# ─── Fetch Headers ──────────────────────────────────────
def fetch_headers(url):
    try:
        response = requests.head(url, timeout=15, headers=HEADERS, allow_redirects=True)
        print(colored("\n[+] HTTP Headers:", 'green', attrs=['bold']))
        for k, v in response.headers.items():
            print(colored(f"    {k}: ", 'cyan') + colored(str(v), 'white'))
        return response.headers
    except Exception as e:
        print(colored(f"[!] Header fetch error: {e}", 'red'))
        return {}

# ─── Fetch and Parse ────────────────────────────────────
def fetch_page(url):
    try:
        response = requests.get(url, timeout=30, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        print(colored(f"\n[+] Status Code: {response.status_code}", 'green', attrs=['bold']))
        print(colored(f"[+] Page Size: {len(response.content)} bytes", 'green', attrs=['bold']))
        print(colored(f"[+] Title: {soup.title.string.strip() if soup.title else 'N/A'}", 'yellow', attrs=['bold']))
        return response, soup
    except Exception as e:
        print(colored(f"[!] Fetch error: {e}", 'red'))
        return None, None

# ─── Extract Internal Links ─────────────────────────────
def extract_links(base_url, soup):
    print(colored("\n[+] Internal Links:", 'green', attrs=['bold']))
    base_domain = urlparse(base_url).netloc
    links = set()
    for tag in soup.find_all('a', href=True):
        full_url = urljoin(base_url, tag['href'])
        if urlparse(full_url).netloc == base_domain:
            links.add(full_url)
    if links:
        for link in links:
            print(colored(f"    - {link}", 'cyan'))
    else:
        print(colored("    No internal links found.", 'red'))

# ─── Extract Emails & Phone Numbers ─────────────────────
def extract_contacts(content):
    print(colored("\n[+] Contacts Found:", 'green', attrs=['bold']))
    emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", content))
    phones = set(re.findall(r"\+?\d[\d\s\-\(\)]{7,}\d", content))

    if emails:
        print(colored("    Emails:", 'cyan'))
        for email in emails:
            print(f"     - {email}")
    else:
        print(colored("    No emails found.", 'red'))

    if phones:
        print(colored("    Phone Numbers:", 'cyan'))
        for phone in phones:
            print(f"     - {phone}")
    else:
        print(colored("    No phone numbers found.", 'red'))

# ─── Tech Stack Fingerprint ─────────────────────────────
def fingerprint(headers, html):
    print(colored("\n[+] Tech Stack:", 'green', attrs=['bold']))
    server = headers.get("Server", "N/A")
    powered = headers.get("X-Powered-By", "N/A")
    generator = re.search(r'generator" content="([^"]+)"', html, re.I)
    print(colored(f"    Server: ", 'cyan') + colored(server, 'white'))
    print(colored(f"    X-Powered-By: ", 'cyan') + colored(powered, 'white'))
    print(colored(f"    Generator: ", 'cyan') + colored(generator.group(1) if generator else "N/A", 'white'))

# ─── Favicon Hash ───────────────────────────────────────
def hash_favicon(soup, url):
    print(colored("\n[+] Favicon Hash:", 'green', attrs=['bold']))
    icon_tag = soup.find("link", rel=lambda x: x and 'icon' in x.lower())
    if icon_tag and icon_tag.get("href"):
        icon_url = urljoin(url, icon_tag["href"])
        try:
            icon = requests.get(icon_url, timeout=10)
            icon_hash = hashlib.md5(icon.content).hexdigest()
            print(colored(f"    MD5: {icon_hash}", 'cyan'))
        except:
            print(colored("    Failed to fetch favicon.", 'red'))
    else:
        print(colored("    No favicon found.", 'red'))

# ─── Save HTML ──────────────────────────────────────────
def save_html(domain, response):
    filename = f"{domain}.html"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(colored(f"[+] HTML saved to {filename}", 'green'))

# ─── Server Info and WHOIS ─────────────────────────────
def server_info(domain):
    print(colored("\n[+] Server Info:", 'green', attrs=['bold']))
    try:
        ip = socket.gethostbyname(domain)
        print(colored(f"    IP Address: ", 'cyan') + colored(ip, 'white'))
    except Exception as e:
        print(colored(f"    Failed to resolve IP: {e}", 'red'))

    try:
        w = whois.whois(domain)
        print(colored("\n[+] WHOIS Info:", 'green', attrs=['bold']))
        print(colored(f"    Registrar: ", 'cyan') + colored(str(w.registrar), 'white'))
        print(colored(f"    Creation Date: ", 'cyan') + colored(str(w.creation_date), 'white'))
        print(colored(f"    Expiration Date: ", 'cyan') + colored(str(w.expiration_date), 'white'))
        print(colored(f"    Name Servers: ", 'cyan') + colored(', '.join(w.name_servers or []), 'white'))
    except Exception as e:
        print(colored(f"    Failed to fetch WHOIS info: {e}", 'red'))

# ─── Main ───────────────────────────────────────────────
def main():
    banner()
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Target website (e.g., https://example.com)", required=True)
    args = parser.parse_args()

    domain = urlparse(args.url).netloc
    server_info(domain)

    headers = fetch_headers(args.url)
    response, soup = fetch_page(args.url)

    if response and soup:
        extract_links(args.url, soup)
        extract_contacts(response.text)
        fingerprint(headers, response.text)
        hash_favicon(soup, args.url)
        save_html(domain, response)

if __name__ == "__main__":
    main()
