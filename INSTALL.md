# Установка и воспроизведение (Задача 2)

## 1. Окружение

```bash
conda create -n sber python=3.12 -y
conda activate sber
pip install -r requirements.txt
```

Конфиги: `configs/task2_config.yaml`, `configs/task2_methods.yaml`.

## 2. Данные / артефакты

| Путь | Назначение |
|------|------------|
| `results/labels_threshold.npy` | метки Тип A/B (140/140) |
| `results/dynamic_summary.json` | скользящие окна PLM → спектральные признаки |
| `data/processed/google_trends_szfo.csv` | Google Trends (прокси) |
| `results/forecast_all_models.csv` | **канон MAE** (после фикса утечки) |
| `results/changepoints_consensus.csv` | консенсус дат структурных сдвигов |

Для полного пересчёта прогноза нужен `data/intermediate/spend.parquet` (сырые расходы конкурса; крупный raw в `.gitignore`).

## 3. Запуск

```bash
conda activate sber
python src/12_timeseries.py
python src/13_changepoints.py
```

Опционально:

```bash
python scripts/run_chronos_task2.py          # foundation MAE (Chronos)
python scripts/run_gdelt_news_forecast.py    # GDELT ± Trends
```

Критическое правило анти-утечки: спектральные признаки месяца `ds` берутся только из окон, полностью завершённых раньше этой даты (`end_dt < ds`).

## 4. Пересборка PDF

```bash
pip install reportlab pillow pyyaml
python scripts/build_task2_pdfs.py
```

Выход: `для_жюри/TASK2_method_report.pdf`, `для_жюри/TASK2_presentation.pdf`.

Репозиторий: https://github.com/odisseykingitaki-commits/sber-szfo-forecast
