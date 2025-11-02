from __future__ import annotations

import csv
import json
from datetime import datetime
from textwrap import dedent
from typing import Dict, Iterable, List, Optional, Tuple

import folium
from folium.plugins import HeatMap, MarkerCluster, TimestampedGeoJson

from .maidenhead import maidenhead_to_latlon

# -------------------------- Parsing helpers ---------------------------


def _parse_coord(text: str, is_lat: bool) -> Optional[float]:
    if text is None:
        return None

    s = text.strip()
    if not s:
        return None

    suffix = s[-1].upper() if s[-1].isalpha() else ""
    val_str = s[:-1] if suffix else s

    try:
        val = float(val_str)
    except ValueError:
        return None

    if suffix:
        if suffix in ("N", "E"):
            pass
        elif suffix in ("S", "W"):
            val = -val
        else:
            return None

    if is_lat and not (-90.0 <= val <= 90.0):
        return None
    if not is_lat and not (-180.0 <= val <= 180.0):
        return None

    return val


def parse_latlon(lat_str: str, lon_str: str) -> Optional[Tuple[float, float]]:
    lat = _parse_coord(lat_str, True)
    lon = _parse_coord(lon_str, False)
    if lat is None or lon is None:
        return None
    return (lat, lon)


def best_latlon(entry: Dict[str, str]) -> Optional[Tuple[float, float, str]]:
    lat = entry.get("LAT")
    lon = entry.get("LON")
    if lat and lon:
        pair = parse_latlon(lat, lon)
        if pair:
            return (pair[0], pair[1], "LATLON")

    grid = entry.get("GRIDSQUARE") or entry.get("MY_GRIDSQUARE")
    if grid:
        pair2 = maidenhead_to_latlon(grid)
        if pair2:
            return (pair2[0], pair2[1], "GRID")

    return None


# -------------------------- UI + formatting ---------------------------


def format_popup(entry: Dict[str, str]) -> str:
    call = entry.get("CALL", "QSO")
    # external lookups
    qrz = f"https://www.qrz.com/lookup/{call}"
    clublog = f"https://clublog.org/logsearch/{call}"

    fields = []
    for key in (
        "CALL",
        "QSO_DATE",
        "TIME_ON",
        "BAND",
        "FREQ",
        "MODE",
        "RST_SENT",
        "RST_RCVD",
        "COUNTRY",
        "GRIDSQUARE",
        "LAT",
        "LON",
    ):
        value = entry.get(key)
        if value:
            fields.append(f"<b>{key}</b>: {value}")

    links = (
        f"<div style='margin-top:6px'>"
        f"<a href='{qrz}' target='_blank' rel='noopener'>QRZ</a> · "
        f"<a href='{clublog}' target='_blank' rel='noopener'>Club Log</a>"
        f"</div>"
    )

    body = ("<br>".join(fields) if fields else "<i>No details</i>") + links
    return body


def _title_element(title: str) -> folium.Element:
    html = dedent(
        f"""
        <div style="position: fixed;
                    top: 10px; left: 50%; transform: translateX(-50%);
                    z-index: 9999; background: white; padding: 6px 10px;
                    border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.15);
                    font-family: sans-serif; font-size: 16px;">
          {title}
        </div>
        """
    ).strip()
    return folium.Element(html)


def _legend_element(items: List[Tuple[str, str]], title: str) -> folium.Element:
    rows = []
    for label, color in sorted(items):
        rows.append(
            (
                '<div style="display:flex;align-items:center;margin:2px 0;">'
                f'<span style="display:inline-block;width:12px;height:12px;'
                f'border-radius:50%;background:{color};margin-right:6px;"></span>'
                f"{label}</div>"
            )
        )

    html = dedent(
        f"""
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;
                    background: white; padding: 8px 10px; border-radius: 8px;
                    box-shadow: 0 1px 6px rgba(0,0,0,0.15);
                    font-family: sans-serif; font-size: 13px;">
          <b>{title}</b>
          <div style="margin-top:4px;">{''.join(rows)}</div>
        </div>
        """
    ).strip()
    return folium.Element(html)


def _stats_panel(entries: List[Dict[str, str]]) -> folium.Element:
    total = len(entries)
    calls = {e.get("CALL", "") for e in entries if e.get("CALL")}
    dates: List[datetime] = []

    def _parse_dt(e: Dict[str, str]) -> Optional[datetime]:
        d = (e.get("QSO_DATE") or "").strip()
        t = (e.get("TIME_ON") or "").strip()
        if len(d) == 8:
            y, m, day = d[:4], d[4:6], d[6:8]
            hh = t[:2] if len(t) >= 2 else "00"
            mm = t[2:4] if len(t) >= 4 else "00"
            ss = t[4:6] if len(t) >= 6 else "00"
            try:
                return datetime.fromisoformat(f"{y}-{m}-{day}T{hh}:{mm}:{ss}")
            except ValueError:
                return None
        return None

    for e in entries:
        dt = _parse_dt(e)
        if dt:
            dates.append(dt)

    drange = f"{min(dates).date()} → {max(dates).date()}" if dates else "n/a"

    # counts by band / mode
    by_band: Dict[str, int] = {}
    by_mode: Dict[str, int] = {}
    for e in entries:
        b = (e.get("BAND") or "").strip().upper() or "OTHER"
        m = (e.get("MODE") or "").strip().upper() or "OTHER"
        by_band[b] = by_band.get(b, 0) + 1
        by_mode[m] = by_mode.get(m, 0) + 1

    def _tab(d: Dict[str, int]) -> str:
        return "".join(
            f"<div style='display:flex;justify-content:space-between'><span>{k}</span><span>{v}</span></div>"
            for k, v in sorted(d.items())
        )

    html = dedent(
        f"""
        <div style="position: fixed; left: 20px; bottom: 20px; z-index: 9999;
                    background: white; padding: 10px 12px; border-radius: 8px;
                    box-shadow: 0 1px 6px rgba(0,0,0,0.15); font-family: sans-serif;
                    font-size: 13px; min-width: 220px;">
          <b>Log stats</b>
          <div style="margin-top:6px">
            <div><b>Total QSOs:</b> {total}</div>
            <div><b>Unique calls:</b> {len(calls)}</div>
            <div><b>Date range:</b> {drange}</div>
          </div>
          <div style="margin-top:8px"><b>By band</b>{_tab(by_band)}</div>
          <div style="margin-top:8px"><b>By mode</b>{_tab(by_mode)}</div>
        </div>
        """
    ).strip()
    return folium.Element(html)


# -------------------------- Colors & mapping --------------------------

BAND_COLORS = {
    "160M": "darkpurple",
    "80M": "darkred",
    "60M": "lightred",
    "40M": "orange",
    "30M": "beige",
    "20M": "blue",
    "17M": "lightblue",
    "15M": "green",
    "12M": "lightgreen",
    "10M": "cadetblue",
    "6M": "purple",
    "4M": "pink",
    "2M": "darkgreen",
    "1.25M": "lightgray",
    "70CM": "gray",
    "33CM": "black",
    "23CM": "darkblue",
}

MODE_COLORS = {
    "SSB": "blue",
    "CW": "darkred",
    "FT8": "green",
    "FT4": "purple",
    "FM": "orange",
    "RTTY": "darkpurple",
    "AM": "gray",
}

DEFAULT_COLOR = "gray"


# ---------------------------- Map builder ----------------------------


def build_map(
    records: List[Dict[str, str]],
    out_path: str,
    title: str = "ADIF QSO Map",
    connect: bool = False,
    home_latlon: Optional[Tuple[float, float]] = None,
    layers_by_band: bool = False,
    layers_by_mode: bool = False,
    heatmap: bool = False,
    heatmap_by_band: bool = False,
    heatmap_by_mode: bool = False,
    cluster: bool = True,
    export_csv: Optional[str] = None,
    export_geojson: Optional[str] = None,
    time_slider: bool = False,
) -> None:
    """Create the Folium map with optional layers, heatmaps, exports & time.

    Notes
    -----
    * If both ``layers_by_band`` and ``layers_by_mode`` are True, band layers
      take precedence and markers are colored by **mode** (so you still get a
      mode legend). For simplicity we avoid nested subgroups.
    * Use ``cluster=False`` to disable clustering on base-layer maps or inside
      band/mode layers.
    """
    points: List[Tuple[float, float, Dict[str, str]]] = []
    skipped = 0

    for rec in records:
        pos = best_latlon(rec)
        if pos is None:
            skipped += 1
            continue
        lat, lon, _src = pos
        points.append((lat, lon, rec))

    if not points and not home_latlon:
        raise SystemExit("No plottable QSO locations found (no LAT/LON or GRIDSQUARE).")

    # Center
    if home_latlon:
        center = home_latlon
    else:
        avg_lat = sum(p[0] for p in points) / len(points)
        avg_lon = sum(p[1] for p in points) / len(points)
        center = (avg_lat, avg_lon)

    fmap = folium.Map(
        location=center, zoom_start=2, control_scale=True, prefer_canvas=True
    )

    # # Basemaps
    # folium.TileLayer("OpenStreetMap").add_to(fmap)
    # folium.TileLayer("Stamen Terrain").add_to(fmap)
    # folium.TileLayer("Stamen Toner").add_to(fmap)
    # folium.TileLayer("CartoDB positron").add_to(fmap)
    # folium.TileLayer("CartoDB dark_matter").add_to(fmap)

    # Basemaps (explicit tiles + proper attribution)
    folium.TileLayer(
        tiles="OpenStreetMap", name="OpenStreetMap", attr="© OpenStreetMap contributors"
    ).add_to(fmap)

    folium.TileLayer(
        tiles="Stamen Terrain",
        name="Stamen Terrain",
        attr="Map tiles by Stamen Design, under CC BY 3.0. Data © OpenStreetMap contributors",
    ).add_to(fmap)

    folium.TileLayer(
        tiles="Stamen Toner",
        name="Stamen Toner",
        attr="Map tiles by Stamen Design, under CC BY 3.0. Data © OpenStreetMap contributors",
    ).add_to(fmap)

    # CartoDB Positron / Dark Matter via explicit tile URLs + attribution
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        name="CartoDB Positron",
        attr="© OpenStreetMap contributors, © CARTO",
    ).add_to(fmap)

    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        name="CartoDB Dark Matter",
        attr="© OpenStreetMap contributors, © CARTO",
    ).add_to(fmap)

    fmap.get_root().html.add_child(_title_element(title))

    # Decide grouping mode
    use_band_layers = bool(layers_by_band)
    use_mode_layers = bool(layers_by_mode and not layers_by_band)

    band_groups: Dict[str, folium.FeatureGroup] = {}
    mode_groups: Dict[str, folium.FeatureGroup] = {}

    if use_band_layers:
        for _, _, rec in points:
            band = (rec.get("BAND") or "").strip().upper() or "OTHER"
            if band not in band_groups:
                grp = folium.FeatureGroup(name=f"Band: {band}")
                grp.add_to(fmap)
                band_groups[band] = grp

    if use_mode_layers:
        for _, _, rec in points:
            mode = (rec.get("MODE") or "").strip().upper() or "OTHER"
            if mode not in mode_groups:
                grp = folium.FeatureGroup(name=f"Mode: {mode}")
                grp.add_to(fmap)
                mode_groups[mode] = grp

    # Base cluster if no layers
    base_cluster: Optional[MarkerCluster] = None
    base_group: Optional[folium.FeatureGroup] = None
    if not use_band_layers and not use_mode_layers:
        if cluster:
            base_cluster = MarkerCluster(name="QSOs")
            fmap.add_child(base_cluster)
        else:
            base_group = folium.FeatureGroup(name="QSOs")
            base_group.add_to(fmap)

    by_band_colors: List[Tuple[str, str]] = []
    by_mode_colors: List[Tuple[str, str]] = []

    # Collect heatmap points
    heat_data_all: List[Tuple[float, float]] = []
    heat_by_band: Dict[str, List[Tuple[float, float]]] = {}
    heat_by_mode: Dict[str, List[Tuple[float, float]]] = {}

    # Plot points
    for lat, lon, rec in points:
        band = (rec.get("BAND") or "").strip().upper()
        mode = (rec.get("MODE") or "").strip().upper()

        # Determine color
        color_band = BAND_COLORS.get(band, DEFAULT_COLOR)
        color_mode = MODE_COLORS.get(mode, DEFAULT_COLOR)

        # If using band layers, color by mode for extra info; else color by band
        color = color_mode if use_band_layers else color_band
        if use_mode_layers:
            color = color_mode

        if band:
            pair = (band, color_band)
            if pair not in by_band_colors:
                by_band_colors.append(pair)
        if mode:
            pair = (mode, color_mode)
            if pair not in by_mode_colors:
                by_mode_colors.append(pair)

        popup = folium.Popup(format_popup(rec), max_width=350)
        tooltip = rec.get("CALL", "QSO")

        # Choose parent layer
        parent = None
        if use_band_layers:
            parent = band_groups.get(band or "OTHER")
        elif use_mode_layers:
            parent = mode_groups.get(mode or "OTHER")

        marker = folium.Marker(
            location=(lat, lon),
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color=color, icon="signal"),
        )

        if parent is not None:
            if cluster:
                # cluster within each layer
                # (create one cluster per layer lazily)
                if not hasattr(parent, "_cluster"):
                    parent._cluster = MarkerCluster(
                        name=f"Cluster: {parent.layer_name}"
                    )
                    parent._cluster.add_to(parent)  # type: ignore[attr-defined]
                marker.add_to(parent._cluster)  # type: ignore[attr-defined]
            else:
                marker.add_to(parent)
        else:
            if base_cluster is not None:
                marker.add_to(base_cluster)
            elif base_group is not None:
                marker.add_to(base_group)

        # Heatmap collections
        heat_data_all.append((lat, lon))
        heat_by_band.setdefault(band or "OTHER", []).append((lat, lon))
        heat_by_mode.setdefault(mode or "OTHER", []).append((lat, lon))

    # Polyline
    if connect and len(points) >= 2:
        folium.PolyLine([(p[0], p[1]) for p in points], weight=2, opacity=0.7).add_to(
            fmap
        )

    # Home marker
    if home_latlon:
        hl, ho = home_latlon
        folium.Marker(
            location=(hl, ho),
            tooltip="Home QTH",
            popup="Home QTH",
            icon=folium.Icon(icon="home", color="red"),
        ).add_to(fmap)

    # Fit bounds
    bounds_pts = [(p[0], p[1]) for p in points]
    if home_latlon:
        bounds_pts.append(home_latlon)
    if bounds_pts:
        fmap.fit_bounds(bounds_pts, padding=(25, 25))

    # Heatmaps
    if heatmap and heat_data_all:
        HeatMap(
            heat_data_all,
            radius=15,
            blur=25,
            min_opacity=0.2,
            name="Heatmap (All)",
            control=True,
        ).add_to(fmap)

    if heatmap_by_band and heat_by_band:
        for b, pts in heat_by_band.items():
            layer = band_groups.get(b) if use_band_layers else None
            if layer is None:
                layer = folium.FeatureGroup(name=f"Heatmap: {b}")
                layer.add_to(fmap)
            HeatMap(
                pts,
                radius=15,
                blur=25,
                min_opacity=0.2,
                name=f"Heatmap: {b}",
                control=True,
            ).add_to(layer)

    if heatmap_by_mode and heat_by_mode:
        for m, pts in heat_by_mode.items():
            layer = mode_groups.get(m) if use_mode_layers else None
            if layer is None:
                layer = folium.FeatureGroup(name=f"Heatmap: {m}")
                layer.add_to(fmap)
            HeatMap(
                pts,
                radius=15,
                blur=25,
                min_opacity=0.2,
                name=f"Heatmap: {m}",
                control=True,
            ).add_to(layer)

    # Legends
    if use_band_layers:
        fmap.get_root().html.add_child(_legend_element(by_mode_colors, "Modes"))
    elif use_mode_layers:
        fmap.get_root().html.add_child(_legend_element(by_mode_colors, "Modes"))
    else:
        fmap.get_root().html.add_child(_legend_element(by_band_colors, "Bands"))

    # Stats panel
    fmap.get_root().html.add_child(_stats_panel([rec for _, _, rec in points]))

    # Time slider (TimestampedGeoJson)
    if time_slider and points:
        features = []
        for lat, lon, rec in points:
            d = (rec.get("QSO_DATE") or "").strip()
            t = (rec.get("TIME_ON") or "").strip()
            if len(d) == 8:
                y, m, day = d[:4], d[4:6], d[6:8]
                hh = t[:2] if len(t) >= 2 else "00"
                mm = t[2:4] if len(t) >= 4 else "00"
                ss = t[4:6] if len(t) >= 6 else "00"
                stamp = f"{y}-{m}-{day}T{hh}:{mm}:{ss}Z"
                props = {"time": stamp, "popup": format_popup(rec)}
                features.append(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat],
                        },
                        "properties": props,
                    }
                )
        if features:
            TimestampedGeoJson(
                {"type": "FeatureCollection", "features": features},
                period="PT1M",
                add_last_point=True,
                auto_play=False,
                loop=False,
                max_speed=10,
                loop_button=True,
                date_options="YYYY-MM-DD HH:mm:ss",
                time_slider_drag_update=True,
                duration="PT1S",
            ).add_to(fmap)

    # Layer control
    folium.LayerControl(collapsed=False).add_to(fmap)

    # Exports
    if export_csv:
        _export_csv(export_csv, [rec for _, _, rec in points])
    if export_geojson:
        _export_geojson(export_geojson, [(lat, lon, rec) for lat, lon, rec in points])

    fmap.save(out_path)

    print(
        "Saved map with "
        f"{len(points)} QSOs to {out_path}. "
        f"Skipped {skipped} record(s) without coordinates."
    )


# ------------------------------- Exports ------------------------------


def _export_csv(path: str, entries: Iterable[Dict[str, str]]) -> None:
    keys = set()
    rows = []
    for e in entries:
        keys.update(e.keys())
        rows.append(e)
    fieldnames = sorted(keys)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def _export_geojson(
    path: str, points: Iterable[Tuple[float, float, Dict[str, str]]]
) -> None:
    feats = []
    for lat, lon, rec in points:
        feats.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": rec,
            }
        )
    data = {"type": "FeatureCollection", "features": feats}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
