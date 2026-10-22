"""Make sure only one copy of the app runs at a time.

Two copies would each hold the dongle's channels open and show two tray icons,
which is easy to trigger by launching manually after the login auto-start.

Usage:
    guard = SingleInstance("mousebattery")
    if not guard.acquire():
        raise SystemExit(0)   # another copy is already running
    try:
        ...run the app...
    finally:
        guard.release()

Ways to implement it (pick one, and say why):
  * a Windows named mutex via ctypes: kernel32.CreateMutexW, then check
    GetLastError() against ERROR_ALREADY_EXISTS (183)
  * bind a TCP socket on 127.0.0.1 to a port derived from the name
  * a lock file (msvcrt.locking on Windows)
Think about what happens if the app crashes: which approach cleans up after itself?
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

# Constant for Windows API
ERROR_ALREADY_EXISTS = 183

class SingleInstance:
    def __init__(self, name: str):
        self.name = name
        self._mutex_handle = None
        

    def acquire(self) -> bool:
        """Return True if this process now owns the lock, False if another copy holds it."""
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
        kernel32.CreateMutexW.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        
        self._mutex_handle = kernel32.CreateMutexA(None, False, self.name)

        error = ctypes.get_last_error()

        if self._mutex_handle == 0:
            raise ctypes.WinError(error)
        elif error == ERROR_ALREADY_EXISTS:
            kernel32.CloseHandle(self._mutex_handle)
        else:
            return True

    def release(self) -> None:
        """Give the lock up so another copy can start. Must be safe to call twice."""
        if self._mutex_handle:
            kernel32.CloseHandle(self._mutex_handle)
            self._mutex_handle = None

