from colorama import init, Fore, Style
init(autoreset=True)  # Inicializa colorama

print(Fore.CYAN + "\n🔢 Soma de Números Inteiros")
print(Fore.YELLOW + "(Digite 0 para encerrar)\n")
soma = 0
numeros = []

while True:
    try:
        entrada = input(Fore.WHITE + "Digite um número inteiro: ")
        numero = int(entrada)
        if numero == 0:
            break
        numeros.append(numero)
        soma += numero
    except ValueError:
        print(Fore.RED + "❌ Entrada inválida. Digite apenas números inteiros.\n")

print(Fore.GREEN + "\n✅ Programa encerrado com sucesso!")
print(Fore.BLUE + f"Números digitados: {numeros}")
print(Fore.MAGENTA + f"Soma total: {soma}")
