try:
  n = int(input("Quantas notas você deseja informar? "))

  if n <= 0:
    print("Erro: o número de notas deve ser maior que zero.")
  else:
    soma = 0
    for i in range(1, n + 1):
      while True:
        try:
          nota = float(input(f"Digite a nota {i}: "))
          if 0 <= nota <= 10:
            soma += nota
            break
          else:
            print("Nota inválida! Digite uma nota entre 0 e 10.")
        except ValueError:
          print("Entrada inválida! Digite um número válido.")
        
    media = soma / n
    print(f"\nA média das {n} notas é: {media:.2f}")
except ValueError:
  print("Erro: digite um número inteiro válido para a quantidade de notas.")
