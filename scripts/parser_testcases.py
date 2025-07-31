#!/usr/bin/env python3

import re
import csv

with open('data/_testcases.txt', encoding='iso-8859-1') as f:
    text = f.read()

# Regex to match SPICE tags with name="L3", "L4", or "L5"
SPICE_TAG_PATTERN = r'<\bxhublayer\s[^>]*\bname\s*=\s*"(L3|L4|L5)"[^>]*>'

# Regex to match thermal conductivity and heat capacity attributes within the SPICE tag
SPICE_THCONF_PATTERN = r'thconf\s*=\s*"([^"]+)"'
SPICE_THCAPF_PATTERN = r'thcapf\s*=\s*"([^"]+)"'

# Regex to match COMSOL tags with name="L3", "L4", or "L5"
COMSOL_TAG_PATTERN = r'<\bxhublayercomsol\s[^>]*\bname\s*=\s*"(L3|L4|L5)"[^>]*>'

# Regex to match thermal conductivity and heat capacity attributes within the COMSOL tag
COMSOL_THCONF_PATTERN = r'ThermalConductivity\s*=\s*"([^"]+)"'
COMSOL_THCAPF_PATTERN = r'SpecificHeatCapacity\s*=\s*"([^"]+)"'
COMSOL_DENSITY_PATTERN = r'Density\s*=\s*"([^"]+)"'

# To get the full tag, use re.finditer:
spice_tags = [m.group(0) for m in re.finditer(SPICE_TAG_PATTERN, text)]
comsol_tags = [m.group(0) for m in re.finditer(COMSOL_TAG_PATTERN, text)]

rows = []
for spice_tag, comsol_tag in zip(spice_tags, comsol_tags):
    # Extract thermal conductivity and heat capacity from SPICE tag
    spice_thconf_match = re.search(SPICE_THCONF_PATTERN, spice_tag)
    spice_thcapf_match = re.search(SPICE_THCAPF_PATTERN, spice_tag)
    if not (spice_thconf_match and spice_thcapf_match):
        raise ValueError(f"missing attribute in spice tag: {spice_tag}")
    spice_thconf_value = spice_thconf_match.group(1)
    spice_thcapf_value = spice_thcapf_match.group(1)

    # Extract thermal conductivity, heat capacity and density from COMSOL tag
    comsol_thconf_match = re.search(COMSOL_THCONF_PATTERN, comsol_tag)
    comsol_thcapf_match = re.search(COMSOL_THCAPF_PATTERN, comsol_tag)
    comsol_density_match = re.search(COMSOL_DENSITY_PATTERN, comsol_tag)
    if not (comsol_thconf_match and comsol_thcapf_match):
        raise ValueError(f"missing attribute in comsol tag: {comsol_tag}")
    
    # Remove units in brackets
    comsol_thconf_value = comsol_thconf_match.group(1).split()[0].strip()
    comsol_thcapf_value = comsol_thcapf_match.group(1).split()[0].strip()  
    comsol_density_value = comsol_density_match.group(1).split()[0].strip() 

    rows.append([
        spice_thconf_value,
        spice_thcapf_value,
        comsol_thconf_value,
        comsol_thcapf_value,
        comsol_density_value
    ])

# Eliminate duplicate rows
unique_rows = []
seen = set()
for row in rows:
    row_tuple = tuple(row)
    if row_tuple not in seen:
        unique_rows.append(row)
        seen.add(row_tuple)

with open('data/spice_comsol_values.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['spice_thconf', 'spice_thcapf', 'comsol_thconf', 'comsol_thcapf', 'comsol_density'])
    writer.writerows(unique_rows)