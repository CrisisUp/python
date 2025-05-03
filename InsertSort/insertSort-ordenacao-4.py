# Códigos ANSI para colorir o terminal
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

def ordena(v):
    print(f"Lista original: {v}")
    for i in range(1, len(v)):
        chave = v[i]
        j = i - 1

        print(f"\n{'='*40}")
        print(f"Iteração {i}:")
        print(f"  Chave selecionada: {RED}{chave}{RESET}")
        
        lista_colorida = [
            f"{RED}{num}{RESET}" if idx == i else str(num)
            for idx, num in enumerate(v)
        ]
        print(f"  A partir desta lista --> [{', '.join(lista_colorida)}]")

        while j >= 0:
            print(f"  Comparando {YELLOW}{v[j]}{RESET} com {RED}{chave}{RESET}...", end=' ')
            if v[j] > chave:
                v[j + 1] = v[j]
                print(f"{BLUE}Desloca {v[j]} para a direita{RESET} → {v}")
                j -= 1
            else:
                print(f"{GREEN}Parou: {v[j]} ≤ {chave}{RESET}")
                break

        v[j + 1] = chave
        print(f"  Inserindo chave na posição {j + 1} → {v}")

    print(f"\n{'='*40}\nLista ordenada: {v}")

# Exemplo
numeros = [5, 2, 4, 6, 1, 3]
ordena(numeros)
