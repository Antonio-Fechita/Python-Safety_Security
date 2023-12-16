import rsa_library


# unlockCar = '0xfd02'
#
# uplu = rsa_library.generate_keypair(277, 239)
# public_key = uplu[0][0]  # e
# modulus = uplu[0][1]  # n
# private_key = uplu[1][0]  # d
#
#
# print(unlockCar)
# mess = hex(rsa_library.encrypt((public_key, modulus), int(unlockCar, 16))).encode()
# print(mess)
# print(rsa_library.decrypt((private_key, modulus), int(mess.decode(), 16)))
# #-----------------------------------------------------------------
#
#
# message_from_client = hex(rsa_library.encrypt((public_key, modulus), 0xfd02)).encode()
# received = rsa_library.decrypt((private_key, modulus), int(message_from_client.decode(), 16))


print(0xaaaa.bit_length())