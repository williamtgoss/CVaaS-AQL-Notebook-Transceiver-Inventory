# Transceiver Inventory — Process Guide

This guide walks through generating a full transceiver inventory (hostname,
device ID, interface, transceiver type, and serial number) for every switch
in a CVaaS tenant, using the AQL notebook plus a local merge script.

Related files in this folder:
- `Transceiver-Inventory-AQL-Notebook.txt` — the three AQL queries to paste into the notebook
- `merge_transceivers.py` — combines the three CSV exports into the final report

## 1. Log into CVaaS

Log into your CloudVision as-a-Service tenant in a browser (e.g.
`https://www.cv-prod-us-central1-c.arista.io`, or whichever cluster hosts
your tenant).

## 2. Navigate to the AQL Notebook

1. Click the **Settings** gear icon.
2. Go to **Settings** → **Developer Tools** → **AQL Notebook**.

## 3. Create the notebook

1. Click **+ Add Notebook**.
2. Name it **Transceiver Inventory Queries**.

## 4. Add and run the three query cells

Open `Transceiver-Inventory-AQL-Notebook.txt` for the exact query text. Add
three cells to the notebook, one per query:

| Cell | Purpose | Export filename |
|---|---|---|
| 1 | Transceiver serial number, per device/interface | `serials.csv` |
| 2 | Transceiver media/form-factor type, per device/interface | `types.csv` |
| 3 | Hostname, per device | `hostnames.csv` |

For each cell:
1. Paste the query text.
2. Run it.
3. Export the result to CSV using the notebook's export option, and save it
   with the filename noted above (all three files should end up in the same
   local folder, alongside `merge_transceivers.py`, to keep the next step
   simple).

## 5. Run the merge script

With Python 3 installed, open a terminal in the folder containing the three
CSV files and `merge_transceivers.py`, then run:

```bash
python merge_transceivers.py serials.csv types.csv hostnames.csv -o transceiver-report.csv
```

This produces `transceiver-report.csv`, the final long-format inventory.

## 6. What's in the final CSV

`transceiver-report.csv` has one row per installed transceiver — ports with
no transceiver plugged in are automatically excluded, so this is a list of
optics actually in use, not every physical port.

| Column | Description |
|---|---|
| `hostname` | The device's configured hostname (e.g. `Goss-710`). Falls back to the device ID if no hostname was found. |
| `device_id` | The device's CVaaS device ID / serial number (e.g. `WTW23230296`). |
| `interface` | The interface the transceiver is installed in (e.g. `Ethernet17`). |
| `type` | The transceiver's media/form-factor type as reported by EOS (e.g. `xcvr1000BaseT`, `xcvr25GBaseCrN`). |
| `serial` | The transceiver's own vendor serial number (e.g. `XHT213360080`), distinct from the switch's device ID/serial above. |

## Re-running later

To refresh the inventory, re-run steps 4–5: re-run and re-export the three
notebook cells (they always reflect current fleet state), then re-run the
merge script over the new exports.
