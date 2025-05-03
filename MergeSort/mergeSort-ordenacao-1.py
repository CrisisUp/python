from termcolor import colored
import time

# Função de intercalação
def intercala(v, ini, meio, fim):
    L = v[ini:meio+1]
    R = v[meio+1:fim+1]
    L.append(999)  # sentinela
    R.append(999)  # sentinela
    i = 0
    j = 0
    print(colored(f'Intercalando: {L[:-1]} e {R[:-1]}', 'blue'))
    for k in range(ini, fim + 1):
        time.sleep(1)  # Espera um pouco para animação
        if L[i] <= R[j]:
            v[k] = L[i]
            i += 1
        else:
            v[k] = R[j]
            j += 1
        # Mostra o vetor a cada iteração de troca
        print(colored(f'Alteração no índice {k}: {v}', 'green'))
        
# Função de merge sort
def meu_sort(v, ini, fim):
    if ini < fim:
        meio = (ini + fim) // 2
        print(colored(f'Divisão do vetor em índices {ini} a {meio} e {meio+1} a {fim}', 'yellow'))
        meu_sort(v, ini, meio)
        meu_sort(v, meio + 1, fim)
        intercala(v, ini, meio, fim)
        print(colored(f'Após intercalação: {v}', 'cyan'))

# Função para iniciar o algoritmo
def merge_sort(v):
    print(f'Vetor inicial: {v}')
    meu_sort(v, 0, len(v) - 1)
    print(colored(f'Vetor ordenado: {v}', 'red'))

# Exemplo de uso
vetor = [38, 27, 43, 3, 9, 82, 10]
merge_sort(vetor)
