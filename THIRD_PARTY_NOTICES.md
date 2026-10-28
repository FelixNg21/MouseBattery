# Third-party notices

MouseBattery's release build bundles the libraries below. Each keeps its own license.

<!-- TODO: fill the blanks. Get versions from `pip freeze` in your build venv, and
     read each project's current license text yourself: the "License" column is what
     the package metadata declared when I checked, not legal advice. -->

| Package | Used for | License (declared in metadata) | Version | Project page |
|---|---|---|---|---|
| pystray | tray icon and menu | LGPL-3.0 | TODO | TODO |
| Pillow | drawing the icon | MIT-CMU | TODO | TODO |
| hidapi (Python bindings) | talking to the USB dongle | BSD or GPLv3, your choice | TODO | TODO |
| PyInstaller | building the exe (not shipped as a library) | GPLv2+ with a special exception | TODO | TODO |

## Things to decide and write down

- **LGPL (pystray).** TODO: include or link the LGPL-3.0 text. Work out what the license
  asks of you when the library is bundled inside an exe, and whether the folder build or
  the one-file build makes that easier. If you aren't sure, ask someone qualified.
- **hidapi.** TODO: state which of its licenses you are relying on.
