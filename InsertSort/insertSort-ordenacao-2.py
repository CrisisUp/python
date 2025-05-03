def ordena(v): 
    print("Lista original:", v)
    for i in range(1, len(v)): 
        chave = v[i] 
        j = i - 1 
        print(f"\nIteração {i}:")
        print(f"  Chave selecionada: {chave}")
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
