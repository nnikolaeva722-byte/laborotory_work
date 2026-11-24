from pathlib import Path
# пути
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
REPORTS_DIR = "reports"
FIGURES_DIR = "reports/figures"

# какие файлы брать
TRIPS_PATTERN = "trips_*.csv"

# параметры очистки
MAX_COST_RATIO = 5.0 

# параметры визуализации 
WIDE_FIGSIZE=(9,4)
SEABORN_FIGSIZE=(9,5)
HEATMAP_FIGSIZE=(11,5)
DASHBOARD_FIGSIZE=(14,9)
LINE_MARKER='o'
SCATTER_ALPHA=0.5
HEATMAP_CMAP='Blues'
HEATMAP_FORMAT='.1f'

MILLION=1_000_000
THOUSAND=1_000
REVENUE_YLIM=(0,14)
GROWTH_LABEL='рост всего 2%'
GROWTH_XY=(3,11.3)
GROWTH_XYTEXT=(1.5,9)
COST_BINS=30
OTD_TARGET=90
OTD_COLOR='#C44E52'
OTD_LINESTYLE='--'
OTD_XLIM=(0,100)
DASHBOARD_TITLE='Перевозки: апрель-май 2025'
DASHBOARD_TITLE_SIZE=15
FIGURE_DPI=130
DASHBOARD_DPI=150

CHARTS_DIR=Path('charts')
