def ordena(v): 
    for i in range(1, len(v)): 
        chave = v[i] 
        j = i - 1 
        while j >= 0 and v[j] > chave: 
            v[j + 1] = v[j] 
            j -= 1 
        v[j + 1] = chave 

# Criando uma lista de números fora de ordem
numeros = [8, 5, 2, 7, 4, 6, 1, 3, 9]

# Chamando a função para ordenar a lista
ordena(numeros)

# Exibindo o resultado
print("Lista ordenada:", numeros)
