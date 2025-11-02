# ADI Map (by band)

Plot your ADIF (`.adi`) QSOs on an interactive Leaflet map using Folium.
Features:

- Colored markers (by band or mode)
- Per-band / per-mode toggleable layers
- Global and per-band/per-mode heatmaps
- Basemap switcher (OSM, Terrain, Toner, Positron, Dark)
- Optional line connecting QSOs
- Home QTH marker
- Stats panel (totals, unique calls, date range, per-band & per-mode counts)
- Time slider (animate QSOs chronologically)
- Callsign links (QRZ, Club Log) in popups
- CSV and GeoJSON export

## Install

```bash
pip install .
```

## CLI examples

```bash
# Basic
adimap log.adi

# With title, connect QSOs, and home QTH
adimap log.adi --title "My ADI Map" --connect --home-grid FN20

# Layers & colors
adimap log.adi --layers-by-band         # layers per band; markers colored by mode
adimap log.adi --layers-by-mode         # layers per mode; markers colored by mode

# Heatmaps
adimap log.adi --heatmap                 # global heatmap
adimap log.adi --layers-by-band --heatmap-by-band
adimap log.adi --layers-by-mode --heatmap-by-mode

# Disable clustering
adimap log.adi --no-cluster

# Time slider
adimap log.adi --time-slider

# Exports
adimap log.adi --export-csv qsos.csv --export-geojson qsos.geojson
```

## Notes

- If you enable both `--layers-by-band` and `--layers-by-mode`, band layers
  take precedence and markers are colored by mode. (Nested subgroups are
  intentionally avoided to keep the UI simple.)
- ADIF timestamps are derived from `QSO_DATE` (YYYYMMDD) and `TIME_ON`
  (HHMM[SS]). When missing, those QSOs are omitted from the time slider.

```
bash
pip install .
```

## CLI

```bash
# Basic
adimap /path/to/log.adi

# Add title and connect QSOs with a line
adimap /path/to/log.adi --title "My ADI Map" --connect

# Home QTH via grid or lat/lon
a dimap log.adi --home-grid FN20
adimap log.adi --home-lat 37.7749 --home-lon -122.4194

# Per-band layers and heatmaps
adimap log.adi --layers-by-band
adimap log.adi --heatmap
adimap log.adi --layers-by-band --heatmap-by-band
```

## Notes

- Coordinates: prefer LAT/LON; otherwise convert Maidenhead `GRIDSQUARE`.
- Unknown/missing bands display in gray.
- Records without a plottable location are skipped with a summary.
- When `--layers-by-band` is used, markers are placed in a FeatureGroup per
  band and a LayerControl is added so you can toggle visibility.
- `--heatmap` adds a global heatmap of all points; `--heatmap-by-band` adds a
  heatmap layer for each band (inside the band's layer when applicable).

```
bash
pip install .
```

## CLI

```bash
# Basic
adimap /path/to/log.adi

# Add title and connect QSOs with a line
adimap /path/to/log.adi --title "My ADI Map" --connect

# Home QTH via grid or lat/lon
adimap log.adi --home-grid FN20
adimap log.adi --home-lat 37.7749 --home-lon -122.4194
```

This generates `adi_map.html` in the current directory.

## Notes

- Coordinates: prefer LAT/LON; otherwise convert Maidenhead `GRIDSQUARE`.
- Unknown/missing bands display in gray.
- Records without a plottable location are skipped with a summary.

```

---
