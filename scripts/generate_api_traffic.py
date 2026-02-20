#!/usr/bin/env python
"""
Script para gerar tráfego na API e popular métricas.

Uso:
    python scripts/generate_api_traffic.py
    python scripts/generate_api_traffic.py --base-url http://localhost:8000 --requests 50

Requer: pip install requests
"""
import argparse
import random
import sys
import time

try:
    import requests
except ImportError:
    print("Instale requests: pip install requests")
    sys.exit(1)

# Endpoints públicos (AllowAny ou sem auth obrigatória)
PUBLIC_ENDPOINTS = [
    "/api/v1/health/",
    "/api/v1/",
    "/api/v1/server/status/",
    "/api/v1/server/players-online/",
    "/api/v1/server/top-pvp/",
    "/api/v1/server/top-pk/",
    "/api/v1/server/top-clan/",
    "/api/v1/server/top-rich/",
    "/api/v1/server/top-online/",
    "/api/v1/server/top-level/",
    "/api/v1/server/olympiad-ranking/",
    "/api/v1/server/olympiad-heroes/",
    "/api/v1/server/olympiad-current-heroes/",
    "/api/v1/server/grandboss-status/",
    "/api/v1/server/siege/",
    "/api/v1/server/boss-jewel-locations/",
    "/api/v1/server/raidboss-status/",
    "/api/v1/auction/items/",
    "/api/v1/vapid-public-key/",
]


def main():
    parser = argparse.ArgumentParser(description="Gera tráfego na API para popular métricas")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:6085",
        help="URL base do servidor (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--requests",
        "-n",
        type=int,
        default=30,
        help="Número de requisições (default: 30)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Delay entre requisições em segundos (default: 0.1)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Não exibe o resultado de cada requisição",
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    total = args.requests
    delay = args.delay

    print(f"Gerando {total} requisições para {base}")
    print(f"Endpoints: {len(PUBLIC_ENDPOINTS)} públicos\n")

    ok = 0
    err = 0

    for i in range(total):
        url = base + random.choice(PUBLIC_ENDPOINTS)
        try:
            r = requests.get(url, timeout=10)
            status = "✓" if r.ok else "✗"
            ok += 1 if r.ok else 0
            err += 0 if r.ok else 1
            if not args.quiet:
                print(f"  [{i+1}/{total}] {status} {r.status_code} {url}")
        except requests.RequestException as e:
            err += 1
            if not args.quiet:
                print(f"  [{i+1}/{total}] ✗ ERRO {url}: {e}")

        if i < total - 1 and delay > 0:
            time.sleep(delay)

    print(f"\nConcluído: {ok} OK, {err} erros")
    print("As métricas devem aparecer na aba Métricas do PWA (usuário staff).")


if __name__ == "__main__":
    main()
