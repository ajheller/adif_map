from __future__ import annotations

from typing import Dict, Optional

# Minimal, pragmatic prefix → country map.
# For serious DXCC accuracy, replace or extend with a robust dataset.
PREFIX_COUNTRY: Dict[str, str] = {
    # North America
    "K": "United States",
    "N": "United States",
    "W": "United States",
    "AA": "United States",
    "AB": "United States",
    "AC": "United States",
    "AD": "United States",
    "AE": "United States",
    "AF": "United States",
    "AG": "United States",
    "AI": "United States",
    "AJ": "United States",
    "AK": "United States",
    "AL": "United States",
    "VE": "Canada",
    "VA": "Canada",
    "VO": "Canada",
    "VY": "Canada",
    "XE": "Mexico",
    # Europe
    "G": "England",
    "M": "England",
    "GM": "Scotland",
    "GW": "Wales",
    "GI": "Northern Ireland",
    "GD": "Isle of Man",
    "GU": "Guernsey",
    "GJ": "Jersey",
    "DL": "Germany",
    "F": "France",
    "I": "Italy",
    "EA": "Spain",
    "CT": "Portugal",
    "OH": "Finland",
    "SM": "Sweden",
    "LA": "Norway",
    "OZ": "Denmark",
    "ON": "Belgium",
    "PA": "Netherlands",
    "OE": "Austria",
    "OK": "Czech Republic",
    "OM": "Slovak Republic",
    "SP": "Poland",
    "YU": "Serbia",
    "S5": "Slovenia",
    "9A": "Croatia",
    "HA": "Hungary",
    "YO": "Romania",
    "LZ": "Bulgaria",
    "SV": "Greece",
    # Asia / Pacific
    "JA": "Japan",
    "7J": "Japan",
    "7K": "Japan",
    "7M": "Japan",
    "VK": "Australia",
    "ZL": "New Zealand",
    "BY": "China",
    "VR": "Hong Kong",
    "HL": "Korea",
    "BV": "Taiwan",
    "9V": "Singapore",
    "VU": "India",
    "HS": "Thailand",
    # South America
    "PY": "Brazil",
    "LU": "Argentina",
    "CX": "Uruguay",
    "CE": "Chile",
    # Africa / Middle East
    "ZS": "South Africa",
    "SU": "Egypt",
    "A4": "Oman",
    "A6": "UAE",
}


def lookup_country(callsign: Optional[str]) -> Optional[str]:
    """Best-effort callsign → country lookup using prefix heuristics.

    Strategy: match the longest prefix from PREFIX_COUNTRY.
    """
    if not callsign:
        return None
    cs = callsign.strip().upper()
    best = None
    for pref, name in PREFIX_COUNTRY.items():
        if cs.startswith(pref) and (best is None or len(pref) > len(best[0])):
            best = (pref, name)
    return best[1] if best else None
