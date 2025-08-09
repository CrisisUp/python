"""
while True:
    try:
        nota = float(input("Digite uma nota entre 0 e 10: "))
        if 0 <= nota <= 10:
            print(f"Nota válida: {nota}")
            break
        else:
            print("Erro: a nota deve estar entre 0 e 10.")
    except ValueError:
        print("Erro: digite um número válido.")
"""

from colorama import init, Fore, Style
init(autoreset=True)
print(Fore.CYAN + "\n💰 Calculadora de Desconto por Faixa de Preço\n")

try:
  preco = float(input(Fore.WHITE + "Informe o valor do produto (em R$): ").replace(",", "."))

  if preco < 100:
    porcentagem = 5
  elif preco < 500:  
    porcentagem = 10
  else:  
    porcentagem = 15

  desconto = preco * (porcentagem / 100)
  preco_final = preco - desconto

  print(Fore.GREEN + "\n✅ Desconto aplicado com sucesso!")
  print(Fore.BLUE   + f"Preço original:           R$ {preco:.2f}")
  print(Fore.MAGENTA+ f"Desconto aplicado:        {porcentagem}%")
  print(Fore.YELLOW + f"Valor do desconto:        R$ {desconto:.2f}")
  print(Fore.CYAN   + f"Preço final com desconto: R$ {preco_final:.2f}")

except ValueError:
  print(Fore.RED + "\n❌ Entrada inválida! Digite um valor numérico (ex: 149.90).")
