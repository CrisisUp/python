import os

# Códigos ANSI para cores
VERDE = '\033[92m'
AZUL = '\033[94m'
AMARELO = '\033[93m'
VERMELHO = '\033[91m'
RESET = '\033[0m'

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def explicacao_decimal_para_binario(numero):
    binario = ''
    quociente = numero
    passos = []

    while quociente > 0:
        resto = quociente % 2
        binario = str(resto) + binario
        passos.append((quociente, resto))
        quociente //= 2

    return binario, passos

def explicacao_binario_para_decimal(binario_str):
    decimal = 0
    tamanho = len(binario_str)
    passos = []

    for i, bit in enumerate(binario_str):
        expoente = tamanho - 1 - i
        valor = int(bit) * (2 ** expoente)
        decimal += valor
        passos.append((bit, expoente, valor))

    return decimal, passos

def explicacao_decimal_para_hex(numero):
    hex_chars = "0123456789ABCDEF"
    resultado = ''
    quociente = numero
    passos = []

    while quociente > 0:
        resto = quociente % 16
        resultado = hex_chars[resto] + resultado
        passos.append((quociente, resto, hex_chars[resto]))
        quociente //= 16

    return resultado, passos

def explicacao_hex_para_decimal(hex_str):
    hex_chars = "0123456789ABCDEF"
    hex_str = hex_str.upper()
    decimal = 0
    tamanho = len(hex_str)
    passos = []

    for i, caractere in enumerate(hex_str):
        expoente = tamanho - 1 - i
        valor = hex_chars.index(caractere) * (16 ** expoente)
        decimal += valor
        passos.append((caractere, expoente, valor))

    return decimal, passos

def hex_para_binario(hex_str):
    hex_str = hex_str.upper()
    binario_completo = ''
    passos = []
    for c in hex_str:
        b = bin(int(c, 16))[2:].zfill(4)
        passos.append((c, b))
        binario_completo += b
    return binario_completo, passos

def menu():
    print(f"{AZUL}=== Conversor de Bases (Decimal ↔ Binário ↔ Hexadecimal) ==={RESET}")
    print("Escolha uma opção:")
    print("1 - Decimal para Binário")
    print("2 - Binário para Decimal")
    print("3 - Decimal para Hexadecimal")
    print("4 - Hexadecimal para Decimal")
    print("5 - Hexadecimal para Binário")
    print("0 - Sair")
    return input("Opção (0 a 5): ").strip()

def pedir_decimal():
    while True:
        try:
            numero = int(input("Digite um número inteiro decimal: "))
            if numero < 0:
                print(f"{AMARELO}Por favor, digite um número positivo.{RESET}")
            else:
                return numero
        except ValueError:
            print(f"{VERMELHO}Erro: Digite um número inteiro válido.{RESET}")

def pedir_binario():
    while True:
        binario = input("Digite um número binário (ex: 1011): ").strip()
        if all(bit in '01' for bit in binario) and binario != '':
            return binario
        else:
            print(f"{VERMELHO}Erro: Entrada não é um número binário válido.{RESET}")

def pedir_hexadecimal():
    while True:
        hexa = input("Digite um número hexadecimal (ex: 1A3F): ").strip().upper()
        if all(c in '0123456789ABCDEFabcdef' for c in hexa) and hexa != '':
            return hexa
        else:
            print(f"{VERMELHO}Erro: Entrada não é um hexadecimal válido.{RESET}")

def main():
    while True:
        limpar_tela()
        escolha = menu()

        if escolha == '1':  # Decimal para Binário
            numero = pedir_decimal()
            binario, passos = explicacao_decimal_para_binario(numero)
            print(f"\n{VERDE}Etapas da conversão decimal → binário:{RESET}")
            for quociente, resto in passos:
                print(f"{AZUL}{quociente}{RESET} ÷ 2 = {AZUL}{quociente // 2}{RESET} com resto = {AMARELO}{resto}{RESET}")
            print(f"\nResultado final: {AMARELO}{binario}{RESET}")

        elif escolha == '2':  # Binário para Decimal
            binario_str = pedir_binario()
            decimal, passos = explicacao_binario_para_decimal(binario_str)
            print(f"\n{VERDE}Etapas da conversão binário → decimal:{RESET}")
            for bit, expoente, valor in passos:
                print(f"{AMARELO}{bit}{RESET} × 2^{AZUL}{expoente}{RESET} = {VERDE}{valor}{RESET}")
            print(f"\nResultado final: {AMARELO}{decimal}{RESET}")

        elif escolha == '3':  # Decimal para Hexadecimal
            numero = pedir_decimal()
            hexa, passos = explicacao_decimal_para_hex(numero)
            print(f"\n{VERDE}Etapas da conversão decimal → hexadecimal:{RESET}")
            for quociente, resto, caractere in passos:
                print(f"{AZUL}{quociente}{RESET} ÷ 16 = {AZUL}{quociente // 16}{RESET} com resto = {AMARELO}{resto}{RESET} → {VERDE}{caractere}{RESET}")
            print(f"\nResultado final: {AMARELO}0x{hexa}{RESET}")

        elif escolha == '4':  # Hexadecimal para Decimal
            hex_str = pedir_hexadecimal()
            decimal, passos = explicacao_hex_para_decimal(hex_str)
            print(f"\n{VERDE}Etapas da conversão hexadecimal → decimal:{RESET}")
            for caractere, expoente, valor in passos:
                print(f"{AMARELO}{caractere}{RESET} × 16^{AZUL}{expoente}{RESET} = {VERDE}{valor}{RESET}")
            print(f"\nResultado final: {AMARELO}{decimal}{RESET}")

        elif escolha == '5':  # Hexadecimal para Binário
            hex_str = pedir_hexadecimal()
            binario, passos = hex_para_binario(hex_str)
            print(f"\n{VERDE}Conversão hexadecimal → binário (4 bits por dígito):{RESET}")
            for c, b in passos:
                print(f"{AMARELO}{c}{RESET} → {AZUL}{b}{RESET}")
            print(f"\nResultado final: {AMARELO}{binario}{RESET}")

        elif escolha == '0':
            print(f"{AZUL}Encerrando o programa. Até logo!{RESET}")
            break

        else:
            print(f"{VERMELHO}Opção inválida. Tente novamente.{RESET}")

        input(f"\n{AZUL}Pressione Enter para continuar...{RESET}")

if __name__ == "__main__":
    main()
