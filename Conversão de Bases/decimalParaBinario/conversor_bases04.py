import os

# Cores para facilitar a leitura
class Cor:
    AZUL = '\033[94m'
    VERDE = '\033[92m'
    VERMELHO = '\033[91m'
    AMARELO = '\033[93m'
    RESET = '\033[0m'

def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')

def cabecalho(titulo):
    print(f"{Cor.AZUL}{'-'*40}")
    print(f"{titulo.center(40)}")
    print(f"{'-'*40}{Cor.RESET}")

def ler_entrada_base(msg, validos):
    while True:
        entrada = input(msg).strip().lower()
        if entrada in validos:
            return entrada
        else:
            print(f"{Cor.VERMELHO}Opção inválida. Tente novamente.{Cor.RESET}")

def ler_valor(msg, validacao):
    while True:
        valor = input(msg).strip()
        if validacao(valor):
            return valor
        else:
            print(f"{Cor.VERMELHO}Valor inválido. Tente novamente.{Cor.RESET}")

# Validações
def binario_valido(b): return all(c in '01' for c in b)
def decimal_valido(d): return d.isdigit()
def hexadecimal_valido(h): return all(c in '0123456789abcdefABCDEF' for c in h)
def octal_valido(o): return all(c in '01234567' for c in o)

# Conversões
def bin_para_dec(b): return str(int(b, 2))
def bin_para_hex(b): return hex(int(b, 2))[2:].upper()
def bin_para_oct(b): return oct(int(b, 2))[2:]

def dec_para_bin(d): return bin(int(d))[2:]
def dec_para_hex(d): return hex(int(d))[2:].upper()
def dec_para_oct(d): return oct(int(d))[2:]

def hex_para_dec(h): return str(int(h, 16))
def hex_para_bin(h): return bin(int(h, 16))[2:]
def hex_para_oct(h): return oct(int(h, 16))[2:]

def oct_para_bin(o): return bin(int(o, 8))[2:]
def oct_para_dec(o): return str(int(o, 8))
def oct_para_hex(o): return hex(int(o, 8))[2:].upper()

def mostrar_resultado(origem, destino, entrada, resultado):
    print(f"{Cor.VERDE}{entrada} ({origem.upper()}) → {resultado} ({destino.upper()}){Cor.RESET}")

# Tabela de conversões possíveis
conversoes = {
    'binario': {
        'decimal': (bin_para_dec, binario_valido),
        'hexadecimal': (bin_para_hex, binario_valido),
        'octal': (bin_para_oct, binario_valido)
    },
    'decimal': {
        'binario': (dec_para_bin, decimal_valido),
        'hexadecimal': (dec_para_hex, decimal_valido),
        'octal': (dec_para_oct, decimal_valido)
    },
    'hexadecimal': {
        'decimal': (hex_para_dec, hexadecimal_valido),
        'binario': (hex_para_bin, hexadecimal_valido),
        'octal': (hex_para_oct, hexadecimal_valido)
    },
    'octal': {
        'decimal': (oct_para_dec, octal_valido),
        'binario': (oct_para_bin, octal_valido),
        'hexadecimal': (oct_para_hex, octal_valido)
    }
}

def main():
    while True:
        limpar()
        cabecalho("CONVERSOR DE BASES NUMÉRICAS")

        print(f"{Cor.AMARELO}Bases disponíveis: binario, decimal, hexadecimal, octal{Cor.RESET}")
        origem = ler_entrada_base("Escolha a base de origem: ", conversoes.keys())
        destino = ler_entrada_base(f"Escolha a base de destino ({', '.join(conversoes[origem].keys())}): ", conversoes[origem].keys())

        funcao, validacao = conversoes[origem][destino]
        valor = ler_valor(f"Digite um valor em {origem.upper()}: ", validacao)

        resultado = funcao(valor)
        mostrar_resultado(origem, destino, valor, resultado)

        continuar = input(f"\n{Cor.AMARELO}Deseja fazer outra conversão? (s/n): {Cor.RESET}").strip().lower()
        if continuar != 's':
            print(f"{Cor.VERDE}Obrigado por usar o conversor!{Cor.RESET}")
            break

if __name__ == "__main__":
    main()
