"""
import getpass

print("🔐 Criador de Senha Segura 🔐\n")
senha_correta = getpass.getpass("Crie sua senha: ")

while True:
    tentativa = getpass.getpass("Digite novamente a senha para confirmar: ")
    if tentativa == senha_correta:
        print("\n✅ Senha confirmada com sucesso!")
        break
    else:
        print("❌ As senhas não coincidem. Tente novamente.\n")
"""

from colorama import init, Fore
init(autoreset=True)
print(Fore.CYAN + "\n🧮 Calculadora de Operações Básicas com Decimais\n")
try:
  num1 = float(input(Fore.WHITE + "Digite o primeiro número: "))
  num2 = float(input(Fore.WHITE + "Digite o segundo número: "))
  print(Fore.YELLOW + "\nEscolha a operação:")
  print(" - soma")
  print(" - subtração")
  print(" - multiplicação")
  print(" - divisão")
  operacao = input(Fore.WHITE + "\nDigite a operação desejada: ").strip().lower()
  if operacao == "soma":
    resultado = num1 + num2
    simbolo = "+"
  elif operacao == "subtração":
    resultado = num1 - num2
    simbolo = "-"
  elif operacao == "multiplicação":
    resultado = num1 * num2
    simbolo = "×"
  elif operacao == "divisão":
    if num2 == 0:
      print(Fore.RED + "\n❌ Erro: divisão por zero não é permitida.")
      exit()
    resultado = num1 / num2
    simbolo = "÷"
  else:
    print(Fore.RED + "\n❌ Operação inválida. Use apenas: soma, subtração, multiplicação ou divisão.")
    exit()
  print(Fore.GREEN + f"\n✅ Resultado: {num1} {simbolo} {num2} = {resultado:.2f}")
except ValueError:
  print(Fore.RED + "\n❌ Entrada inválida! Digite apenas números reais (ex: 10.5 ou 3,75).")
