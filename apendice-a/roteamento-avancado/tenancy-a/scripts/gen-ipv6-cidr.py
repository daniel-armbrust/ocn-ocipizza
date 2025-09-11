import sys
import ipaddress

try:
    address_with_prefix = sys.argv[1]
    ipv6_address, prefix = address_with_prefix.split('/')
    expanded_address = ipaddress.IPv6Address(ipv6_address).exploded

    print(f'{expanded_address}/64')
except (IndexError, ValueError):
    print("Erro: Por favor, forneça um endereço IPv6 válido no formato '::/prefixo'.")
    sys.exit(1)

sys.exit(0)