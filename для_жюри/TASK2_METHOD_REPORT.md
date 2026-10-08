# Задача 2. Методологический отчёт: прогноз расходов и структурные сдвиги (СЗФО)

**Объект:** агрегаты расходов двух режимов потребления МО СЗФО (Тип A / Тип B, 140/140)  
**Два уровня:** (A) многомодельный прогноз H∈{1,3,6,12}; (B) changepoints на спектральном сигнале  
**Репозиторий:** https://github.com/odisseykingitaki-commits/sber-szfo-forecast  

Числа сверены с `results/forecast_all_models.csv`, `forecast_foundation.csv`, `forecast_news.csv`, `changepoints_consensus.csv` (канон после leakage-fix).

Отчёт **самодостаточен** — жюри может не видеть Task 1.

---

## 0. Постановка без Task 1

**Данные.** Помесячные расходы СберИндекса («Все категории»), **280 МО**, **≈24 месяца** (2023–2024).

**Два кластера.** По признакам расходов строится PLM → главная мода → проекция `U₁` → **медиана** → две группы по 140 МО.  
- **Тип A (сельский паттерн, cluster 0):** ↑ grocery  
- **Тип B (городской паттерн, cluster 1):** ↑ food / transport  

Ярлыки — интерпретация структуры трат, **не** юридический статус МО.

**Спектральные ряды.** Скользящие окна (типично 6 мес.) → λ₁…λ₅, PR₊, Frustration. В прогнозе только окна с **`end_dt < ds`**. В changepoints: сигнал **`[λ₁…λ₅, PR₊]`** (без Frustration).

---

## 1. Архитектура

| Уровень | Скрипт | Выход |
|---------|--------|-------|
| A · прогноз | `src/12_timeseries.py` | `results/forecast_all_models.csv` |
| B · сдвиги | `src/13_changepoints.py` | `changepoints_*.csv` |
| Foundation | `scripts/run_chronos_task2.py` | `forecast_foundation.csv` |
| News proxy | `scripts/run_gdelt_news_forecast.py` | `forecast_news.csv` |

---

## 2. Анти-утечка (критично)

Был баг: `start_dt ≤ ds`.  
**Фикс:** `mask = spectral['end_dt'] < row['ds']`.

После фикса «магический» вклад спектральных фич ослаб — ожидаемо. Все выводы ниже — **post-leakage**.

---

## 3. Exact MAE (winner = min MAE)

### Тип A — сельские

| H | naive | seasonal | prophet | lgbm | winner |
|--:|------:|---------:|--------:|-----:|--------|
| 1 | 5197.90 | **4314.35** | 4375.11 | 5222.82 | **seasonal** |
| 3 | 3133.21 | 3862.03 | 1838.56 | **1761.44** | **lgbm** |
| 6 | **1496.77** | 3663.17 | 1618.03 | 1649.22 | **naive** |
| 12 | 1888.81 | 2997.43 | **1514.08** | — | **prophet** |

### Тип B — городские

| H | naive | seasonal | prophet | lgbm | winner |
|--:|------:|---------:|--------:|-----:|--------|
| 1 | 7222.19 | 7282.87 | **5641.67** | 8478.98 | **prophet** |
| 3 | 4713.06 | 6386.06 | **2653.36** | 5240.56 | **prophet** |
| 6 | 2168.01 | 6415.53 | **2039.51** | 2782.76 | **prophet** |
| 12 | **2525.30** | 6608.86 | 3415.60 | — | **naive** |

**Итог:** единого победителя нет. Prophet часто городские; LGBM — сельские H=3; naive конкурентоспособен. Trends **не** стабильно помогают. H=12: LGBM/CatBoost пусты (мало точек после lag_12).

---

## 4. Chronos (honest negative)

`amazon/chronos-bolt-tiny`, zero-shot, тот же holdout.

| | Выиграно vs лучший классический |
|---|---|
| Chronos | **0 / 8** |

На ≈24 точках foundation не сильнее Prophet/LGBM/naive.

---

## 5. Внешние сигналы

| Сигнал | Статус |
|--------|--------|
| Google Trends | выровнен по дате; часто ухудшает MAE; один SZFO-ряд на оба типа |
| GDELT Russia-wide | выгрузка OK; систематического MAE-win нет; заметна городские H=1 (~−5.6%) |
| News NLP по СЗФО | не реализован |

**Trends ≠ новости.**

---

## 6. Changepoints

9 методов ruptures+CUSUM → консенсус **≥50%**:

| Дата | Голоса | Статус |
|------|-------:|--------|
| **2024-09-01** | **7/9** | сильнейшая |
| 2023-11-01 | 5/9 | сигнал |
| 2024-04-01 | 5/9 | сигнал |

PR₊ вокруг 2024-09: **4.303 → 4.267 → 4.162** (`dynamic_summary.json`).

---

## 7. Воспроизведение

```bash
conda activate sber
pip install -r requirements.txt
python src/12_timeseries.py
python src/13_changepoints.py
# optional:
python scripts/run_chronos_task2.py
python scripts/build_task2_pdfs.py
```

Конфиги: `configs/task2_config.yaml`, `configs/task2_methods.yaml`.

---

## 8. Краткие выводы

1. Task 2 = прогноз + консенсус changepoints; самодостаточно без Task 1.  
2. После `end_dt < ds` **нет доминирующей модели**.  
3. Chronos 0/8; GDELT без системного win.  
4. Консенсусные даты: **2023-11 / 2024-04 / 2024-09**.  
5. Аналитику нужны и число, и сигнал перехода режима.
