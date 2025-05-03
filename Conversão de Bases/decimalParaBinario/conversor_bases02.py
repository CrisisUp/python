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

def menu():
    print(f"{AZUL}=== Conversor de Bases (Decimal ↔ Binário) ==={RESET}")
    print("Escolha uma opção:")
    print("1 - Converter Decimal para Binário")
    print("2 - Converter Binário para Decimal")
    print("0 - Sair")
    return input("Opção (0, 1 ou 2): ").strip()

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

def main():
    while True:
        limpar_tela()
        escolha = menu()

        if escolha == '1':
            numero = pedir_decimal()
            binario, passos = explicacao_decimal_para_binario(numero)

            print(f"\n{VERDE}Etapas da conversão decimal → binário:{RESET}")
            for quociente, resto in passos:
                print(f"{AZUL}{quociente}{RESET} ÷ 2 = {AZUL}{quociente // 2}{RESET} com resto = {AMARELO}{resto}{RESET}")

            print(f"\n{VERDE}Resultado final em binário: {AMARELO}{binario}{RESET}")

        elif escolha == '2':
            binario_str = pedir_binario()
            decimal, passos = explicacao_binario_para_decimal(binario_str)

            print(f"\n{VERDE}Etapas da conversão binário → decimal:{RESET}")
            for bit, expoente, valor in passos:
                print(f"Bit {AMARELO}{bit}{RESET} × 2^{AZUL}{expoente}{RESET} = {VERDE}{valor}{RESET}")

            print(f"\n{VERDE}Resultado final em decimal: {AMARELO}{decimal}{RESET}")

        elif escolha == '0':
            print(f"{AZUL}Encerrando o programa. Até mais!{RESET}")
            break

        else:
            print(f"{VERMELHO}Opção inválida. Tente novamente.{RESET}")
            continue

        input(f"\n{AZUL}Pressione Enter para continuar...{RESET}")

if __name__ == "__main__":
    main()
