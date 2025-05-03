from colorama import init, Fore, Style

# Inicializa o colorama
init(autoreset=True)

# Dicionário de bases e seus nomes
bases = {
    "2": "Binário",
    "8": "Octal",
    "10": "Decimal",
    "16": "Hexadecimal"
}

def exibir_opcoes():
    print(Fore.CYAN + "\nEscolha uma base:")
    for chave, nome in bases.items():
        print(f"{Fore.YELLOW}[{chave}]{Style.RESET_ALL} {nome}")

def validar_base(base):
    return base in bases

def converter(valor, base_origem, base_destino):
    try:
        numero_decimal = int(valor, int(base_origem))
    except ValueError:
        print(Fore.RED + "Erro: número inválido para a base selecionada.")
        return None
    
    if base_destino == "2":
        return bin(numero_decimal)[2:]
    elif base_destino == "8":
        return oct(numero_decimal)[2:]
    elif base_destino == "10":
        return str(numero_decimal)
    elif base_destino == "16":
        return hex(numero_decimal)[2:].upper()
    else:
        return None

def conversor_interativo():
    print(Fore.GREEN + "\n=== Conversor de Bases Numéricas ===")
    
    while True:
        print(Fore.MAGENTA + "\n--- Nova Conversão ---")
        
        # Etapa 1: Escolha da base de origem
        exibir_opcoes()
        base_origem = input(Fore.CYAN + "\nDigite a base de ORIGEM (ou 'S' para sair): ").strip()
        if base_origem.lower() == "s":
            break
        while not validar_base(base_origem):
            print(Fore.RED + "Base inválida.")
            base_origem = input(Fore.CYAN + "Digite novamente a base de ORIGEM (ou 'S' para sair): ").strip()
            if base_origem.lower() == "s":
                return
        
        # Etapa 2: Número a ser convertido
        valor = input(Fore.CYAN + f"Digite o número na base {bases[base_origem]}: ").strip()

        # Etapa 3: Escolha da base de destino
        exibir_opcoes()
        base_destino = input(Fore.CYAN + "\nDigite a base de DESTINO (ou 'S' para sair): ").strip()
        if base_destino.lower() == "s":
            break
        while not validar_base(base_destino):
            print(Fore.RED + "Base inválida.")
            base_destino = input(Fore.CYAN + "Digite novamente a base de DESTINO (ou 'S' para sair): ").strip()
            if base_destino.lower() == "s":
                return

        # Etapa 4: Conversão e resultado
        resultado = converter(valor, base_origem, base_destino)
        if resultado is not None:
            print(Fore.GREEN + f"\nResultado: {valor} (base {bases[base_origem]}) → {resultado} (base {bases[base_destino]})")

    print(Fore.BLUE + "\nObrigado por usar o conversor! Até a próxima 👋")

# Execução principal
if __name__ == "__main__":
    conversor_interativo()
