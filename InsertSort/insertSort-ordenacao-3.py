# Códigos ANSI para colorir o terminal
RED = '\033[91m'
RESET = '\033[0m'

def ordena(v): 
    print("Lista original:", v)
    for i in range(1, len(v)): 
        chave = v[i] 
        j = i - 1 
        print(f"\nIteração {i}:")
        print(f"  Chave selecionada: {RED}{chave}{RESET}")
        
        # Mostra a lista com a chave colorida
        lista_formatada = [
            f"{RED}{num}{RESET}" if idx == i else str(num)
            for idx, num in enumerate(v)
        ]
        print(f"  A partir desta lista --> [{', '.join(lista_formatada)}]")

        while j >= 0 and v[j] > chave: 
            v[j + 1] = v[j] 
            j -= 1 
            print(f"  Deslocando {v[j+1]} para a direita → {v}")
        v[j + 1] = chave 
        print(f"  Inserindo chave na posição {j+1} → {v}")
    print("\nLista ordenada:", v)

# Exemplo de uso
numeros = [5, 2, 4, 6, 1, 3]
ordena(numeros)
