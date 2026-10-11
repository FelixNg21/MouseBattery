"""Device identifiers. Kept in one place so the rest of the code stays generic."""

# PixArt vendor ID, used by the mouse's wireless SoC.
VENDOR_ID = 0x093A

# 2.4 GHz dongle (wireless mode) and the mouse itself (wired mode).
PRODUCT_ID_DONGLE = 0x522C
PRODUCT_ID_WIRED = 0x622C

TARGET_PRODUCT_IDS = (PRODUCT_ID_DONGLE, PRODUCT_ID_WIRED)
