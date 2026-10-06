"""Strict native log decoding across Windows PowerShell and PowerShell Core.
UTF-16 is selected only by its BOM; unmarked files must be UTF-8.
Original bytes remain unchanged for provenance hashing.
"""
def decode_native_log(raw):
    if raw.startswith((b'\xff\xfe',b'\xfe\xff')):
        return raw.decode('utf-16')
    return raw.decode('utf-8-sig')
