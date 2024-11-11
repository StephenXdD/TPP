def hashing_program(keyfield_number, space):
    address = ((keyfield_number % 2) * space) + space * (keyfield_number % 3)
    print(address)

hashing_program(8075, 7638)