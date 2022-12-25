import pyotp
Totpkey = 'Z24Z347A6XX62B56KR5ODGTX6565PK5D'
# Totpkey = 'F7QK2Z4757P5EDBGH43C5P5M3JZ77LS7'
pin =pyotp.TOTP(Totpkey).now()

pin = f"{(pin)}"

# pin = f"{int(pin):06d}" if len(pin) <= 5 else pin
print("LOGIN AYYA MOWAA")
print(pin)
