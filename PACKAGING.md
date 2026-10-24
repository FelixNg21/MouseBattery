# Packaging roadmap

Goal: a tray app you don't need a terminal for. `MouseBattery.exe` runs without a
console, starts when you log in, never runs twice, and writes errors to the log.

Each piece has a stub with hints and a test file that acts as the spec. Each test
file starts with a `pytestmark = ... skip` line: delete it when you start on that
piece, watch the tests fail, then make them pass.

Suggested order (each step works on its own):

## 1. Entry point: `run_tray.py`
- [X] Write `main()`: logging first, then the tray.
- [X] Run it: `python run_tray.py` should behave like `python -m mousebattery tray`.

## 2. Single instance: `mousebattery/single_instance.py`  (tests: `test_single_instance.py`)
- [X] Pick an approach (see the docstring) and implement `acquire()` / `release()`.
- [X] Use it in `run_tray.py`. Start two copies by hand to check the second one exits.
- Think about: what happens to the lock if the app crashes or is killed?

## 3. Build: `build_exe.py`  (tests: `test_build.py`)
- [ ] `pip install -r requirements-dev.txt`
- [ ] Write `build_args()`.
- [ ] Do a `--debug` build first. A console window shows errors the windowless build
      would hide. Run `dist\MouseBattery\MouseBattery.exe` from a terminal.
- [ ] Then try the release build, then `--onefile`.
- Questions to research: how do `--onefile` and `--onedir` differ at startup? Which one
  is easier to debug? Why might antivirus or SmartScreen complain about an unsigned exe?
- `build/`, `dist/` and `*.spec` are build output. Don't commit them.

## 4. Login start: `mousebattery/startup.py`  (tests: `test_startup.py`)
- [ ] `startup_command()`, then `enable()`, `disable()`, `is_enabled()`.
- The registry tests only run on Windows and use a throwaway key
  (`HKCU\Software\mousebattery-tests`), never the real Run key.
- [ ] Add two subcommands to `cli.py` yourself: `install-startup` and `uninstall-startup`.
- Design question: when the app runs from source, `sys.executable` is `python.exe`.
  When it's a PyInstaller build, `getattr(sys, "frozen", False)` is true and
  `sys.executable` is your .exe. What should `install-startup` do when not frozen?

## 5. Final checks (do all of these on the real build)
- [ ] Debug build: icon appears, log shows "connected to dongle".
- [ ] Windowless build: no console window, icon still appears.
- [ ] Unplug and replug the dongle: it recovers.
- [ ] Launch a second copy: no second icon.
- [ ] After `install-startup`: `reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
      shows the entry. Sign out and in again: the icon comes back.
- [ ] After `uninstall-startup`: the entry is gone.
- [ ] Menu > Quit leaves no stray process in Task Manager.

## Things I could not verify for you (check them on your machine)
- Whether the built exe can see the dongle. The `hid` module is a compiled extension.
  PyInstaller often finds these on its own, but the only real test is the log line
  "connected to dongle" from the built exe.
- Whether PyInstaller finds pystray's Windows backend. pystray picks its backend at
  runtime, so it may be missed. If the exe starts but no icon appears, check the log,
  then look at `--hidden-import`.
- With no console, `sys.stdout` / `sys.stderr` can be None. `setup_logging` already
  guards against that, but any new code that prints should too.

## Stretch goals
- Generate an `.ico` from `render_icon()` with Pillow and pass it with `--icon`.
- Dim the tray icon when the reading is stale.
- Low-battery notification with `icon.notify(...)`.
- A Startup-folder `.lnk` version of `startup.py`.
