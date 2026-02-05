def validate_phone_numbers(phone_numbers):
    valid_phones = []

    for phone in phone_numbers:
        if len(phone) == 10 and phone.isdigit():
            valid_phones.append(phone)

    return valid_phones


def validate_upi_ids(upi_ids):
    valid_upis = []

    for upi in upi_ids:
        if "@" in upi and len(upi.split("@")) == 2:
            valid_upis.append(upi)

    return valid_upis
