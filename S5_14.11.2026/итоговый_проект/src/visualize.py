# -*- coding: utf-8 -*-
'''Слой 3 построение графиков'''
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

import config as cfg


def _save_png(fig, out_dir, filename, dpi=cfg.FIGURE_DPI):
    '''Сохраняет рисунок, закрывает его и возвращает путь.'''
    path = Path(out_dir) / filename
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
    finally:
        plt.close(fig)
    return path


def plot_revenue_by_carrier(df, out_dir=cfg.CHARTS_DIR):
    '''Строит столбчатую диаграмму выручки по перевозчикам.'''
    carrier_sorted = df.groupby("carrier")["cost_rub"].sum().sort_values()
    fig, ax = plt.subplots(figsize=cfg.WIDE_FIGSIZE)
    ax.barh(carrier_sorted.index,carrier_sorted.values/ cfg.MILLION)
    ax.set_title('Выручка по перевозчикам')
    ax.set_xlabel('Выурчка, млн. руб')
    ax.set_ylabel('Перевозчики')
    fig.tight_layout()

    return _save_png(fig, out_dir, 'revenue_by_carrier.png')


def plot_trips_by_month(df, out_dir=cfg.CHARTS_DIR):
    '''Показывает, как менялось число рейсов по месяцам.'''
    trips_month = df.groupby('month')['trip_id'].count()
    fig, ax = plt.subplots(figsize=cfg.WIDE_FIGSIZE)
    ax.plot(trips_month.index,trips_month.values,marker=cfg.LINE_MARKER)
    ax.set_title('Число рейсов по месяцам')
    ax.set_xlabel('Год, месяц')
    ax.set_ylabel('Кол-во рейсов')
    fig.tight_layout()

    return _save_png(fig, out_dir, 'trips_by_month.png')


def plot_distance_and_duration(df, out_dir=cfg.CHARTS_DIR):
    '''Показывает связь расстояния со временем в пути.'''
    fig, ax = plt.subplots(figsize=cfg.WIDE_FIGSIZE)
    ax.scatter(df['duration_h'],df['distance_km'],alpha=cfg.SCATTER_ALPHA)
    ax.set_title('Зависимость расстояния от времени в пути')
    ax.set_xlabel('Время в пути, часы')
    ax.set_ylabel('Расстояние, км')
    fig.tight_layout()

    return _save_png(fig, out_dir, 'distance_and_duration.png')


def plot_cost_by_carrier(df, out_dir=cfg.CHARTS_DIR):
    '''Сравнивает распределение стоимости рейса по перевозчикам.'''
    fig, ax = plt.subplots(figsize=cfg.SEABORN_FIGSIZE)
    order = df.groupby("carrier")["cost_rub"].median().sort_values().index
    sns.boxplot(data=df,x='carrier',y='cost_rub',ax=ax, order=order)

    ax.set_title("Распределение стоимости рейса по перевозчикам")
    ax.set_xlabel("")
    ax.set_ylabel("Стоимость рейса, руб.")
    fig.tight_layout()

    return _save_png(fig, out_dir, 'cost_by_carrier.png')


def plot_cargo_weight(df, out_dir=cfg.CHARTS_DIR):
    '''Строит гистограмму веса груза.'''
    fig,ax= plt.subplots(figsize=cfg.SEABORN_FIGSIZE)
    sns.histplot(data=df,x="weight_t")

    ax.set_title("Распределение веса груза.")
    ax.set_xlabel("Вес, тонн")
    ax.set_ylabel("Кол-во рейсов")

    fig.tight_layout()

    return _save_png(fig, out_dir, 'cargo_weight.png')


def plot_cost_and_distance(df, out_dir=cfg.CHARTS_DIR):
    '''Показывает стоимость рейса по расстоянию и типу груза.'''
    fig,ax= plt.subplots(figsize=cfg.SEABORN_FIGSIZE)
    sns.scatterplot(data=df,x='distance_km',y=df['cost_rub'], hue='cargo_type')

    ax.set_title("Распрделение цены по расстоянию рейса и типу груза.")
    ax.set_xlabel("Расстояние, км")
    ax.set_ylabel("Цена, рубли")

    fig.tight_layout()

    return _save_png(fig, out_dir, 'cost_and_distance.png')


def plot_delay_heatmap(df, out_dir=cfg.CHARTS_DIR):
    '''Строит теплокарту средней задержки по маршрутам и перевозчикам.'''
    pivot_t = df.pivot_table(index="route", columns="carrier",
                           values="delay_h", aggfunc="mean", fill_value=0) 

    fig, ax = plt.subplots(figsize=cfg.HEATMAP_FIGSIZE)
    sns.heatmap(pivot_t, annot=True, fmt=cfg.HEATMAP_FORMAT, cmap=cfg.HEATMAP_CMAP, ax=ax,
                cbar_kws={"label": "Средняя задержка, час."})
    ax.set_title("Средняя задержка, час .")
    ax.set_xlabel("Перевозчик")
    ax.set_ylabel("Маршрут")


    fig.tight_layout()

    return _save_png(fig, out_dir, 'delay_heatmap.png')


def plot_revenue_by_route(df, out_dir=cfg.CHARTS_DIR):
    '''Строит интерактивную диаграмму выручки по маршрутам и сохраняет её в HTML.'''
    route_stats = (df.groupby("route")
                   .agg(revenue=("cost_rub", "sum"), trips=("trip_id", "count"))
                   .reset_index()
                   .sort_values("revenue",ascending=False))

    fig = px.bar(route_stats, x="route", y="revenue" ,title="Выручка по маршрутам(наведите курсор на столбец)",
                hover_data=["trips", "route"], labels={'route':'Маршрут','revenue':'Выручка, руб.','trips':'Кол-во рейсов'}
                )

    path = Path(out_dir) / 'revenue_by_route.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs=True)
    return path


def plot_cost_by_cargo(df, out_dir=cfg.CHARTS_DIR):
    '''Строит интерактивное распределение стоимости рейса по типам груза.'''
    fig = px.box(df, x="cargo_type", y="cost_rub" ,title="Зависимость стоимости рейса от типа груза(наведите курсор на столбец)",
                 labels={'cargo_type':'Тип груза','cost_rub':'Стоимость рейса, руб.'})

    path = Path(out_dir) / 'cost_by_cargo.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs=True)
    return path


def _draw_revenue_by_month(df, ax):
    '''Рисует выручку по месяцам на оси дашборда.'''
    monthly_rev=df.groupby("month")["cost_rub"].sum()/cfg.MILLION


    ax.plot(monthly_rev.index,monthly_rev.values,marker=cfg.LINE_MARKER)
    ax.set_title('Динамика выручки')
    ax.set_xlabel('Год, месяц')
    ax.set_ylabel('Выручка, млн. рублей')
    ax.set_ylim(*cfg.REVENUE_YLIM)
    for x, y in zip(monthly_rev.index, monthly_rev.values):
        ax.annotate(f"{y:.1f}", xy=(x, y), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=9)

    ax.annotate(cfg.GROWTH_LABEL,
                xy=cfg.GROWTH_XY, xytext=cfg.GROWTH_XYTEXT,
                arrowprops=dict(arrowstyle="->", color="black"))


def plot_revenue_by_month(df, out_dir=cfg.CHARTS_DIR):
    '''Динамика выручки по месяцам.'''
    fig, ax = plt.subplots(figsize=cfg.WIDE_FIGSIZE)
    _draw_revenue_by_month(df, ax)
    fig.tight_layout()

    return _save_png(fig, out_dir, 'revenue_by_month.png')


def _draw_route_revenue_bar(df, ax):
    '''Рисует выручку по маршрутам на оси дашборда.'''

    route_sorted = df.groupby("route")["cost_rub"].sum().sort_values()
    ax.barh(route_sorted.index,route_sorted.values/ cfg.MILLION)
    ax.set_title('Выручка по маршрутам')
    ax.set_xlabel('Выурчка, млн. руб')
    ax.set_ylabel('Маршруты')


def plot_route_revenue_bar(df, out_dir=cfg.CHARTS_DIR):
    '''Столбчатая диаграмма выручки по маршрутам.'''
    fig, ax = plt.subplots(figsize=cfg.HEATMAP_FIGSIZE)
    _draw_route_revenue_bar(df, ax)
    fig.tight_layout()

    return _save_png(fig, out_dir, 'route_revenue_bar.png')


def _draw_trip_cost_histogram(df, ax):
    '''Рисует гистограмму стоимости рейса на оси дашборда.'''

    ax.hist(df['cost_rub']/cfg.THOUSAND,bins=cfg.COST_BINS)
    ax.set_title("Распредление стоимости ")
    ax.set_xlabel("Стоимость рейса, тыс. руб.")
    ax.set_ylabel("Количество рейсов, шт.")


def plot_trip_cost_histogram(df, out_dir=cfg.CHARTS_DIR):
    '''Распределение стоимости рейса.'''
    fig, ax = plt.subplots(figsize=cfg.WIDE_FIGSIZE)
    _draw_trip_cost_histogram(df, ax)
    fig.tight_layout()

    return _save_png(fig, out_dir, 'trip_cost_histogram.png')


def _draw_otd_by_carrier(df, ax, target):
    '''Рисует долю рейсов без задержки и линию цели по OTD.'''
    kpi=df.groupby('carrier').agg(otd=("delay_h", lambda s: (s == 0).mean() * 100))

    ax.barh(kpi.index, kpi['otd'])
    ax.axvline(target, color=cfg.OTD_COLOR, linestyle=cfg.OTD_LINESTYLE, label=f'цель: {target}%')
    if kpi['otd'].max()<target:
        ax.set_title(f'Никто из перевозчиков не достиг цели OTD - {target}%!')
    else:
        ax.set_title(f'OTD по перевозчикам, цель {target}%')
    ax.set_xlabel("OTD, %")
    ax.set_ylabel("Перевозчик")
    ax.set_xlim(*cfg.OTD_XLIM)


def plot_otd_by_carrier(df, out_dir=cfg.CHARTS_DIR, target=cfg.OTD_TARGET):
    '''Доля рейсов без задержки с линией целевого OTD.'''
    fig, ax = plt.subplots(figsize=cfg.WIDE_FIGSIZE)
    _draw_otd_by_carrier(df, ax, target)
    fig.tight_layout()

    return _save_png(fig, out_dir, 'otd_by_carrier.png')


def plot_dashboard(df, out_dir=cfg.CHARTS_DIR, target=cfg.OTD_TARGET):
    '''Собирает четыре графика дашборда и сохраняет их в PNG.'''
    fig, axes = plt.subplots(2, 2, figsize=cfg.DASHBOARD_FIGSIZE)

    _draw_revenue_by_month(df,axes[0,0])
    _draw_route_revenue_bar(df,axes[0,1])
    _draw_trip_cost_histogram(df,axes[1,0])
    _draw_otd_by_carrier(df,axes[1,1],target)

    fig.suptitle(cfg.DASHBOARD_TITLE, fontsize=cfg.DASHBOARD_TITLE_SIZE)
    fig.tight_layout()

    return _save_png(fig, out_dir, 'dashboard.png', dpi=cfg.DASHBOARD_DPI)
