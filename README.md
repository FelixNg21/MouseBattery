# mouse-battery

Reads battery status from an Incott G23 wireless mouse over its USB dongle.

## Setup
    pip install -r requirements.txt

## Step 1: list interfaces
    python -m mousebattery list          # the mouse/dongle only
    python -m mousebattery list --all    # every HID device
