from __future__ import annotations

import argparse
from typing import Optional, Tuple

from .adif import parse_adif
from .maidenhead import maidenhead_to_latlon
from .map_builder import build_map


def _build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Plot ADIF (.adi) QSO locations on an interactive map, colored by "
            "band or mode; optional per-band/mode layers, heatmaps, time "
            "slider, exports, and clustering control."
        )
    )
    parser.add_argument("adi", help="Path to ADI/ADIF file")
    parser.add_argument(
        "--out",
        default="adi_map.html",
        help="Output HTML path (default: adi_map.html)",
    )
    parser.add_argument("--title", default="ADIF QSO Map", help="Map title")
    parser.add_argument(
        "--connect",
        action="store_true",
        help="Draw a line connecting QSOs in file order",
    )
    parser.add_argument(
        "--home-grid",
        help="Home QTH Maidenhead grid (e.g., FN20)",
    )
    parser.add_argument(
        "--home-lat", type=float, help="Home QTH latitude (decimal degrees)"
    )
    parser.add_argument(
        "--home-lon", type=float, help="Home QTH longitude (decimal degrees)"
    )

    # Layers and colors
    parser.add_argument(
        "--layers-by-band",
        action="store_true",
        help=(
            "Create a FeatureGroup per BAND; if set, markers are colored by MODE "
            "and a mode legend is shown."
        ),
    )
    parser.add_argument(
        "--layers-by-mode",
        action="store_true",
        help=(
            "Create a FeatureGroup per MODE and color by MODE. Ignored if "
            "--layers-by-band is also set (band takes precedence)."
        ),
    )

    # Heatmaps
    parser.add_argument("--heatmap", action="store_true", help="Add global heatmap")
    parser.add_argument(
        "--heatmap-by-band",
        action="store_true",
        help="Add a heatmap layer per band",
    )
    parser.add_argument(
        "--heatmap-by-mode",
        action="store_true",
        help="Add a heatmap layer per mode",
    )

    # Clustering
    parser.add_argument(
        "--no-cluster",
        action="store_true",
        help="Disable marker clustering",
    )

    # Exports
    parser.add_argument("--export-csv", help="Write CSV of plotted QSOs")
    parser.add_argument("--export-geojson", help="Write GeoJSON of plotted QSOs")

    # Time
    parser.add_argument(
        "--time-slider",
        action="store_true",
        help="Add a TimestampedGeoJson time slider based on QSO date/time",
    )

    return parser.parse_args()


def main() -> None:
    args = _build_args()

    with open(args.adi, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    records = parse_adif(content)

    home_latlon: Optional[Tuple[float, float]] = None
    if args.home_grid:
        home_latlon = maidenhead_to_latlon(args.home_grid)
        if not home_latlon:
            raise SystemExit(f"Could not parse home grid: {args.home_grid}")
    elif args.home_lat is not None and args.home_lon is not None:
        home_latlon = (args.home_lat, args.home_lon)
        if not (-90 <= home_latlon[0] <= 90 and -180 <= home_latlon[1] <= 180):
            raise SystemExit("Home lat/lon out of range.")

    build_map(
        records,
        out_path=args.out,
        title=args.title,
        connect=args.connect,
        home_latlon=home_latlon,
        layers_by_band=args.layers_by_band,
        layers_by_mode=args.layers_by_mode,
        heatmap=args.heatmap,
        heatmap_by_band=args.heatmap_by_band,
        heatmap_by_mode=args.heatmap_by_mode,
        cluster=not args.no_cluster,
        export_csv=args.export_csv,
        export_geojson=args.export_geojson,
        time_slider=args.time_slider,
    )
