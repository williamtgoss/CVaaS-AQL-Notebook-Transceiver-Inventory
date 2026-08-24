#!/usr/bin/env python3
"""Merge CVaaS AQL notebook exports (serial, type, hostname) into one long-format transceiver report."""
import argparse
import csv
import re
import sys

EMPTY_MARKERS = {"", "unknown"}


def read_wide(path):
    """Read a 'key' + per-interface-column CSV into {device: {interface: value}}."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        interfaces = header[1:]
        data = {}
        for row in reader:
            if not row or not row[0]:
                continue
            device = row[0].strip()
            values = {}
            for iface, val in zip(interfaces, row[1:]):
                values[iface.strip()] = (val or "").strip()
            data[device] = values
    return data


def read_narrow(path):
    """Read a 'key' + single-value CSV into {device: value}, regardless of header names."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # header, names not relied upon
        data = {}
        for row in reader:
            if not row or not row[0]:
                continue
            device = row[0].strip()
            value = (row[1] if len(row) > 1 else "").strip()
            data[device] = value
    return data


def natural_key(s):
    return [int(chunk) if chunk.isdigit() else chunk for chunk in re.split(r"(\d+)", s)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("serials_csv")
    parser.add_argument("types_csv")
    parser.add_argument("hostnames_csv")
    parser.add_argument("-o", "--output", default="transceiver-report.csv")
    args = parser.parse_args()

    serials = read_wide(args.serials_csv)
    types = read_wide(args.types_csv)
    hostnames = read_narrow(args.hostnames_csv)

    rows = []
    devices = sorted(set(serials) | set(types))
    for device in devices:
        device_serials = serials.get(device, {})
        device_types = types.get(device, {})
        interfaces = sorted(set(device_serials) | set(device_types), key=natural_key)
        hostname = hostnames.get(device, device)
        for iface in interfaces:
            serial = device_serials.get(iface, "")
            xcvr_type = device_types.get(iface, "")
            if serial.lower() in EMPTY_MARKERS:
                continue
            rows.append((hostname, device, iface, xcvr_type, serial))

    rows.sort(key=lambda r: (r[0], natural_key(r[2])))

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["hostname", "device_id", "interface", "type", "serial"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} transceiver rows to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
