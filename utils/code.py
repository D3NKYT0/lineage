import datetime


def base36encode(number):
    base36, sign, alphabet = str(), str(), '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if number < 0:
        sign = '-'
        number = -number
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign + base36


def create_code():
    actual_datetime = datetime.datetime.now()
    actual_datetime = actual_datetime.strftime("1%d%m%y%H%M%S%f")
    return str(base36encode(int(actual_datetime)))
