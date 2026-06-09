"""Geo distance penalty constants and country/continent mappings.

Used by proximity scoring to prefer peers in the same country/continent.
"""

# Geo distance penalties (lower = better)
GEO_SAME_COUNTRY = 0.0
GEO_ADJACENT = 15.0
GEO_SAME_CONTINENT = 35.0
GEO_DIFFERENT_CONTINENT = 60.0
GEO_UNKNOWN = 45.0

# Continent codes
CONTINENT_AF = "AF"  # Africa
CONTINENT_AS = "AS"  # Asia
CONTINENT_EU = "EU"  # Europe
CONTINENT_NA = "NA"  # North America
CONTINENT_SA = "SA"  # South America
CONTINENT_OC = "OC"  # Oceania
CONTINENT_AN = "AN"  # Antarctica

# Country ISO code -> Continent mapping
COUNTRY_CONTINENT: dict[str, str] = {
    # Europe
    "AL": CONTINENT_EU, "AD": CONTINENT_EU, "AT": CONTINENT_EU,
    "BE": CONTINENT_EU, "BG": CONTINENT_EU, "HR": CONTINENT_EU,
    "CY": CONTINENT_EU, "CZ": CONTINENT_EU, "DK": CONTINENT_EU,
    "EE": CONTINENT_EU, "FI": CONTINENT_EU, "FR": CONTINENT_EU,
    "DE": CONTINENT_EU, "GR": CONTINENT_EU, "HU": CONTINENT_EU,
    "IE": CONTINENT_EU, "IT": CONTINENT_EU, "LV": CONTINENT_EU,
    "LT": CONTINENT_EU, "LU": CONTINENT_EU, "MT": CONTINENT_EU,
    "MD": CONTINENT_EU, "MC": CONTINENT_EU, "ME": CONTINENT_EU,
    "NL": CONTINENT_EU, "MK": CONTINENT_EU, "NO": CONTINENT_EU,
    "PL": CONTINENT_EU, "PT": CONTINENT_EU, "RO": CONTINENT_EU,
    "RU": CONTINENT_EU, "SM": CONTINENT_EU, "RS": CONTINENT_EU,
    "SK": CONTINENT_EU, "SI": CONTINENT_EU, "ES": CONTINENT_EU,
    "SE": CONTINENT_EU, "CH": CONTINENT_EU, "TR": CONTINENT_EU,
    "UA": CONTINENT_EU, "GB": CONTINENT_EU, "IS": CONTINENT_EU,
    "BA": CONTINENT_EU, "XK": CONTINENT_EU,
    # Asia
    "AF": CONTINENT_AS, "AM": CONTINENT_AS, "AZ": CONTINENT_AS,
    "BH": CONTINENT_AS, "BD": CONTINENT_AS, "BT": CONTINENT_AS,
    "BN": CONTINENT_AS, "MM": CONTINENT_AS, "KP": CONTINENT_AS,
    "KH": CONTINENT_AS, "CN": CONTINENT_AS, "GE": CONTINENT_AS,
    "IN": CONTINENT_AS, "ID": CONTINENT_AS, "IR": CONTINENT_AS,
    "IQ": CONTINENT_AS, "IL": CONTINENT_AS, "JP": CONTINENT_AS,
    "JO": CONTINENT_AS, "KZ": CONTINENT_AS, "KW": CONTINENT_AS,
    "KG": CONTINENT_AS, "LA": CONTINENT_AS, "LB": CONTINENT_AS,
    "MY": CONTINENT_AS, "MV": CONTINENT_AS, "MN": CONTINENT_AS,
    "OM": CONTINENT_AS, "PK": CONTINENT_AS, "PS": CONTINENT_AS,
    "PH": CONTINENT_AS, "QA": CONTINENT_AS, "SA": CONTINENT_AS,
    "SG": CONTINENT_AS, "KR": CONTINENT_AS, "LK": CONTINENT_AS,
    "SY": CONTINENT_AS, "TW": CONTINENT_AS, "TJ": CONTINENT_AS,
    "TH": CONTINENT_AS, "TL": CONTINENT_AS, "AE": CONTINENT_AS,
    "UZ": CONTINENT_AS, "VN": CONTINENT_AS, "YE": CONTINENT_AS,
    # North America
    "AG": CONTINENT_NA, "BS": CONTINENT_NA, "BB": CONTINENT_NA,
    "BZ": CONTINENT_NA, "BM": CONTINENT_NA, "CA": CONTINENT_NA,
    "CR": CONTINENT_NA, "CU": CONTINENT_NA, "DM": CONTINENT_NA,
    "DO": CONTINENT_NA, "SV": CONTINENT_NA, "GD": CONTINENT_NA,
    "GT": CONTINENT_NA, "HT": CONTINENT_NA, "HN": CONTINENT_NA,
    "JM": CONTINENT_NA, "MX": CONTINENT_NA, "NI": CONTINENT_NA,
    "PA": CONTINENT_NA, "KN": CONTINENT_NA, "LC": CONTINENT_NA,
    "VC": CONTINENT_NA, "TT": CONTINENT_NA, "US": CONTINENT_NA,
    # South America
    "AR": CONTINENT_SA, "BO": CONTINENT_SA, "BR": CONTINENT_SA,
    "CL": CONTINENT_SA, "CO": CONTINENT_SA, "EC": CONTINENT_SA,
    "GY": CONTINENT_SA, "PY": CONTINENT_SA, "PE": CONTINENT_SA,
    "SR": CONTINENT_SA, "UY": CONTINENT_SA, "VE": CONTINENT_SA,
    # Africa
    "DZ": CONTINENT_AF, "AO": CONTINENT_AF, "BJ": CONTINENT_AF,
    "BW": CONTINENT_AF, "BF": CONTINENT_AF, "BI": CONTINENT_AF,
    "CM": CONTINENT_AF, "CV": CONTINENT_AF, "CF": CONTINENT_AF,
    "TD": CONTINENT_AF, "KM": CONTINENT_AF, "CG": CONTINENT_AF,
    "CD": CONTINENT_AF, "DJ": CONTINENT_AF, "EG": CONTINENT_AF,
    "GQ": CONTINENT_AF, "ER": CONTINENT_AF, "SZ": CONTINENT_AF,
    "ET": CONTINENT_AF, "GA": CONTINENT_AF, "GM": CONTINENT_AF,
    "GH": CONTINENT_AF, "GN": CONTINENT_AF, "GW": CONTINENT_AF,
    "CI": CONTINENT_AF, "KE": CONTINENT_AF, "LS": CONTINENT_AF,
    "LR": CONTINENT_AF, "LY": CONTINENT_AF, "MG": CONTINENT_AF,
    "MW": CONTINENT_AF, "ML": CONTINENT_AF, "MA": CONTINENT_AF,
    "MU": CONTINENT_AF, "MR": CONTINENT_AF, "MZ": CONTINENT_AF,
    "NA": CONTINENT_AF, "NE": CONTINENT_AF, "NG": CONTINENT_AF,
    "RW": CONTINENT_AF, "ST": CONTINENT_AF, "SN": CONTINENT_AF,
    "SC": CONTINENT_AF, "SL": CONTINENT_AF, "SO": CONTINENT_AF,
    "SS": CONTINENT_AF, "SD": CONTINENT_AF, "TZ": CONTINENT_AF,
    "TG": CONTINENT_AF, "TN": CONTINENT_AF, "UG": CONTINENT_AF,
    "ZM": CONTINENT_AF, "ZW": CONTINENT_AF,
    # Oceania
    "AU": CONTINENT_OC, "FJ": CONTINENT_OC, "KI": CONTINENT_OC,
    "MH": CONTINENT_OC, "FM": CONTINENT_OC, "NZ": CONTINENT_OC,
    "NR": CONTINENT_OC, "PW": CONTINENT_OC, "PG": CONTINENT_OC,
    "WS": CONTINENT_OC, "SB": CONTINENT_OC, "TO": CONTINENT_OC,
    "TV": CONTINENT_OC, "VU": CONTINENT_OC,
}

# Country adjacency map (simplified - neighboring countries)
COUNTRY_ADJACENCY: dict[str, set[str]] = {
    # Europe adjacencies
    "DE": {"FR", "NL", "BE", "LU", "CH", "AT", "CZ", "PL", "DK"},
    "FR": {"DE", "BE", "LU", "CH", "IT", "ES", "PT"},
    "IT": {"FR", "CH", "AT", "SI"},
    "ES": {"FR", "PT"},
    "GB": {"FR"},  # Channel
    "PL": {"DE", "CZ", "SK", "UA", "BY", "LT", "RU"},
    "UA": {"PL", "RO", "HU", "SK", "BY", "RU"},
    "RU": {"NO", "FI", "EE", "LV", "LT", "BY", "UA", "GE", "CN", "Mn", "KZ", "KP"},
    "CN": {"RU", "Mn", "KP", "VN", "LA", "MM", "NP", "BT", "IN", "PK", "AF", "KZ"},
    "IN": {"NP", "BT", "BD", "MM", "PK", "CN"},
    "BR": {"AR", "UY", "PY", "BO", "PE", "CO", "VE", "GY", "SR"},
    "AR": {"BO", "CH", "PY", "UY", "BR"},
    "US": {"CA", "MX"},
    "CA": {"US"},
    "MX": {"US", "GT", "BZ"},
    "JP": {},
    "KR": {"KP"},
    "AU": {},
    "ID": {"MY", "TH", "SG", "TL", "PG"},
    "TR": {"GR", "GE", "AM", "AZ", "IR", "SY", "IQ"},
    "SA": {"IQ", "JO", "YE", "OM", "AE", "KW", "QA", "BH"},
    "EG": {"LY", "SD", "SD"},
    "ZA": {"NA", "BW", "ZM", "MZ", "MZ"},
    "NG": {"BJ", "NE", "TD", "CM"},
    "KE": {"ET", "SO", "DJ", "SS", "SD", "TZ", "UG", "RW", "TZ"},
    "NG": {"BJ", "NE", "TD", "CM"},
    # Add more as needed - this is a simplified adjacency list
}

# Ensure all countries have at least an empty set
for country_code in COUNTRY_CONTINENT:
    COUNTRY_ADJACENCY.setdefault(country_code, set())
