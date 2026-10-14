def make_packet(byte1=0x56, byte2=0x20, dpi_reg=0x1D):
    """Build a realistic 33-byte status packet"""
    packet = bytearray(33)
    packet[0] = 0x09
    packet[1] = byte1
    packet[2] = byte2
    packet[3] = 0x08
    packet[5] = packet[6] = dpi_reg 
    packet[7] = 0x01
    return bytes(packet)