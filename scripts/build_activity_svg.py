#!/usr/bin/env python3
"""Gera um painel SVG público contendo SOMENTE métricas agregadas do GitHub.

Requer PROFILE_STATS_TOKEN de um usuário autorizado a consultar suas próprias
contribuições. Não grava respostas da API, repositórios, mensagens ou tokens.
"""
from __future__ import annotations

import json
import os
from datetime import date
from html import escape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "caiocezar-dev")
OUTPUT = Path("assets/activity.svg")
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def fetch_activity() -> dict:
    token = os.environ.get("PROFILE_STATS_TOKEN", "")
    if not token:
        raise SystemExit("PROFILE_STATS_TOKEN ausente: cartão existente preservado.")
    body = json.dumps({"query": QUERY, "variables": {"login": OWNER}}).encode()
    req = Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "arcis-github-profile",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except (HTTPError, URLError) as exc:
        raise SystemExit("Falha ao consultar a API GitHub; cartão preservado.") from exc
    if payload.get("errors") or not payload.get("data", {}).get("user"):
        raise SystemExit("GraphQL não retornou a coleção solicitada; cartão preservado.")
    return payload["data"]["user"]["contributionsCollection"]


def rect(x: int, y: int, w: int, h: int, color: str, radius: int = 0) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
        f'rx="{radius}" fill="{color}"/>'
    )


def text(x: int, y: int, value: object, size: int, color: str, bold: bool = False) -> str:
    weight = ' font-weight="700"' if bold else ""
    return (
        f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" '
        f'font-size="{size}" fill="{color}"{weight}>{escape(str(value))}</text>'
    )


def render(data: dict) -> str:
    calendar = data["contributionCalendar"]
    weeks = calendar["weeks"]
    if not weeks or not any(week["contributionDays"] for week in weeks):
        raise ValueError("Calendário vazio: cartão anterior preservado.")

    stats = [
        ("COMMITS / 12 MESES", data["totalCommitContributions"]),
        ("CONTRIBUIÇÕES", calendar["totalContributions"]),
        ("PULL REQUESTS", data["totalPullRequestContributions"]),
        ("ISSUES", data["totalIssueContributions"]),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="345" '
        'viewBox="0 0 960 345" role="img" aria-labelledby="title desc">',
        f'<title id="title">Atividade do GitHub de {escape(OWNER)}</title>',
        '<desc id="desc">Estatísticas agregadas dos últimos doze meses. '
        'Não revela nomes ou conteúdos de repositórios privados.</desc>',
        rect(0, 0, 960, 345, "#071B13", 18),
        '<rect x="1" y="1" width="958" height="343" rx="17" '
        'fill="none" stroke="#315743" stroke-width="2"/>',
        text(32, 43, "ATIVIDADE NO GITHUB", 17, "#95CDA9", True),
        text(760, 43, "ÚLTIMOS 12 MESES", 13, "#C0D8C8", True),
    ]

    for index, (label, value) in enumerate(stats):
        x = 32 + index * 228
        parts += [
            rect(x, 61, 212, 92, "#123425", 12),
            text(x + 16, 88, label, 12, "#A9CCB6", True),
            text(x + 16, 129, f"{int(value):,}".replace(",", "."), 31, "#F1F8F3", True),
        ]

    parts.append(text(32, 186, "CALENDÁRIO DE CONTRIBUIÇÕES", 13, "#A9CCB6", True))
    # Domingo = primeira linha, mesmo padrão adotado pelo calendário do GitHub.
    colors = ("#214333", "#366A4C", "#4B9D70", "#8EE1AD")
    month_labels = {1:"JAN",2:"FEV",3:"MAR",4:"ABR",5:"MAI",6:"JUN",
                    7:"JUL",8:"AGO",9:"SET",10:"OUT",11:"NOV",12:"DEZ"}
    last_month = None
    for wi, week in enumerate(weeks):
        x = 57 + wi * 15
        for day in week["contributionDays"]:
            d = date.fromisoformat(day["date"])
            count = int(day["contributionCount"])
            row = (d.weekday() + 1) % 7
            y = 209 + row * 16
            color = colors[0 if count == 0 else 1 if count <= 3 else 2 if count <= 8 else 3]
            parts.append(rect(x, y, 11, 11, color, 2))
            # Rótulo em cada início de mês, sem duplicar nas demais semanas.
            if d.month != last_month:
                if x < 883:
                    parts.append(text(x, 202, month_labels[d.month], 10, "#8EBFA2"))
                last_month = d.month
    parts += [
        text(32, 333, "Dados agregados. Repositórios privados permanecem confidenciais.", 12, "#A9CCB6"),
        "</svg>",
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    data = fetch_activity()
    svg = render(data)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print("Painel SVG gerado: somente métricas agregadas (sem detalhes privados).")


if __name__ == "__main__":
    main()
