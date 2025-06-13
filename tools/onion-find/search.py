#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import argparse
import os
import hashlib
import re
from urllib.parse import urljoin
from pyfiglet import Figlet
from termcolor import colored

# ─── Config ───────────────────────────────────────────
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# ─── Banner ───────────────────────────────────────────
def banner():
    f = Figlet(font='slant')
    print(colored(f.renderText('onion-find'), 'cyan'))
    print(colored('By ClayHacker Group', 'yellow', attrs=['bold']))
    print(colored('Instagram: @h4cker.in\n', 'magenta'))

# ─── Print colored key-value pairs ────────────────────
def print_colored_dict(d, title=""):
    print(colored(f"\n[+] {title}", 'green', attrs=['bold']))
    for k, v in d.items():
        print(colored(f"    {k}: ", 'cyan') + colored(str(v), 'white'))

# ─── Fetch HTTP Headers ───────────────────────────────
def fetch_headers(url):
    try:
        response = requests.head(url, proxies=proxies, timeout=30, headers=HEADERS)
        print_colored_dict(response.headers, "Headers")
        return response.headers
    except Exception as e:
        print(colored(f"[!] Header fetch error: {e}", 'red'))
        return {}

# ─── Fetch and Parse Page ─────────────────────────────
def fetch_page_info(url):
    try:
        response = requests.get(url, proxies=proxies, timeout=60, headers=HEADERS)
        print(colored(f"\n[+] Status Code: {response.status_code}", 'green', attrs=['bold']))
        print(colored(f"[+] Page Size: {len(response.content)} bytes", 'green', attrs=['bold']))
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string.strip() if soup.title else "N/A"
        print(colored(f"[+] Title: {title}", 'yellow', attrs=['bold']))
        return response, soup
    except Exception as e:
        print(colored(f"[!] Page fetch error: {e}", 'red'))
        return None, None

# ─── Extract internal links ───────────────────────────
def extract_links(url, soup):
    print(colored("\n[+] Extracting internal links...", 'green', attrs=['bold']))
    links = set()
    for a in soup.find_all('a', href=True):
        link = urljoin(url, a['href'])
        if ".onion" in link or link.startswith("/"):
            links.add(link)
    if links:
        for link in links:
            print(colored(f"    - {link}", 'cyan'))
    else:
        print(colored("    No internal links found.", 'red'))

# ─── Extract emails ───────────────────────────────────
def extract_emails(content):
    print(colored("\n[+] Searching for emails...", 'green', attrs=['bold']))
    emails = set(re.findall(r"[\\w.-]+@[\\w.-]+", content))
    if emails:
        for email in emails:
            print(colored(f"    - {email}", 'cyan'))
    else:
        print(colored("    No emails found.", 'red'))

# ─── Fingerprint tech stack ───────────────────────────
def fingerprint_tech(headers, html):
    print(colored("\n[+] Fingerprinting tech stack...", 'green', attrs=['bold']))
    server = headers.get("Server", "N/A")
    powered_by = headers.get("X-Powered-By", "N/A")
    generator = re.search(r'generator" content="([^"]+)"', html, re.I)
    print(colored(f"    Server: ", 'cyan') + colored(server, 'white'))
    print(colored(f"    X-Powered-By: ", 'cyan') + colored(powered_by, 'white'))
    print(colored(f"    Generator: ", 'cyan') + colored(generator.group(1) if generator else 'N/A', 'white'))

# ─── Save HTML content ────────────────────────────────
def save_content(domain, response):
    filename = f"{domain}.html"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(colored(f"\n[+] Saved page content to {filename}", 'green', attrs=['bold']))

# ─── Hash favicon ──────────────────────────────────────
def hash_favicon(soup, url):
    print(colored("\n[+] Hashing favicon...", 'green', attrs=['bold']))
    icon_link = soup.find("link", rel=lambda x: x and 'icon' in x.lower())
    if icon_link:
        icon_href = urljoin(url, icon_link['href'])
        try:
            icon = requests.get(icon_href, proxies=proxies, timeout=15)
            favicon_hash = hashlib.md5(icon.content).hexdigest()
            print(colored(f"    Favicon Hash (MD5): ", 'cyan') + colored(favicon_hash, 'white'))
        except:
            print(colored("    Failed to download favicon.", 'red'))
    else:
        print(colored("    No favicon found.", 'red'))

# ─── Main ─────────────────────────────────────────────
def main():
    banner()
    parser = argparse.ArgumentParser(description="Advanced .onion Site Investigator - onion-find")
    parser.add_argument("-u", "--url", help="Target .onion URL", required=True)
    args = parser.parse_args()

    if not args.url.endswith(".onion"):
        print(colored("[!] Must be a .onion URL.", 'red', attrs=['bold']))
        return

    domain = args.url.split("//")[-1].split(".onion")[0]

    headers = fetch_headers(args.url)
    response, soup = fetch_page_info(args.url)

    if response and soup:
        extract_links(args.url, soup)
        extract_emails(response.text)
        fingerprint_tech(headers, response.text)
        save_content(domain, response)
        hash_favicon(soup, args.url)

if __name__ == "__main__":
    main()
