# # -*- coding: utf-8 -*-
'''Точка входа: запускает весь анализ от сырых данных до отчёта.'''
import json
from os.path import relpath
from datetime import datetime
from pathlib import Path

import config
from src.load import load_trips, load_carriers
from src.prepare import prepare_trips
from src import visualize


def df_to_markdown(df):
    '''Превращает таблицу в markdown без внешних зависимостей.'''
    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "|" + "---|" * len(df.columns)
    rows = ["| " + " | ".join(str(v) for v in row) + " |"
            for row in df.itertuples(index=False)]
    return chr(10).join([header, sep] + rows)


def build_report(kpi, quality, by_carrier, figures):
    '''Собирает текстовый отчёт в формате Markdown.'''
    lines = ["# Отчёт по перевозкам", ""]
    lines.append("Сформирован: " + datetime.now().strftime("%d.%m.%Y %H:%M"))

    lines += ["", "## Ключевые показатели", ""]
    for k, v in kpi.items():
        lines.append(f"- **{k}**: {v}")

    lines += ["", "## Качество данных", ""]
    for k, v in quality.items():
        lines.append(f"- {k}: {v}")

    lines += ["", "## По перевозчикам", "", df_to_markdown(by_carrier)]

    lines += ["", "## Графики", ""]
    for path in figures:
        link = Path(relpath(path, config.REPORTS_DIR)).as_posix()
        marker = "!" if path.suffix == ".png" else ""
        lines.append(f"{marker}[{path.stem}]({link})")

    return chr(10).join(lines)


def main():
    started = datetime.now()
    print("=" * 56)
    print("ЗАПУСК PIPELINE", started.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 56)

    for folder in (config.PROCESSED_DIR, config.REPORTS_DIR, config.FIGURES_DIR):
        Path(folder).mkdir(parents=True, exist_ok=True)

    print("[1/5] загрузка")
    raw = load_trips(config.RAW_DIR, config.TRIPS_PATTERN)
    carriers = load_carriers(config.RAW_DIR)

    print("[2/5] подготовка")
    clean, quality = prepare_trips(raw, max_cost_ratio=config.MAX_COST_RATIO)
    clean_path = Path(config.PROCESSED_DIR) / "trips_clean.csv"
    clean.to_csv(clean_path, index=False, encoding="utf-8")
    print(f"    сохранено: {clean_path} ({len(clean)} строк)")

    print("[3/5] расчёт метрик")
    kpi = {
        "рейсов": len(clean),
        "выручка": int(clean["cost_rub"].sum()),
        "средний чек": round(clean["cost_rub"].mean()),
        "медианный чек": round(clean["cost_rub"].median()),
        "выручка на км": round(float(clean["cost_rub"].sum() / clean["distance_km"].sum()), 1),
        "OTD, %": round(float((~clean["is_delayed"]).mean() * 100), 1),
    }

    by = {}
    for column in ("carrier", "month"):
        table = (clean.groupby(column)
                 .agg(trips=("trip_id", "count"),
                      revenue=("cost_rub", "sum"),
                      avg_ticket=("cost_rub", "mean"),
                      otd=("is_delayed", lambda s: (~s).mean() * 100))
                 .round(1)
                 .sort_values("revenue", ascending=False)
                 .reset_index())
        table.to_csv(Path(config.PROCESSED_DIR) / f"kpi_by_{column}.csv",
                     index=False, encoding="utf-8")
        by[column] = table
    by_carrier = by["carrier"]

    print("[4/5] графики")
    fig1 = visualize.plot_revenue_by_month(clean, config.FIGURES_DIR)
    fig2 = visualize.plot_otd_by_carrier(clean, config.FIGURES_DIR, target=config.OTD_TARGET)
    figures = [fig1, fig2]
    for plot in (visualize.plot_revenue_by_carrier, visualize.plot_trips_by_month,
                 visualize.plot_cost_by_carrier, visualize.plot_cargo_weight,
                 visualize.plot_cost_and_distance, visualize.plot_delay_heatmap,
                 visualize.plot_revenue_by_route, visualize.plot_cost_by_cargo,
                 visualize.plot_route_revenue_bar, visualize.plot_trip_cost_histogram):
        figures.append(plot(clean, config.FIGURES_DIR))
    if "duration_h" in clean.columns:
        figures.append(visualize.plot_distance_and_duration(clean, config.FIGURES_DIR))
    else:
        print("    график расстояния и времени пропущен: нет столбца duration_h")
    figures.append(visualize.plot_dashboard(clean, config.FIGURES_DIR, target=config.OTD_TARGET))
    for path in figures:
        print(f"    {path}")

    print("[5/5] отчёт")
    report_path = Path(config.REPORTS_DIR) / "report.md"
    report_path.write_text(build_report(kpi, quality, by_carrier, figures),
                           encoding="utf-8")

    manifest = {
        "запуск": started.isoformat(timespec="seconds"),
        "длительность, с": round((datetime.now() - started).total_seconds(), 2),
        "параметры": {"MAX_COST_RATIO": config.MAX_COST_RATIO,
                      "OTD_TARGET": config.OTD_TARGET,
                      "TRIPS_PATTERN": config.TRIPS_PATTERN},
        "качество данных": quality,
        "итоговые метрики": kpi,
    }
    manifest_path = Path(config.PROCESSED_DIR) / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                             encoding="utf-8")

    print(f"    {report_path}")
    print(f"    {manifest_path}")
    print("ГОТОВО")
    return manifest


if __name__ == "__main__":
    main()

