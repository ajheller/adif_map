from __future__ import annotations


def maidenhead_to_latlon(grid: str) -> tuple[float, float] | None:
    """Convert Maidenhead grid (e.g. FN20, JN58TD) → (lat, lon) cell center.

    Supports 2-8 chars. Returns ``None`` on invalid input.
    """
    if not grid:
        return None

    g = grid.strip().upper()
    if len(g) < 2:
        return None

    try:
        lon = (ord(g[0]) - ord("A")) * 20 - 180
        lat = (ord(g[1]) - ord("A")) * 10 - 90
    except Exception:
        return None

    if len(g) >= 4 and g[2:4].isdigit():
        lon += int(g[2]) * 2
        lat += int(g[3]) * 1
    elif len(g) >= 3:
        return None

    if len(g) >= 6 and g[4].isalpha() and g[5].isalpha():
        lon += (ord(g[4]) - ord("A")) * (2 / 24)
        lat += (ord(g[5]) - ord("A")) * (1 / 24)
    elif len(g) == 5:
        return None

    if len(g) >= 8 and g[6:8].isdigit():
        lon += int(g[6]) * (2 / 240)
        lat += int(g[7]) * (1 / 240)
    elif len(g) == 7:
        return None

    cell_lon = 20.0
    cell_lat = 10.0
    if len(g) >= 4:
        cell_lon = 2.0
        cell_lat = 1.0
    if len(g) >= 6:
        cell_lon = 2.0 / 24.0
        cell_lat = 1.0 / 24.0
    if len(g) >= 8:
        cell_lon = 2.0 / 240.0
        cell_lat = 1.0 / 240.0

    return (lat + cell_lat / 2.0, lon + cell_lon / 2.0)
