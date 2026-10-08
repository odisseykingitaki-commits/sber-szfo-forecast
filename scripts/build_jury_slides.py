"""Build chart-first jury PDF: для_жюри/TASK2_presentation.pdf (11 landscape slides).

    python scripts/build_jury_slides.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JURY = ROOT / "для_жюри"
ASSETS = ROOT / "scripts" / "_pitch" / "presentation_assets"
OUT = JURY / "TASK2_presentation.pdf"
REPO_URL = "https://github.com/odisseykingitaki-commits/sber-szfo-forecast"

C_BG = "#f4f6f8"
C_NAVY = "#1e3a5f"
C_INK = "#1a2332"
C_MUTED = "#6b7280"
C_TEAL = "#2a6f6a"
C_ORANGE = "#c45c26"


def _fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    windir = Path(r"C:\Windows\Fonts")
    for reg, bold in [
        (windir / "arial.ttf", windir / "arialbd.ttf"),
        (windir / "Arial.ttf", windir / "Arialbd.ttf"),
        (windir / "calibri.ttf", windir / "calibrib.ttf"),
    ]:
        if reg.exists():
            pdfmetrics.registerFont(TTFont("Body", str(reg)))
            pdfmetrics.registerFont(TTFont("BodyBold", str(bold if bold.exists() else reg)))
            return "Body", "BodyBold"
    raise FileNotFoundError("Need Arial/Calibri TTF with Cyrillic")


def slides_spec():
    return [
        {
            "title": "Можно ли предсказать расходы — и поймать смену режима?",
            "phrases": [
                "280 МО СЗФО · 2 режима потребления · ≈24 месяца",
                "Прогноз числа и мониторинг структурных сдвигов — разные задачи.",
            ],
            "fig": "slide01_hook.png",
            "footer": "СЗФО · СберИндекс 2023–2024",
        },
        {
            "title": "Не одна модель — честный bakeoff на двух уровнях",
            "phrases": [
                "A: прогноз агрегатов Тип A / Тип B на горизонтах 1 / 3 / 6 / 12 мес.",
                "B: консенсус дат структурных сдвигов по спектральному сигналу структуры трат",
            ],
            "fig": "slide02_bakeoff.png",
            "footer": "паттерны потребления, не юр. статус МО",
        },
        {
            "title": "Утечка будущего искажала сравнение. Правило исправлено.",
            "phrases": [
                "Было: окно могло включать текущий месяц · Стало: окно полностью в прошлом",
                "После фикса вклад спектральных признаков в ошибку ослаб — ожидаемо.",
            ],
            "fig": "slide03_leakage.png",
            "footer": "канон: results/forecast_all_models.csv",
        },
        {
            "title": "После честного теста универсального победителя нет",
            "phrases": [
                "Средняя абсолютная ошибка (MAE) — по всем моделям и горизонтам из CSV",
                "Цвет: ниже MAE лучше · оранжевое число — победитель ячейки",
            ],
            "fig": "slide04_mae_grid.png",
            "footer": "",
        },
        {
            "title": "Кто выигрывает — зависит от типа и горизонта",
            "phrases": [
                "Городские 1/3/6 мес. — часто Prophet · сельские 3 мес. — LightGBM",
                "Naive и seasonal конкурентоспособны на части горизонтов",
            ],
            "fig": "slide05_winners.png",
            "footer": "победитель = минимальный MAE среди доступных моделей",
        },
        {
            "title": "ML выигрывает локально — не универсально",
            "phrases": [
                "Тип A, 3 мес.: LightGBM 1761 < Prophet 1839",
                "Тип B, 3 мес.: Prophet 2653 << LightGBM 5241",
            ],
            "fig": "slide06_rural_case.png",
            "footer": "",
        },
        {
            "title": "Foundation-модель не дала преимущества — и это результат",
            "phrases": [
                "Chronos-bolt-tiny (zero-shot): 0 / 8 выигранных горизонтов",
                "Ряд ≈24 точки слишком короткий для foundation time series",
            ],
            "fig": "slide07_chronos.png",
            "footer": "results/forecast_foundation.csv",
        },
        {
            "title": "Внешний сигнал: Trends слабый, GDELT без системного выигрыша",
            "phrases": [
                "Google Trends часто ухудшает MAE · один ряд на оба типа",
                "GDELT (глобальная база событий): заметна только городские 1 мес. (~−5.6%)",
            ],
            "fig": "slide08_external.png",
            "footer": "Trends ≠ новости",
        },
        {
            "title": "Сдвиги ловим консенсусом, не одним алгоритмом",
            "phrases": [
                "9 методов → сигнал при ≥5/9 · сильный при 7/9",
                "2023-11 · 2024-04 · 2024-09 (самая согласованная)",
            ],
            "fig": "slide09_changepoints.png",
            "footer": "сигнал: топ-5 собственных значений + PR₊ (без Frustration)",
        },
        {
            "title": "Что получает аналитик",
            "phrases": [
                "мониторинг переходов + выбор прогнозной модели по режиму",
                "честный протокол оценки без утечки будущего",
            ],
            "fig": "slide10_value.png",
            "footer": "",
        },
        {
            "title": "Режимы разные — и прогноз, и сдвиги это показывают",
            "phrases": [
                "Нет единого победителя по MAE · Chronos 0/8 · сдвиги: 2023-11 / 2024-04 / 2024-09",
                "Воспроизводимо из репозитория: configs + src/12 + src/13",
            ],
            "fig": "slide11_finale.png",
            "footer": "подробности метода — в методологическом отчёте",
        },
    ]


def build():
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader

    font, font_b = _fonts()
    specs = slides_spec()
    JURY.mkdir(parents=True, exist_ok=True)
    page = landscape(A4)
    c = canvas.Canvas(str(OUT), pagesize=page)
    W, H = page
    mx = 1.15 * cm
    header_h = 1.55 * cm
    footer_h = 0.75 * cm

    for i, s in enumerate(specs):
        c.setFillColor(colors.HexColor(C_BG))
        c.rect(0, 0, W, H, fill=1, stroke=0)

        c.setFillColor(colors.HexColor(C_NAVY))
        c.rect(0, H - header_h, W, header_h, fill=1, stroke=0)

        c.setFillColor(colors.white)
        title = s["title"]
        size = 15 if len(title) < 70 else 13
        c.setFont(font_b, size)
        max_w = W - 2 * mx
        if c.stringWidth(title, font_b, size) <= max_w:
            c.drawString(mx, H - 1.0 * cm, title)
        else:
            words = title.split()
            line1, line2 = "", ""
            for w in words:
                trial = (line1 + " " + w).strip()
                if c.stringWidth(trial, font_b, size - 1) < max_w:
                    line1 = trial
                else:
                    line2 = (line2 + " " + w).strip()
            c.setFont(font_b, size - 1)
            c.drawString(mx, H - 0.75 * cm, line1)
            if line2:
                c.drawString(mx, H - 1.25 * cm, line2)

        y = H - header_h - 0.45 * cm
        c.setFillColor(colors.HexColor(C_INK))
        for ph in s["phrases"][:4]:
            c.setFont(font, 12)
            c.drawString(mx, y, ph)
            y -= 0.48 * cm

        fig_path = ASSETS / s["fig"]
        band_top = y - 0.12 * cm
        band_bottom = footer_h + 0.28 * cm
        band_h = max(band_top - band_bottom, 3.5 * cm)
        band_w = W - 2 * mx

        if fig_path.exists():
            img = ImageReader(str(fig_path))
            nw, nh = img.getSize()
            scale = min(band_w / nw, band_h / nh)
            iw, ih = nw * scale, nh * scale
            x_img = (W - iw) / 2
            y_img = band_bottom + (band_h - ih) / 2
            c.drawImage(img, x_img, y_img, width=iw, height=ih,
                        preserveAspectRatio=True, mask="auto")
        else:
            c.setFillColor(colors.HexColor("#aa0000"))
            c.setFont(font, 10)
            c.drawString(mx, band_bottom + band_h / 2, f"[missing {s['fig']}]")

        c.setFillColor(colors.HexColor(C_MUTED))
        c.setFont(font, 7.5)
        left = s.get("footer") or ""
        right = f"Task 2 · {i + 1}/11 · {REPO_URL}"
        if left and "http" not in left:
            c.drawString(mx, 0.32 * cm, left[:100])
        c.drawRightString(W - mx, 0.32 * cm, right)
        c.setFillColor(colors.HexColor(C_TEAL))
        c.rect(0, 0, W * 0.55, 0.1 * cm, fill=1, stroke=0)
        c.setFillColor(colors.HexColor(C_ORANGE))
        c.rect(W * 0.55, 0, W * 0.45, 0.1 * cm, fill=1, stroke=0)
        c.showPage()

    c.save()
    print(f"OK slides -> {OUT}")


if __name__ == "__main__":
    build()
