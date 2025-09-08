import datetime
import random


def base36encode(number):
    base36, sign, alphabet = str(), str(), '12356789BCDFGHJKLMNPQRSTVWXYZ'  # Sem caracteres: 0,4,A,E,I,O,U
    if number < 0:
        sign = '-'
        number = -number
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign + base36


def create_protocol():
    actual_datetime = datetime.datetime.now()
    # Obtém a data e hora no formato: "1ddMMyyHHMMSSsss"
    datetime_str = actual_datetime.strftime("1%d%m%y%H%M%S") + str(actual_datetime.microsecond)[:3]
    # Adiciona um número aleatório para garantir a unicidade
    random_number = random.randint(0, 999)  # Número aleatório de 3 dígitos
    combined_number = int(datetime_str) + random_number  # Combina a data/hora com o número aleatório
    return base36encode(combined_number)
