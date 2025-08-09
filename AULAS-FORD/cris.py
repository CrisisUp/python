from colorama import init, Fore
init(autoreset=True)
print(Fore.CYAN + "\n◼️ Calculadora de Perímetro de um Quadrado\n")

try:
  lado = float(input(Fore.WHITE + "Digite o valor do lado (em metros): "))

  if lado <= 0:
    print(Fore.RED + "❌ O lado deve ser maior que zero.")
  else:
    perimetro = 4 * lado
    print(Fore.GREEN + f"\n✅ Perímetro do quadrado: {perimetro:.2f} m")

except ValueError:
  print(Fore.RED + "\n❌ Entrada inválida! Digite apenas números válidos.")





