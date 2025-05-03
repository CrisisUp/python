from colorama import init, Fore, Style
import string

init(autoreset=True)

DIGITOS_VALIDOS = string.digits + string.ascii_uppercase

def base_valida(b):
    return b.isdigit() and 2 <= int(b) <= 36

def validar_digitos(numero, base):
    base = int(base)
    numero = numero.upper().lstrip('-')
    invalidos = [char for char in numero if char not in DIGITOS_VALIDOS[:base]]
    return invalidos

def para_decimal_explicando(numero, base_origem, modo):
    base = int(base_origem)
    negativo = numero.startswith('-')
    numero = numero.upper().lstrip('-')
    total = 0

    if modo == "detalhado":
        print(Fore.YELLOW + "\n🔍 Conversão para decimal:")
        if negativo:
            print(Fore.CYAN + "Observação: número negativo detectado. O sinal será preservado após a conversão.")
    
    for i, char in enumerate(reversed(numero)):
        valor = DIGITOS_VALIDOS.index(char)
        potencia = base ** i
        parcial = valor * potencia
        if modo == "detalhado":
            print(f"{char} × {base}^{i} = {valor} × {potencia} = {parcial}")
        total += parcial

    total = -total if negativo else total
    if modo == "detalhado":
        print(Fore.GREEN + f"➡ Total em decimal: {total}")
    return total

def de_decimal_explicando(decimal, base_destino, modo):
    base = int(base_destino)
    negativo = decimal < 0
    n = abs(decimal)
    resultado = ''
    etapas = []

    if modo == "detalhado":
        print(Fore.YELLOW + "\n🔄 Conversão de decimal para base destino:")
        if negativo:
            print(Fore.CYAN + "Observação: número negativo detectado. O sinal será reaplicado após a conversão.")

    if n == 0:
        if modo == "detalhado":
            print("0 ÷", base, "= 0 (resto 0)")
        return '0'

    while n > 0:
        quociente = n // base
        resto = n % base
        etapas.append((n, quociente, resto))
        n = quociente

    for n, q, r in etapas:
        if modo == "detalhado":
            print(f"{n} ÷ {base} = {q} (resto {DIGITOS_VALIDOS[r]})")
        resultado = DIGITOS_VALIDOS[r] + resultado

    if negativo:
        resultado = '-' + resultado

    if modo == "detalhado":
        print(Fore.GREEN + f"➡ Resultado final: {resultado}")
    return resultado

def salvar_em_arquivo(conversao):
    with open("conversoes.txt", "a") as f:
        f.write(conversao + "\n")

def conversor_com_melhorias():
    print(Fore.GREEN + "\n=== Conversor de Bases com Melhorias ===")
    print(Fore.YELLOW + "Digite 'S' a qualquer momento para sair.")


    while True:
        print(Fore.MAGENTA + "\n--- Nova Conversão ---")
        
        modo = input(Fore.CYAN + "Escolha o modo (minimalista/detalhado): ").strip().lower()
        if modo not in ["minimalista", "detalhado"]:
            print(Fore.RED + "Modo inválido! Escolha 'minimalista' ou 'detalhado'.")
            continue

        base_origem = input(Fore.CYAN + "Digite a base de ORIGEM (2 a 36, ou 'S' para sair): ").strip()
        if base_origem.lower() == 's':
            break
        while not base_valida(base_origem):
            print(Fore.RED + "Base inválida. Use um número de 2 a 36.")
            base_origem = input(Fore.CYAN + "Digite novamente a base de ORIGEM: ").strip()
            if base_origem.lower() == 's':
                return

        valor = input(Fore.CYAN + f"Digite o número (positivo ou negativo) na base {base_origem}: ").strip().upper()
        invalidos = validar_digitos(valor, base_origem)
        if invalidos:
            print(Fore.RED + f"Erro: os caracteres inválidos para a base {base_origem} são: {', '.join(invalidos)}.")
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
            numero_decimal = para_decimal_explicando(valor, base_origem, modo)
            convertido = de_decimal_explicando(numero_decimal, base_destino, modo)
            conversao = f"{valor} (base {base_origem}) -> {convertido} (base {base_destino})"
            print(Fore.GREEN + f"\n✅ Resultado: {conversao}")
            if modo == "minimalista":
                salvar_em_arquivo(conversao)
        except Exception as e:
            print(Fore.RED + f"Erro durante a conversão: {e}")
    
    print(Fore.BLUE + "\nObrigado por usar o conversor! 👋")

# Execução principal
if __name__ == "__main__":
    conversor_com_melhorias()
