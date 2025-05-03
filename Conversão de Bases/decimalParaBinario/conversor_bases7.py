from colorama import init, Fore, Style
import string

init(autoreset=True)

DIGITOS_VALIDOS = string.digits + string.ascii_uppercase

def base_valida(b):
    return b.isdigit() and 2 <= int(b) <= 36

def validar_digitos(numero, base):
    base = int(base)
    numero = numero.upper()
    for char in numero:
        if char not in DIGITOS_VALIDOS[:base]:
            return False, char
    return True, None

def para_decimal(numero, base_origem):
    return int(numero, int(base_origem))

def de_decimal(numero_decimal, base_destino):
    base_destino = int(base_destino)
    if numero_decimal == 0:
        return '0'
    resultado = ''
    while numero_decimal > 0:
        resto = numero_decimal % base_destino
        resultado = DIGITOS_VALIDOS[resto] + resultado
        numero_decimal //= base_destino
    return resultado

def conversor_personalizado():
    print(Fore.GREEN + "\n=== Conversor de Bases (2 a 36) ===")

    while True:
        print(Fore.MAGENTA + "\n--- Nova Conversão ---")
        
        base_origem = input(Fore.CYAN + "Digite a base de ORIGEM (2 a 36, ou 'S' para sair): ").strip()
        if base_origem.lower() == 's':
            break
        while not base_valida(base_origem):
            print(Fore.RED + "Base inválida. Use um número de 2 a 36.")
            base_origem = input(Fore.CYAN + "Digite novamente a base de ORIGEM: ").strip()
            if base_origem.lower() == 's':
                return
        
        valor = input(Fore.CYAN + f"Digite o número na base {base_origem}: ").strip().upper()
        valido, caractere = validar_digitos(valor, base_origem)
        if not valido:
            print(Fore.RED + f"Erro: o caractere '{caractere}' não é válido na base {base_origem}.")
            continue
        
        base_destino = input(Fore.CYAN + "Digite a base de DESTINO (2 a 36, ou 'S' para sair): ").strip()
        if base_destino.lower() == 's':
            break
        while not base_valida(base_destino):
            print(Fore.RED + "Base inválida. Use um número de 2 a 36.")
            base_destino = input(Fore.CYAN + "Digite novamente a base de DESTINO: ").strip()
            if base_destino.lower() == 's':
                return

        try:
            numero_decimal = para_decimal(valor, base_origem)
            convertido = de_decimal(numero_decimal, base_destino)
            print(Fore.GREEN + f"\n{valor} (base {base_origem}) → {convertido} (base {base_destino})")
        except Exception as e:
            print(Fore.RED + f"Erro durante a conversão: {e}")
    
    print(Fore.BLUE + "\nObrigado por usar o conversor! 👋")

# Execução principal
if __name__ == "__main__":
    conversor_personalizado()
