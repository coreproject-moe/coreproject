# Continent membership: ISO 3166-1 alpha-2 -> continent code
# 249 recognized codes (countries, territories, and special areas)
# Each code appears exactly once; last-assignment wins in Python dicts.

COUNTRY_CONTINENT: dict[str, str] = {
    # ═══════════════════════════════════════════════════════════
    # AFRICA (58)
    # ═══════════════════════════════════════════════════════════
    "DZ": "AF",  # Algeria
    "AO": "AF",  # Angola
    "BJ": "AF",  # Benin
    "BW": "AF",  # Botswana
    "BF": "AF",  # Burkina Faso
    "BI": "AF",  # Burundi
    "CV": "AF",  # Cabo Verde
    "CM": "AF",  # Cameroon
    "CF": "AF",  # Central African Republic
    "TD": "AF",  # Chad
    "KM": "AF",  # Comoros
    "CG": "AF",  # Congo (Republic)
    "CD": "AF",  # Congo (DRC)
    "CI": "AF",  # Cote d'Ivoire
    "DJ": "AF",  # Djibouti
    "EG": "AF",  # Egypt
    "GQ": "AF",  # Equatorial Guinea
    "ER": "AF",  # Eritrea
    "SZ": "AF",  # Eswatini
    "ET": "AF",  # Ethiopia
    "GA": "AF",  # Gabon
    "GM": "AF",  # Gambia
    "GH": "AF",  # Ghana
    "GN": "AF",  # Guinea
    "GW": "AF",  # Guinea-Bissau
    "KE": "AF",  # Kenya
    "LS": "AF",  # Lesotho
    "LR": "AF",  # Liberia
    "LY": "AF",  # Libya
    "MG": "AF",  # Madagascar
    "MW": "AF",  # Malawi
    "ML": "AF",  # Mali
    "MR": "AF",  # Mauritania
    "MU": "AF",  # Mauritius
    "YT": "AF",  # Mayotte
    "MA": "AF",  # Morocco
    "MZ": "AF",  # Mozambique
    "NA": "AF",  # Namibia
    "NE": "AF",  # Niger
    "NG": "AF",  # Nigeria
    "RE": "AF",  # Reunion
    "RW": "AF",  # Rwanda
    "ST": "AF",  # Sao Tome and Principe
    "SN": "AF",  # Senegal
    "SC": "AF",  # Seychelles
    "SL": "AF",  # Sierra Leone
    "SO": "AF",  # Somalia
    "SD": "AF",  # Sudan
    "SS": "AF",  # South Sudan
    "TZ": "AF",  # Tanzania
    "TG": "AF",  # Togo
    "TN": "AF",  # Tunisia
    "UG": "AF",  # Uganda
    "EH": "AF",  # Western Sahara
    "ZA": "AF",  # South Africa
    "ZM": "AF",  # Zambia
    "ZW": "AF",  # Zimbabwe

    # ═══════════════════════════════════════════════════════════
    # ASIA (48)
    # ═══════════════════════════════════════════════════════════
    "AF": "AS",  # Afghanistan
    "AM": "AS",  # Armenia
    "AZ": "AS",  # Azerbaijan
    "BH": "AS",  # Bahrain
    "BD": "AS",  # Bangladesh
    "BT": "AS",  # Bhutan
    "BN": "AS",  # Brunei
    "GE": "AS",  # Georgia
    "HK": "AS",  # Hong Kong
    "IN": "AS",  # India
    "CN": "AS",  # China
    "ID": "AS",  # Indonesia
    "IR": "AS",  # Iran
    "IQ": "AS",  # Iraq
    "IL": "AS",  # Israel
    "JP": "AS",  # Japan
    "JO": "AS",  # Jordan
    "KZ": "AS",  # Kazakhstan
    "KP": "AS",  # North Korea
    "KR": "AS",  # South Korea
    "KW": "AS",  # Kuwait
    "KG": "AS",  # Kyrgyzstan
    "LA": "AS",  # Laos
    "LB": "AS",  # Lebanon
    "MO": "AS",  # Macau
    "MY": "AS",  # Malaysia
    "MV": "AS",  # Maldives
    "MN": "AS",  # Mongolia
    "MM": "AS",  # Myanmar
    "NP": "AS",  # Nepal
    "OM": "AS",  # Oman
    "PK": "AS",  # Pakistan
    "PS": "AS",  # Palestine
    "PH": "AS",  # Philippines
    "QA": "AS",  # Qatar
    "SA": "AS",  # Saudi Arabia
    "SG": "AS",  # Singapore
    "KH": "AS",  # Cambodia
    "LK": "AS",  # Sri Lanka
    "SY": "AS",  # Syria
    "TW": "AS",  # Taiwan
    "TJ": "AS",  # Tajikistan
    "TM": "AS",  # Turkmenistan
    "TH": "AS",  # Thailand
    "TL": "AS",  # Timor-Leste
    "AE": "AS",  # United Arab Emirates
    "UZ": "AS",  # Uzbekistan
    "VN": "AS",  # Vietnam
    "YE": "AS",  # Yemen

    # ═══════════════════════════════════════════════════════════
    # NORTH AMERICA + CARIBBEAN (37)
    # ═══════════════════════════════════════════════════════════
    "US": "NA",  # United States
    "CA": "NA",  # Canada
    "MX": "NA",  # Mexico
    "GT": "NA",  # Guatemala
    "BZ": "NA",  # Belize
    "SV": "NA",  # El Salvador
    "HN": "NA",  # Honduras
    "NI": "NA",  # Nicaragua
    "CR": "NA",  # Costa Rica
    "PA": "NA",  # Panama
    "CU": "NA",  # Cuba
    "HT": "NA",  # Haiti
    "DO": "NA",  # Dominican Republic
    "JM": "NA",  # Jamaica
    "TT": "NA",  # Trinidad and Tobago
    "BS": "NA",  # Bahamas
    "BB": "NA",  # Barbados
    "GD": "NA",  # Grenada
    "LC": "NA",  # Saint Lucia
    "VC": "NA",  # Saint Vincent and the Grenadines
    "AG": "NA",  # Antigua and Barbuda
    "DM": "NA",  # Dominica
    "KN": "NA",  # Saint Kitts and Nevis
    "PR": "NA",  # Puerto Rico
    "AI": "NA",  # Anguilla
    "AW": "NA",  # Aruba
    "BM": "NA",  # Bermuda
    "BQ": "NA",  # Bonaire, Sint Eustatius and Saba
    "KY": "NA",  # Cayman Islands
    "CW": "NA",  # Curacao
    "GL": "NA",  # Greenland
    "GP": "NA",  # Guadeloupe
    "MQ": "NA",  # Martinique
    "MS": "NA",  # Montserrat
    "MP": "NA",  # Northern Mariana Islands
    "SX": "NA",  # Sint Maarten
    "TC": "NA",  # Turks and Caicos Islands
    "VG": "NA",  # British Virgin Islands
    "VI": "NA",  # U.S. Virgin Islands

    # ═══════════════════════════════════════════════════════════
    # SOUTH AMERICA (13)
    # ═══════════════════════════════════════════════════════════
    "AR": "SA",  # Argentina
    "BO": "SA",  # Bolivia
    "BR": "SA",  # Brazil
    "CL": "SA",  # Chile
    "CO": "SA",  # Colombia
    "EC": "SA",  # Ecuador
    "GF": "SA",  # French Guiana
    "GY": "SA",  # Guyana
    "PY": "SA",  # Paraguay
    "PE": "SA",  # Peru
    "SR": "SA",  # Suriname
    "UY": "SA",  # Uruguay
    "VE": "SA",  # Venezuela

    # ═══════════════════════════════════════════════════════════
    # EUROPE (57)
    # ═══════════════════════════════════════════════════════════
    "AL": "EU",  # Albania
    "AD": "EU",  # Andorra
    "AT": "EU",  # Austria
    "BY": "EU",  # Belarus
    "BE": "EU",  # Belgium
    "BA": "EU",  # Bosnia and Herzegovina
    "BG": "EU",  # Bulgaria
    "HR": "EU",  # Croatia
    "CY": "EU",  # Cyprus
    "CZ": "EU",  # Czech Republic
    "DK": "EU",  # Denmark
    "EE": "EU",  # Estonia
    "FO": "EU",  # Faroe Islands
    "FI": "EU",  # Finland
    "FR": "EU",  # France
    "DE": "EU",  # Germany
    "GR": "EU",  # Greece
    "GG": "EU",  # Guernsey
    "HU": "EU",  # Hungary
    "IE": "EU",  # Ireland
    "IM": "EU",  # Isle of Man
    "IS": "EU",  # Iceland
    "IT": "EU",  # Italy
    "JE": "EU",  # Jersey
    "XK": "EU",  # Kosovo
    "LV": "EU",  # Latvia
    "LI": "EU",  # Liechtenstein
    "LT": "EU",  # Lithuania
    "LU": "EU",  # Luxembourg
    "MK": "EU",  # North Macedonia
    "MT": "EU",  # Malta
    "MD": "EU",  # Moldova
    "MC": "EU",  # Monaco
    "ME": "EU",  # Montenegro
    "NL": "EU",  # Netherlands
    "NO": "EU",  # Norway
    "PL": "EU",  # Poland
    "PT": "EU",  # Portugal
    "RO": "EU",  # Romania
    "RU": "EU",  # Russia
    "SM": "EU",  # San Marino
    "RS": "EU",  # Serbia
    "SK": "EU",  # Slovakia
    "SI": "EU",  # Slovenia
    "ES": "EU",  # Spain
    "SJ": "EU",  # Svalbard and Jan Mayen
    "SE": "EU",  # Sweden
    "CH": "EU",  # Switzerland
    "TR": "EU",  # Turkey
    "UA": "EU",  # Ukraine
    "GB": "EU",  # United Kingdom
    "VA": "EU",  # Vatican City
    "AX": "EU",  # Aland Islands
    "BL": "EU",  # Saint Barthelemy
    "MF": "EU",  # Saint Martin

    # ═══════════════════════════════════════════════════════════
    # OCEANIA (27)
    # ═══════════════════════════════════════════════════════════
    "AS": "OC",  # American Samoa
    "AU": "OC",  # Australia
    "CK": "OC",  # Cook Islands
    "FJ": "OC",  # Fiji
    "PF": "OC",  # French Polynesia
    "GU": "OC",  # Guam
    "KI": "OC",  # Kiribati
    "MH": "OC",  # Marshall Islands
    "FM": "OC",  # Micronesia
    "NR": "OC",  # Nauru
    "NU": "OC",  # Niue
    "NF": "OC",  # Norfolk Island
    "NZ": "OC",  # New Zealand
    "NC": "OC",  # New Caledonia
    "PW": "OC",  # Palau
    "PG": "OC",  # Papua New Guinea
    "PN": "OC",  # Pitcairn
    "WS": "OC",  # Samoa
    "SB": "OC",  # Solomon Islands
    "TK": "OC",  # Tokelau
    "TO": "OC",  # Tonga
    "TV": "OC",  # Tuvalu
    "UM": "OC",  # U.S. Minor Outlying Islands
    "VU": "OC",  # Vanuatu
    "WF": "OC",  # Wallis and Futuna
    "FK": "SA",  # Falkland Islands (South America geographically)

    # ═══════════════════════════════════════════════════════════
    # ANTARCTICA (3)
    # ═══════════════════════════════════════════════════════════
    "AQ": "AN",  # Antarctica
    "TF": "AN",  # French Southern Territories
    "HM": "AN",  # Heard Island and McDonald Islands
}

# ── Adjacent countries ────────────────────────────────────────────────
# Share a land border or are very close by sea (<=300km).
# If a country is missing here, geo fallback (same-continent) applies.

COUNTRY_ADJACENCY: dict[str, set[str]] = {
    # ── AFRICA ──────────────────────────────────────────────────
    "DZ": {"TN", "LY", "EH", "MR", "ML", "NE"},
    "AO": {"CG", "CD", "ZM", "NA"},
    "BJ": {"TG", "BF", "NE"},
    "BW": {"ZA", "NA", "ZM", "TZ"},
    "BF": {"ML", "GH", "TG", "BJ", "NE"},
    "BI": {"CD", "RW", "TZ"},
    "CV": set(),
    "CM": {"CF", "TD", "NG", "GQ", "GA"},
    "CF": {"TD", "CM", "CG", "CD", "UG", "SS"},
    "TD": {"LY", "NE", "NG", "CM", "CF", "SS", "SD", "ER"},
    "KM": {"MG", "MU"},
    "CG": {"GA", "GQ", "CD", "AO", "CF"},
    "CD": {"AO", "CG", "CF", "SS", "UG", "RW", "BI", "TZ", "MW", "ZM", "MZ"},
    "CI": {"GN", "LR", "ML", "BF", "GH"},
    "DJ": {"ET", "ER", "SO"},
    "EG": {"LY", "SD", "ER"},
    "GQ": {"CG", "GA"},
    "ER": {"SD", "ET", "DJ", "SO"},
    "SZ": {"ZA", "MZ"},
    "ET": {"SD", "SS", "DJ", "ER", "SO", "KE"},
    "GA": {"GQ", "CG", "CD"},
    "GM": {"SN"},
    "GH": {"TG", "BF", "CI"},
    "GN": {"ML", "CI", "LR", "SL", "MR", "GW"},
    "GW": {"GN", "SL"},
    "KE": {"ET", "SO", "SS", "UG", "TZ"},
    "LS": {"ZA"},
    "LR": {"GN", "CI", "SL"},
    "LY": {"DZ", "TD", "SD", "EG", "TN"},
    "MG": {"MU", "KM", "SC"},
    "MW": {"TZ", "MZ", "ZM", "CD", "MZ"},
    "ML": {"DZ", "NE", "BJ", "BF", "CI", "GN", "MR"},
    "MR": {"DZ", "ML", "SN", "GN", "EH"},
    "MU": {"SC", "YT", "RE"},
    "YT": {"MU", "MG"},
    "MA": {"DZ", "EH"},
    "MZ": {"CD", "ZM", "MW", "TZ", "ZA", "MW"},
    "NA": {"AO", "ZM", "BW", "ZA"},
    "NE": {"DZ", "LY", "TD", "NG", "BJ", "BF", "ML"},
    "NG": {"NE", "TD", "CM", "BJ"},
    "RE": {"MU", "YT"},
    "RW": {"CD", "BI", "TZ", "UG"},
    "ST": set(),
    "SN": {"GN", "GM", "ML", "MR"},
    "SC": {"MU", "MG"},
    "SL": {"GN", "CI", "LR"},
    "SO": {"DJ", "ET", "KE", "ER"},
    "SD": {"EG", "LY", "TD", "CF", "SS", "ET", "ER"},
    "SS": {"SD", "CF", "UG", "CD", "ET"},
    "TZ": {"UG", "SS", "CD", "RW", "BI", "MZ", "MW", "KE"},
    "TG": {"BJ", "GH", "BF"},
    "TN": {"DZ", "LY"},
    "UG": {"SS", "CD", "RW", "TZ", "KE"},
    "EH": {"DZ", "MR", "MA"},
    "ZM": {"CD", "TZ", "MW", "BW", "ZA", "NA", "AO"},
    "ZA": {"NA", "BW", "ZM", "MZ", "LS"},
    "ZW": {"ZM", "MZ", "BW", "ZA"},

    # ── ASIA ───────────────────────────────────────────────────
    "AF": {"PK", "IR", "TM", "UZ", "TJ", "CN"},
    "AM": {"TR", "GE", "AZ", "IR"},
    "AZ": {"RU", "GE", "AM", "IR", "TR"},
    "BH": {"SA"},
     "BD": {"IN", "MM"},
    "BT": {"IN", "CN"},
    "BN": {"MY"},
    "CN": {"NP", "BT", "IN", "PK", "AF", "TJ", "KG", "KZ", "RU", "MN", "VN", "LA", "MM"},
    "GE": {"RU", "AM", "AZ", "TR"},
    "HK": {"CN"},
    "IN": {"NP", "BT", "BD", "MM", "PK", "LK"},
    "ID": {"MY", "PG", "TL"},
    "IR": {"AF", "PK", "TM", "AM", "AZ", "TR", "IQ"},
    "IQ": {"IR", "TR", "SY", "SA", "KW", "JO"},
    "IL": {"EG", "JO", "SY", "LB"},
    "JP": {"RU"},
    "JO": {"SY", "IQ", "SA", "KW", "IL"},
    "KZ": {"RU", "UZ", "TM", "AF", "CN", "MN"},
    "KP": {"RU", "CN", "KR"},
    "KR": {"KP"},
    "KW": {"SA", "IQ"},
    "KG": {"UZ", "TJ", "AF", "CN"},
    "LA": {"MM", "CN", "VN", "KH", "TH"},
    "LB": {"SY", "IL"},
    "MO": {"CN"},
    "MY": {"TH", "SG", "ID", "BN"},
    "MV": {"IN"},
    "MN": {"RU", "CN"},
    "MM": {"CN", "IN", "BD", "TH", "LA"},
    "NP": {"CN", "IN"},
    "OM": {"SA", "AE", "YE"},
    "PK": {"IN", "AF", "IR", "CN"},
    "PS": {"IL", "JO"},
    "PH": {"VN"},
    "QA": {"SA"},
    "SA": {"IQ", "JO", "KW", "QA", "AE", "OM", "YE", "IR"},
    "SG": {"MY"},
    "KH": {"TH", "LA", "VN"},
    "LK": {"IN"},
    "SY": {"TR", "IL", "JO", "IQ", "IR"},
    "TW": {"JP", "PH"},
    "TJ": {"UZ", "KG", "AF", "CN"},
    "TM": {"UZ", "KZ", "AF", "IR"},
    "TH": {"MM", "LA", "KH", "MY"},
    "TL": {"ID"},
    "AE": {"OM", "SA"},
    "UZ": {"KZ", "TM", "AF", "TJ", "KG"},
    "VN": {"CN", "LA", "KH"},
    "YE": {"SA", "OM"},

    # ── NORTH AMERICA + CARIBBEAN ──────────────────────────────
    "US": {"CA", "MX"},
    "CA": {"US", "GL"},
    "MX": {"US", "GT", "BZ"},
    "GT": {"MX", "BZ", "SV", "HN"},
    "BZ": {"MX", "GT"},
    "SV": {"GT", "HN"},
    "HN": {"GT", "SV", "NI"},
    "NI": {"HN", "CR"},
    "CR": {"NI", "PA"},
    "PA": {"CR", "CO"},
    "CU": {"JM"},
    "HT": {"DO"},
    "DO": {"HT"},
    "JM": {"CU", "HT"},
    "TT": {"GY"},
    "BS": {"CU"},
    "BB": {"TT"},
    "GD": {"VC"},
    "LC": {"VC", "GD"},
    "VC": {"GD", "LC"},
    "AG": {"DM"},
    "DM": {"AG"},
    "KN": {"MS"},
    "PR": {"VG"},
    "AI": {"MS"},
    "AW": {"VE"},
    "BM": set(),
    "BQ": {"CW"},
    "KY": {"CU"},
    "CW": {"AW", "BQ"},
    "GL": {"CA", "IS"},
    "GP": {"MS"},
    "MQ": {"GP"},
    "MS": {"AI", "KN"},
    "MP": {"GU"},
    "SX": {"GP"},
    "TC": {"BS"},
    "VG": {"PR"},
    "VI": {"VG"},

    # ── SOUTH AMERICA ──────────────────────────────────────────
    "AR": {"BO", "CL", "PY", "UY", "BR", "FK"},
    "BO": {"PE", "BR", "PY", "AR", "CL"},
    "BR": {"CO", "VE", "GY", "SR", "GF", "UY", "PY", "AR", "BO", "PE"},
    "CL": {"AR", "BO", "PE"},
    "CO": {"PA", "VE", "BR", "PE", "EC"},
    "EC": {"CO", "PE"},
    "GF": {"BR", "VE", "SR"},
    "GY": {"BR", "CO", "VE"},
    "PY": {"BO", "BR", "AR"},
    "PE": {"CO", "EC", "BO", "BR", "CL"},
    "SR": {"BR", "GY", "GF"},
    "UY": {"BR", "AR"},
    "VE": {"CO", "BR", "GF", "GY"},
    "FK": {"AR"},

    # ── EUROPE ─────────────────────────────────────────────────
    "AL": {"GR", "MK", "RS", "XK"},
    "AD": {"ES", "FR"},
    "AT": {"DE", "CZ", "SK", "HU", "SI", "IT", "CH", "LI"},
    "BY": {"RU", "UA", "PL", "LT", "LV"},
    "BE": {"FR", "LU", "NL", "DE"},
    "BA": {"HR", "RS", "ME"},
    "BG": {"GR", "TR", "RS", "MD", "UA", "RO"},
    "HR": {"SI", "AT", "HU", "RS", "BA"},
    "CY": {"TR"},
    "CZ": {"DE", "PL", "SK", "AT"},
    "DK": {"DE"},
    "EE": {"RU", "LV"},
    "FO": {"IS"},
    "FI": {"SE", "NO", "RU"},
    "FR": {"ES", "AD", "MC", "BE", "LU", "DE", "CH", "IT", "GB"},
    "DE": {"DK", "PL", "CZ", "AT", "CH", "BE", "NL", "LU"},
    "GR": {"AL", "MK", "BG", "TR"},
    "GG": {"FR"},
    "HU": {"AT", "SK", "UA", "RO", "RS", "BA", "HR"},
    "IE": {"GB"},
    "IM": {"GB"},
    "IS": {"GB", "FO", "GL"},
    "IT": {"FR", "CH", "AT", "SI", "SM", "VA"},
    "JE": {"FR"},
    "XK": {"AL", "MK", "RS", "BA"},
    "LV": {"EE", "RU", "BY", "LT"},
    "LI": {"CH", "AT"},
    "LT": {"BY", "RU", "LV", "PL"},
    "LU": {"FR", "BE", "DE"},
    "MK": {"AL", "GR", "BG", "RS", "XK"},
    "MT": {"IT"},
    "MD": {"UA", "RO"},
    "MC": {"FR"},
    "ME": {"AL", "RS", "XK", "BA"},
    "NL": {"BE", "DE"},
    "NO": {"SE", "FI", "RU"},
    "PL": {"DE", "CZ", "SK", "UA", "BY", "LT", "RU"},
    "PT": {"ES"},
    "RO": {"HU", "UA", "MD", "BG", "RS"},
    "RU": {"NO", "FI", "EE", "LV", "LT", "BY", "UA", "GE", "AZ", "KZ", "MN", "CN", "KP"},
    "SM": {"IT"},
    "RS": {"HU", "RO", "BG", "MK", "AL", "XK", "BA", "HR"},
    "SK": {"PL", "CZ", "AT", "HU", "UA"},
    "SI": {"IT", "AT", "HU", "HR"},
    "ES": {"PT", "FR", "AD", "GB"},
    "SJ": {"NO"},
    "SE": {"NO", "FI"},
    "CH": {"FR", "DE", "AT", "IT", "LI"},
    "TR": {"GR", "BG", "GE", "AM", "AZ", "IR", "SY"},
    "UA": {"PL", "SK", "HU", "RO", "BG", "MD", "BY", "RU", "GE"},
    "GB": {"IE", "FR"},
    "VA": {"IT"},
    "AX": {"FI"},
    "BL": {"MF"},
    "MF": {"BL"},

    # ── OCEANIA ────────────────────────────────────────────────
    "AS": {"WS"},
    "AU": {"PG"},
    "CK": {"NZ"},
    "FJ": {"NZ", "PG"},
    "PF": set(),
    "GU": {"MP"},
    "KI": {"FM"},
    "MH": {"FM", "PW"},
    "FM": {"MH", "PW", "GU"},
    "NR": {"KI"},
    "NC": {"AU"},
    "NU": {"WS"},
    "NF": {"AU"},
    "NZ": {"AU", "NC", "FJ"},
    "PW": {"ID", "MH", "FM"},
    "PG": {"ID", "SB"},
    "PN": {"CK"},
    "WS": {"TO", "AS"},
    "SB": {"PG", "VU"},
    "TK": {"NZ"},
    "TO": {"WS", "FJ"},
    "TV": {"KI"},
    "UM": {"KI"},
    "VU": {"SB", "NC"},
    "WF": {"NC"},

    # ── ANTARCTICA ─────────────────────────────────────────────
    "AQ": {"AU", "NZ"},
    "TF": {"AQ"},
    "HM": {"AQ"},
}

# ── Geo distance penalties ────────────────────────────────────────────
# Added to peer base score. Lower = closer = higher priority.

GEO_SAME_COUNTRY = 0.0
GEO_ADJACENT = 15.0
GEO_SAME_CONTINENT = 35.0
GEO_DIFFERENT_CONTINENT = 60.0
GEO_UNKNOWN = 25.0
