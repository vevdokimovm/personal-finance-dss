# Fonts

LiberationSans-Regular.ttf / LiberationSans-Bold.ttf — метрически совместимый с Arial
свободный шрифт (лицензия SIL OFL / GPL+exception), содержит кириллицу. Зашит в репозиторий,
потому что встроенные шрифты reportlab (Helvetica/Vera) кириллицу не содержат — без бандла
PDF-экспорт выводил бы квадраты вместо русского текста. Регистрируется в `report_pdf.py`
как `FinpilotSans`/`FinpilotSans-Bold` и переиспользуется экспортом плана (`plan_export.py`).
Источник: пакет fonts-liberation (Debian/Ubuntu).
