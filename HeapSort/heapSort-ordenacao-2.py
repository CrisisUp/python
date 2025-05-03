import time

# Códigos ANSI para colorir o terminal
RED = '\033[91m'     # Elemento sendo movido para o final
YELLOW = '\033[93m'  # Subárvore em ajuste (heapify)
GREEN = '\033[92m'   # Elemento finalizado
BLUE = '\033[94m'    # Construção do heap
RESET = '\033[0m'

def heapify(arr, n, i):
    largest = i
    l = 2 * i + 1  # filho esquerdo
    r = 2 * i + 2  # filho direito

    if l < n and arr[l] > arr[largest]:
        largest = l

    if r < n and arr[r] > arr[largest]:
        largest = r

    if largest != i:
        print(f"  {YELLOW}Ajustando subárvore: troca {arr[i]} com {arr[largest]}{RESET}")
        arr[i], arr[largest] = arr[largest], arr[i]
        exibir_lista(arr, destaque=[i, largest], cor=YELLOW)
        time.sleep(0.5)
        heapify(arr, n, largest)
    else:
        print(f"  {YELLOW}Subárvore com raiz {arr[i]} já está em ordem.{RESET}")
        exibir_lista(arr, destaque=[i], cor=YELLOW)
        time.sleep(0.5)

def exibir_lista(arr, destaque=[], cor=RESET):
    lista_formatada = [
        f"{cor}{num}{RESET}" if idx in destaque else str(num)
        for idx, num in enumerate(arr)
    ]
    print(f"  Lista: [{', '.join(lista_formatada)}]")

def heapsort(arr):
    n = len(arr)
    print(f"{BLUE}Construindo o heap...{RESET}")
    for i in range(n // 2 - 1, -1, -1):
        print(f"\nProcessando nó interno de índice {i} (valor {arr[i]})")
        heapify(arr, n, i)

    print(f"\n{RED}Iniciando ordenação por Heapsort...{RESET}")
    for i in range(n - 1, 0, -1):
        print(f"\n{RED}Movendo maior elemento ({arr[0]}) para a posição {i}{RESET}")
        arr[0], arr[i] = arr[i], arr[0]
        exibir_lista(arr, destaque=[i], cor=GREEN)
        time.sleep(0.5)
        heapify(arr, i, 0)

    print(f"\n{GREEN}Lista ordenada:{RESET} {arr}")

# Exemplo de uso
numeros = [4, 10, 3, 5, 1]
heapsort(numeros)
