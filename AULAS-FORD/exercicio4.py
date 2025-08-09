print("🔢 Soma de Números Inteiros\n(Digite 0 para encerrar)\n")
soma = 0

while True:
    try:
        numero = int(input("Digite um número inteiro: "))
        if numero == 0:
            break
        soma += numero
    except ValueError:
        print("❌ Entrada inválida. Digite apenas números inteiros.\n")

print(f"\n✅ A soma total dos números digitados é: {soma}")
