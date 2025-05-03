import os

# Códigos ANSI para cores
VERDE = '\033[92m'
AZUL = '\033[94m'
AMARELO = '\033[93m'
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

def main():
    limpar_tela()
    print(f"{AZUL}=== Conversor de Decimal para Binário ==={RESET}")
    try:
        numero = int(input("Digite um número inteiro decimal: "))
        if numero < 0:
            print(f"{AMARELO}Por favor, digite um número inteiro positivo.{RESET}")
            return

        binario, passos = explicacao_decimal_para_binario(numero)

        print(f"\n{VERDE}Etapas da conversão:{RESET}")
        for quociente, resto in passos:
            print(f"{AZUL}{quociente}{RESET} ÷ 2 = {AZUL}{quociente // 2}{RESET} com resto = {AMARELO}{resto}{RESET}")

        print(f"\n{VERDE}Resultado final em binário: {AMARELO}{binario}{RESET}")
    except ValueError:
        print(f"{AMARELO}Entrada inválida. Por favor, digite um número inteiro.{RESET}")

if __name__ == "__main__":
    main()
