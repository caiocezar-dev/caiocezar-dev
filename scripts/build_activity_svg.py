#!/usr/bin/env python3
"""Painel de contribuições do titular via API GraphQL oficial do GitHub.

Nunca consulta nem publica repositórios, mensagens, arquivos ou hashes privados.
O token (read:user) é usado apenas na chamada HTTPS, via GitHub Actions secret.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OWNER = "caiocezar-dev"
OUTPUT = Path("assets/activity.svg")
API_URL = "https://api.github.com/graphql"

# 'viewer', não 'user(login:...)': a API autentica a autoria das contribuições.
QUERY = """
query {
  viewer {
    login
    contributionsCollection {
      startedAt
      endedAt
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoriesWithContributedCommits
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

COLORS = ("#123627", "#22583D", "#348758", "#57B77A", "#92E7A9")
MONTHS = ("JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL",
          "AGO", "SET", "OUT", "NOV", "DEZ")
DAYS = ("D", "S", "T", "Q", "Q", "S", "S")


def fetch_activity(token: str | None = None) -> dict:
    token = token or os.environ.get("PROFILE_STATS_TOKEN", "")
    if not token:
        raise ValueError("PROFILE_STATS_TOKEN ausente; SVG existente preservado.")
    body = json.dumps({"query": QUERY}).encode("utf-8")
    request = Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "arcis-profile-activity",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=25) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(
            "Consulta à API GraphQL falhou; SVG existente preservado."
        ) from exc
    if payload.get("errors") or not isinstance(payload.get("data"), dict):
        raise ValueError("Resposta GraphQL inválida; SVG existente preservado.")
    viewer = payload["data"].get("viewer")
    if not isinstance(viewer, dict) or viewer.get("login", "").casefold() != OWNER.casefold():
        raise ValueError("Token não pertence ao titular caiocezar-dev.")
    return validate_activity(viewer.get("contributionsCollection"))


def validate_activity(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Coleção de contribuições ausente.")
    fields = (
        "totalCommitContributions", "totalIssueContributions",
        "totalPullRequestContributions", "totalPullRequestReviewContributions",
        "totalRepositoriesWithContributedCommits",
    )
    for name in fields:
        if type(data.get(name)) is not int or data[name] < 0:
            raise ValueError(f"Campo inválido: {name}")
    calendar = data.get("contributionCalendar")
    if not isinstance(calendar, dict):
        raise ValueError("Calendário ausente.")
    if type(calendar.get("totalContributions")) is not int or calendar["totalContributions"] < 0:
        raise ValueError("Total de contribuições inválido.")
    weeks = calendar.get("weeks")
    if not isinstance(weeks, list) or not 48 <= len(weeks) <= 55:
        raise ValueError("Número de semanas inesperado; não publicar dados parciais.")
    days_seen = set()
    previous = None
    days = []
    for week in weeks:
        if not isinstance(week, dict) or not isinstance(week.get("contributionDays"), list):
            raise ValueError("Semana inválida.")
        for entry in week["contributionDays"]:
            if not isinstance(entry, dict):
                raise ValueError("Dia inválido.")
            day = date.fromisoformat(entry["date"])
            count = entry.get("contributionCount")
            if type(count) is not int or count < 0 or day in days_seen:
                raise ValueError("Contagem ou data inválida.")
            if previous is not None and day <= previous:
                raise ValueError("Datas fora de ordem.")
            days_seen.add(day)
            previous = day
            days.append((day, count))
    if not 330 <= len(days) <= 375:
        raise ValueError("Calendário incompleto; SVG existente preservado.")
    # Retorna os mesmos dados recebidos, mas somente após validação integral.
    return data


def _text(x: float, y: float, value: object, size=14, color="#E9F4ED",
          weight=400, anchor="start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'
    )


def _rect(x: float, y: float, width: float, height: float,
          color: str, radius: float = 0) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" '
        f'height="{height:.1f}" rx="{radius:.1f}" fill="{color}"/>'
    )


def _number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def render(data: dict, generated_at: datetime | None = None) -> str:
    validate_activity(data)
    generated_at = generated_at or datetime.now(timezone.utc)
    if generated_at.tzinfo is None:
        raise ValueError("Timestamp deve conter fuso horário.")
    updated = generated_at.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    calendar = data["contributionCalendar"]
    weeks = calendar["weeks"]
    records = [
        (date.fromisoformat(day["date"]), day["contributionCount"])
        for week in weeks for day in week["contributionDays"]
    ]
    active_days = sum(1 for _, count in records if count > 0)
    last_7 = sum(count for _, count in records[-7:])
    last_30 = sum(count for _, count in records[-30:])
    peak = max((count for _, count in records), default=0)
    month_totals = defaultdict(int)
    for day, count in records:
        month_totals[(day.year, day.month)] += count
    months = sorted(month_totals)

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="722" '
        'viewBox="0 0 1060 722" role="img" aria-labelledby="title desc">',
        '<title id="title">Atividade autenticada no GitHub de Caio Araújo</title>',
        '<desc id="desc">Contribuições elegíveis do GitHub nos últimos 12 meses, '
        'incluindo privadas autorizadas; gráfico diário e distribuição por mês. '
        'Nenhum repositório privado é identificado.</desc>',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#06170F"/>'
        '<stop offset="1" stop-color="#0B2820"/></linearGradient></defs>',
        _rect(0, 0, 1060, 722, "url(#bg)", 20),
        '<rect x="1" y="1" width="1058" height="720" rx="19" '
        'fill="none" stroke="#25543F" stroke-width="2"/>',
        _text(36, 42, "ARCIS / GITHUB ACTIVITY", 17, "#85D7AA", 700),
        _text(1023, 42, "12 MESES • DADOS OFICIAIS", 13, "#B4D6C1", 700, "end"),
        _text(36, 71, "Contribuições verificadas e atribuídas ao perfil", 16, "#C9E0D2"),
    ]

    main_stats = [
        ("CONTRIBUIÇÕES", calendar["totalContributions"]),
        ("COMMITS ELEGÍVEIS", data["totalCommitContributions"]),
        ("DIAS COM ATIVIDADE", active_days),
        ("PICO EM UM DIA", peak),
    ]
    for index, (label, value) in enumerate(main_stats):
        x = 36 + index * 253
        svg.extend([
            _rect(x, 93, 239, 104, "#103927", 13),
            _text(x + 17, 122, label, 12, "#ABD9BE", 700),
            _text(x + 17, 174, _number(value), 39, "#F3FFF6", 700),
        ])

    small_stats = [
        ("PULL REQUESTS", data["totalPullRequestContributions"]),
        ("ISSUES", data["totalIssueContributions"]),
        ("REVIEWS", data["totalPullRequestReviewContributions"]),
        ("REPOS COM COMMITS", data["totalRepositoriesWithContributedCommits"]),
        ("ÚLTIMOS 30 DIAS", last_30),
        ("ÚLTIMOS 7 DIAS", last_7),
    ]
    for index, (label, value) in enumerate(small_stats):
        x = 36 + index * 169
        svg.extend([
            _rect(x, 210, 155, 71, "#123225", 10),
            _text(x + 11, 234, label, 11, "#A9D0B8", 700),
            _text(x + 11, 267, _number(value), 26, "#EDFAF1", 700),
        ])

    svg.extend([
        _text(36, 324, "CALENDÁRIO DE CONTRIBUIÇÕES", 15, "#B3DCC2", 700),
        _text(1023, 324, f"{len(records)} dias contabilizados", 12, "#B3DCC2", 400, "end"),
    ])

    grid_x, grid_y, step = 104.0, 354.0, 17.5
    # Dias na primeira semana podem começar no meio da coluna.
    last_labeled_month = -100.0
    for index, week in enumerate(weeks):
        x = grid_x + index * step
        days = week["contributionDays"]
        for entry in days:
            day = date.fromisoformat(entry["date"])
            n = entry["contributionCount"]
            weekday = (day.weekday() + 1) % 7
            y = grid_y + weekday * step
            level = 0 if n == 0 else 1 if n <= 3 else 2 if n <= 8 else 3 if n <= 16 else 4
            svg.append(_rect(x, y, 12.5, 12.5, COLORS[level], 2.5))
            if day.day == 1 and x - last_labeled_month > 47:
                svg.append(_text(x, 345, MONTHS[day.month - 1], 11, "#B9D5C2"))
                last_labeled_month = x
    for weekday, label in ((1, "SEG"), (3, "QUA"), (5, "SEX")):
        svg.append(_text(78, grid_y + weekday * step + 11, label, 11,
                         "#99BFAB", 400, "end"))
    svg.extend([
        _text(36, 495, "Menos", 12, "#B6D0C0"),
        *(_rect(84 + i * 18, 484, 12, 12, color, 2) for i, color in enumerate(COLORS)),
        _text(188, 495, "Mais", 12, "#B6D0C0"),
        _text(1023, 495, "Contribuições diárias, não apenas commits", 12,
              "#B6D0C0", 400, "end"),
        '<path d="M36 511 H1024" stroke="#28513D" stroke-width="1"/>',
        _text(36, 542, "VOLUME MENSAL", 15, "#B3DCC2", 700),
        _text(1023, 542, "Meses extremos podem ser parciais", 12,
              "#B3DCC2", 400, "end"),
    ])

    max_month = max(month_totals.values()) if month_totals else 1
    n_months = max(1, len(months))
    month_spacing = 948 / n_months
    bar_width = min(45.0, month_spacing * 0.58)
    base = 655.0
    for index, key in enumerate(months):
        value = month_totals[key]
        height = 0 if max_month == 0 else round((value / max_month) * 87, 1)
        center = 66 + (index + 0.5) * month_spacing
        svg.extend([
            _rect(center - bar_width / 2, base - max(height, 2), bar_width,
                  max(height, 2), "#4BBE82", 5),
            _text(center, 672, MONTHS[key[1] - 1], 11, "#CAE6D2", 400, "middle"),
            _text(center, max(561, base - height - 7), _number(value),
                  11, "#DEF7E8", 700, "middle"),
        ])

    svg.extend([
        '<path d="M36 685 H1024" stroke="#28513D" stroke-width="1"/>',
        _text(36, 707, f"Sincronizado em {updated}", 12, "#B4D6C1"),
        _text(1023, 707, "Apenas totais; projetos privados permanecem confidenciais",
              12, "#B4D6C1", 400, "end"),
        "</svg>",
    ])
    return "\n".join(svg) + "\n"


def main() -> None:
    # Escrita atômica: falha na API ou renderização não corrompe o painel atual.
    data = fetch_activity()
    svg = render(data)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".svg.tmp")
    try:
        temporary.write_text(svg, encoding="utf-8")
        temporary.replace(OUTPUT)
    finally:
        temporary.unlink(missing_ok=True)
    print("Painel de contribuições oficiais gerado; dados privados não divulgados.")


if __name__ == "__main__":
    main()
