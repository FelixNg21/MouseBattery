# MouseBattery

A Windows system tray application that displays the live battery percentage of an Incott G23 V2.

![The MouseBattery tray icon showing 94% battery remaining.](docs/images/tray-image.png)

## Supported hardware

  Tested with: Incott G23 V2, 2.4 GHZ dongle (USB ID 093a:522c)
  Other mouse models may use different packets and require varying ways to parse the presented data. Use `capture.py` to record the packets and then analysis can be done to determine what each byte means.

## Download and run

    Go to: https://github.com/FelixNg21/mouse-battery/releases/latest
    Unzip the zip.
    Run MouseBattery.exe and look for the icon in your tray.
    Right click the icon and enable "Start at login"


## Build from source

You need Windows and Python 3.11 (the version this was developed and tested with;
other versions haven't been tried). The dongle is only needed to *run* the app,
not to build it or run the tests.

```powershell
git clone https://github.com/FelixNg21/mouse-battery.git
cd mouse-battery

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
```

Run the tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run the app from source (without building an exe):

```powershell
.\.venv\Scripts\python.exe -m mousebattery tray
```

Build the exe:

```powershell
.\.venv\Scripts\python.exe build_exe.py --onefile
```

The result is `dist\MouseBattery.exe`. Leave out `--onefile` to get a folder
build in `dist\MouseBattery\` instead. If a copy of the app is running, quit it
first: Windows won't let a running exe be overwritten.

## What is and isn't verified

There is no official documentation of this mouse's USB format. Everything here was
worked out by observing what the dongle sends, using one mouse (Incott G23 V2, 2.4 GHz
dongle, USB ID `093a:522c`) on one Windows PC (Windows build 22631, Python 3.11.4).

**Checked and working**

- **Battery percentage.** It goes down as the mouse is used and reads exactly 100% after
  a full charge.
- **Charging indicator.** It shows while the cable is charging the mouse and clears when
  the charge completes.
- **Reconnecting.** If the dongle is unplugged and plugged back in, the app reconnects
  within a few seconds without a restart.
- **Start at login.** The tray menu item adds and removes the login entry, and the app
  starts after a restart.
- **The release exe.** It was built from a clean virtual environment and runs from a
  folder that doesn't contain the project files.

**Not verified, or known limitations**

- **Accuracy.** The percentage has never been compared with the manufacturer's own
  battery display (their driver page was unavailable during testing), so it may not match.
- **Updates pause while you use the mouse.** The dongle sends status reports when the
  mouse is idle, so the value can lag. The tooltip says how old the reading is once it's
  more than two minutes old.
- **Other connection modes.** Bluetooth, and plugging the mouse straight into the PC
  without the dongle, were not tested.
- **Other computers.** The app has not been run on a second PC, or on one without Python
  installed. How Windows SmartScreen and antivirus programs treat the exe is also untested.

**Experimental extras.** The status packet also contains DPI and polling-rate fields.
The tray doesn't show them, but the command-line `battery` command prints them. The DPI
formula matches six DPI stages, but it hasn't been confirmed against official software.
The polling-rate field steps through four values as the button is pressed, but which
value means which rate is a guess. Three other bytes in the packet never changed and
are unidentified.

## Does it work with my mouse?

Probably not yet. The app only recognizes this mouse's dongle IDs and one kind of report,
and other models, even from the same chip maker, may lay theirs out differently. If you'd
like to help with another model, you can collect the information from source (see
[Build from source](#build-from-source) for setup):

1. List the USB HID devices, and find the lines for your mouse. Note the `VID:PID` and
   any interfaces marked `[vendor]`:

   ```powershell
   python -m mousebattery list --all
   ```

2. For those IDs, show which reports each vendor channel uses (this only reads):

   ```powershell
   python -m mousebattery descriptor --vid <VID> --pid <PID>
   ```

3. Open an issue with: the mouse model and connection mode, your mouse's lines from step 1,
   the output of step 2, your Windows version, and what the manufacturer's software shows
   for battery at the time.

In step 1, please paste only the lines for your mouse. The full list names every HID
device on your PC, including keyboards and headsets.

Please don't send guessed packets to your mouse to see what happens. The same channels
can carry settings or firmware, and this app is deliberately read-only.

## Privacy and safety

- **Read-only.** The app only listens to the status reports the dongle sends. It never
  writes to the mouse or the dongle.
- **No network.** It makes no network connections and collects no data.
- **A log file.** The app writes `%LOCALAPPDATA%\mousebattery\mousebattery.log`, kept to
  roughly 750 KB by rotation. It holds timestamps, battery and charging changes,
  connection problems, and error tracebacks. Use "Open log file" in the tray menu to read
  it. Tracebacks can include file paths with your Windows username, so check before you
  paste any of it into an issue.
- **What it changes on your PC.** Only the log folder above, and, only if you turn on
  "Start at login", one value named `MouseBattery` under
  `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`. Turning the option off removes it.
  It's per-user and needs no administrator rights.

## License

Released under the MIT license. See [LICENSE](LICENSE).

The release build bundles third-party libraries that keep their own licenses. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

MouseBattery is an independent project. It is not affiliated with, endorsed by, or
sponsored by Incott or PixArt. Those names are used only to say which hardware it was
tested with.
