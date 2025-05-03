# Códigos ANSI para colorir o terminal
RED = '\033[91m'     # Para a chave
YELLOW = '\033[93m'  # Para elemento em comparação
GREEN = '\033[92m'   # Para o elemento que parou
BLUE = '\033[94m'    # Para deslocamento
RESET = '\033[0m'

def ordena(v):
    print(f"Lista original: {v}")
    for i in range(1, len(v)):
        chave = v[i]
        j = i - 1

        print(f"\n{'='*40}")
        print(f"Iteração {i}:")
        print(f"  Chave selecionada: {RED}{chave}{RESET}")
        
        # Mostra a lista com a chave destacada
        lista_formatada = [
            f"{RED}{num}{RESET}" if idx == i else str(num)
            for idx, num in enumerate(v)
        ]
        print(f"  A partir desta lista --> [{', '.join(lista_formatada)}]")

        while j >= 0:
            print(f"  Comparando {YELLOW}{v[j]}{RESET} com {RED}{chave}{RESET}...", end=' ')
            if v[j] > chave:
                v[j + 1] = v[j]
                # Exibe a lista destacando o número deslocado
                lista_deslocada = [
                    f"{BLUE}{v[idx]}{RESET}" if idx == j + 1 else str(v[idx])
                    for idx in range(len(v))
                ]
                print(f"Desloca {v[j]} para a direita → [{', '.join(lista_deslocada)}]")
                j -= 1
            else:
                print(f"{GREEN}Parou: {v[j]} ≤ {chave}{RESET}")
                break

        v[j + 1] = chave

        # Exibe a lista após a inserção da chave, destacando ela
        lista_inserida = [
            f"{RED}{v[idx]}{RESET}" if idx == j + 1 else str(v[idx])
            for idx in range(len(v))
        ]
        print(f"  Inserindo chave na posição {j + 1} → [{', '.join(lista_inserida)}]")

    print(f"\n{'='*40}\nLista ordenada: {v}")

# Exemplo
numeros = [5, 2, 4, 6, 1, 3]
ordena(numeros)
