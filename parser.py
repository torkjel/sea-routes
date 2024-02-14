# -*- coding: utf-8 -*-
"""Takes a copy paste from the PDF and spews out a nicer file"""
import re
import json

with open('PUB151_raw.txt') as f:
    raw = f.read()

def split_by_port(x):
    """makes list of raw ports"""
    p = re.compile('([A-Z][A-Z\-\(\)\ \,\.\n\’]+\n\([\d]+)')
    x = p.split(x)[1:]
    x = zip(x[::2], x[1::2])
    x = [''.join(list(a)) for a in x]
    return x

ports = split_by_port(raw)

def parse_destinations(ports):
    if ports != 'Special case':
        ports = ports.replace('&', ' ')
        # print(ports)
        # ports = ports.replace(',', '')
        p = re.compile('[\D]+[\d\,\d]+')
        ports = p.findall(ports)
        ports = [x.strip() for x in ports]
        # print(ports[0])
        dist_pattern = re.compile('\d+,*\d+')
        name_pattern = re.compile('\D+')
        ports = [{"name": name_pattern.search(x).group(0).strip()[:-1], "distance": float(dist_pattern.search(x).group(0).replace(',',''))} for x in ports]
        #ports = {x[0]:float(x[1]) for x in ports}
    return ports

def single_location_parser(loc):
    # print('----------RAW------------')
    # print(loc)
    # print('-------EXTRACTED------------')
    loc = loc.replace('\n', '&')
    p = re.compile('.*\([0-9]')
    port_name = p.match(loc).group(0)[:-2].replace('&', ' ').strip()

    # print('Port name: {}'.format(port_name.title()))
    port_name = port_name.title()

    l = re.compile('\(\d.*\\"[A-Z]\.\)')
    location = l.search(loc).group()
    location = location.replace('(', '')
    location = location.replace(')', '')
    # print('location: {}'.format(location))

    try:
        junctions = loc[loc.index("Junction Points*")+len("Junction Points* "):loc.index("Ports")]
    except ValueError as e:
        # print('Special case with no Junction points?')
        junctions = 'Special case'
        pass
    try:
        ports = loc[loc.index("Ports")+len("Ports "):]
    except Exception as e:
        # print('Special case?')
        ports = 'Special case'
        pass

    junctions = parse_destinations(junctions)
    ports = parse_destinations(ports)
    return port_name, location, junctions, ports

def normalize_name(name):
    name_split = name.split(",")
    port_name = name_split[0].strip()
    port_name_split = port_name.split("(")
    port_name_short = port_name_split[0].strip().rstrip(";")
    port_name_detail = ""
    if len(port_name_split) > 1:
        port_name_detail = port_name_split[1].strip().rstrip(")").lstrip("(").strip().rstrip(";")

    if len(name_split) > 1:
        country_name = name_split[1].strip().rstrip(";")
    else:
        country_name = ""

    country_name_split = country_name.split("(")
    country_name_short = country_name_split[0].strip().rstrip(";")
    country_name_detail = ""
    if len(country_name_split) > 1:
        country_name_detail = country_name_split[1].strip().rstrip(")").lstrip("(").strip().rstrip(";")
    return port_name, port_name_short, port_name_detail, country_name, country_name_short, country_name_detail

with open("PUB151_distances.json", 'w') as out:
    a = []
    for port in ports[:]:
        n,l,j,p = single_location_parser(port)
        a.append({"name":n, "location":l, "junctions":j, "destinations":p})
    out.write(json.dumps(a, indent=2, encoding="utf-8", ensure_ascii=False, sort_keys=True))

with open("PUB151_distances.csv", 'w') as out:
    a = []
    out.write("full_name;port_name;port_name_short;port_name_details;country_name;country_name_short;country_name_details;location;type;dest_full_name;dest_port_name;dest_port_name_short;dest_port_name_details;dest_country_name;dest_country_name_short;dest_country_name_details;distance\n")
    for port in ports[:]:
        n,l,j,p = single_location_parser(port)
        port_name, port_name_short, port_name_detail, country_name, country_name_short, country_name_detail = normalize_name(n)
        port_part = n.strip() + ";" + port_name + ";" + port_name_short + ";" + port_name_detail + ";" + country_name + ";" + country_name_short + ";" + country_name_detail + ";" + l
        for junction in j:
            if not isinstance(junction, str):
                port_name, port_name_short, port_name_detail, country_name, country_name_short, country_name_detail = normalize_name(junction["name"])
                out.write(port_part + ";junction;" + junction["name"].strip() + ";" + port_name + ";" + port_name_short + ";" + port_name_detail + ";" + country_name + ";" + country_name_short + ";" + country_name_detail + ";" + str(junction["distance"]) + "\n")

        for dest in p:
            if not isinstance(junction, str):
                out.write(port_part + ";port;" + dest["name"].strip() + ";" + port_name + ";" + port_name_short + ";" + port_name_detail + ";" + country_name + ";" + country_name_short + ";" + country_name_detail + ";" + str(dest["distance"]) + "\n")
