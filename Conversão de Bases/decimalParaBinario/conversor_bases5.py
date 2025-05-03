import os
import time

# Cores para terminal
VERDE = '\033[92m'
AZUL = '\033[94m'
AMARELO = '\033[93m'
VERMELHO = '\033[91m'
RESET = '\033[0m'

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def esperar():
    input(f"\n{AZUL}Pressione Enter para continuar...{RESET}")

def titulo(texto):
    print(f"\n{AMARELO}{'=' * 50}")
    print(f"{texto.center(50)}")
    print(f"{'=' * 50}{RESET}")

def obter_opcao(mensagem, opcoes_validas):
    while True:
        escolha = input(mensagem).strip().lower()
        if escolha in opcoes_validas:
            return escolha
        else:
            print(f"{VERMELHO}Entrada inválida. Tente novamente.{RESET}")

def obter_numero(base_origem):
    while True:
        valor = input(f"\n{AZUL}Digite o número em {base_origem}: {RESET}").strip().lower()
        try:
            if base_origem == 'binário':
                int(valor, 2)
            elif base_origem == 'octal':
                int(valor, 8)
            elif base_origem == 'decimal':
                int(valor)
            elif base_origem == 'hexadecimal':
                int(valor, 16)
            return valor
        except ValueError:
            print(f"{VERMELHO}Número inválido para a base {base_origem}. Tente novamente.{RESET}")

def converter(valor, base_origem, base_destino):
    base_map = {'binário': 2, 'octal': 8, 'decimal': 10, 'hexadecimal': 16}
    decimal = int(valor, base_map[base_origem])
    print(f"\n{VERDE}Etapa 1: Convertendo {valor.upper()} de {base_origem} para decimal: {decimal}{RESET}")
    time.sleep(1)

    if base_destino == 'decimal':
        print(f"{VERDE}Etapa 2: Resultado final em decimal: {decimal}{RESET}")
    elif base_destino == 'binário':
        binario = bin(decimal)[2:]
        print(f"{VERDE}Etapa 2: Convertendo {decimal} para binário: {binario}{RESET}")
    elif base_destino == 'octal':
        octal = oct(decimal)[2:]
        print(f"{VERDE}Etapa 2: Convertendo {decimal} para octal: {octal}{RESET}")
    elif base_destino == 'hexadecimal':
        hexa = hex(decimal)[2:].upper()
        print(f"{VERDE}Etapa 2: Convertendo {decimal} para hexadecimal: {hexa}{RESET}")

def menu():
    while True:
        limpar_tela()
        titulo("CONVERSOR DE BASES NUMÉRICAS")

        print(f"{AZUL}Escolha a base de ORIGEM:{RESET}")
        print("1. Binário\n2. Octal\n3. Decimal\n4. Hexadecimal")
        opcoes_base = {'1': 'binário', '2': 'octal', '3': 'decimal', '4': 'hexadecimal'}
        origem = obter_opcao("Digite o número da base de origem: ", opcoes_base.keys())
        base_origem = opcoes_base[origem]

        print(f"\n{AZUL}Escolha a base de DESTINO:{RESET}")
        print("1. Binário\n2. Octal\n3. Decimal\n4. Hexadecimal")
        destino = obter_opcao("Digite o número da base de destino: ", opcoes_base.keys())
        base_destino = opcoes_base[destino]

        if base_origem == base_destino:
            print(f"{VERMELHO}As bases de origem e destino são iguais. Escolha diferentes!{RESET}")
            esperar()
            continue

        numero = obter_numero(base_origem)
        converter(numero, base_origem, base_destino)

        continuar = obter_opcao(f"\n{AZUL}Deseja fazer outra conversão? (s/n): {RESET}", ['s', 'n'])
        if continuar == 'n':
            print(f"{VERDE}Obrigado por usar o conversor! Até logo!{RESET}")
            break

menu()
