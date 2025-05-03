from colorama import init, Fore, Style
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import string
import os

init(autoreset=True)
console = Console()

DIGITOS_VALIDOS = string.digits + string.ascii_uppercase
HISTORICO_ARQUIVO = "conversoes.txt"

def base_valida(b):
    return b.isdigit() and 2 <= int(b) <= 36

def validar_digitos(numero, base):
    base = int(base)
    numero = numero.upper().lstrip('-')
    invalidos = [char for char in numero if char not in DIGITOS_VALIDOS[:base]]
    return invalidos

def para_decimal_explicando(numero, base_origem, modo):
    base = int(base_origem)
    negativo = numero.startswith('-')
    numero = numero.upper().lstrip('-')
    total = 0

    if modo == "detalhado":
        console.print("\n[bold yellow]🔍 Conversão para decimal:[/]")
        if negativo:
            console.print("[cyan]Número negativo detectado. O sinal será preservado.[/]")
        with Progress() as progress:
            task = progress.add_task("Convertendo...", total=len(numero))
            for i, char in enumerate(reversed(numero)):
                valor = DIGITOS_VALIDOS.index(char)
                potencia = base ** i
                parcial = valor * potencia
                console.print(f"{char} × {base}^{i} = {valor} × {potencia} = {parcial}")
                total += parcial
                progress.update(task, advance=1)

    else:
        for i, char in enumerate(reversed(numero)):
            valor = DIGITOS_VALIDOS.index(char)
            potencia = base ** i
            parcial = valor * potencia
            total += parcial

    return -total if negativo else total

def de_decimal_explicando(decimal, base_destino, modo):
    base = int(base_destino)
    negativo = decimal < 0
    n = abs(decimal)
    resultado = ''
    etapas = []

    if modo == "detalhado":
        console.print("\n[bold yellow]🔄 Conversão para base destino:[/]")
        if negativo:
            console.print("[cyan]Número negativo detectado. O sinal será reaplicado após a conversão.[/]")

    if n == 0:
        if modo == "detalhado":
            console.print(f"0 ÷ {base} = 0 (resto 0)")
        return '0'

    while n > 0:
        quociente = n // base
        resto = n % base
        etapas.append((n, quociente, resto))
        n = quociente

    if modo == "detalhado":
        with Progress() as progress:
            task = progress.add_task("Convertendo...", total=len(etapas))
            for n, q, r in etapas:
                console.print(f"{n} ÷ {base} = {q} (resto {DIGITOS_VALIDOS[r]})")
                progress.update(task, advance=1)

    for _, _, r in etapas:
        resultado = DIGITOS_VALIDOS[r] + resultado

    return '-' + resultado if negativo else resultado

def salvar_em_arquivo(conversao):
    with open(HISTORICO_ARQUIVO, "a", encoding="utf-8") as f:
        f.write(conversao + "\n")

def ver_historico():
    console.print("\n[bold cyan]📜 Histórico de conversões:[/]")
    if not os.path.exists(HISTORICO_ARQUIVO):
        console.print("[italic]Nenhum histórico disponível.[/]")
        return
    with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
        linhas = f.readlines()
    if not linhas:
        console.print("[italic]Histórico está vazio.[/]")
        return
    tabela = Table(show_header=True, header_style="bold magenta")
    tabela.add_column("Nº", style="dim", width=5)
    tabela.add_column("Conversão")
    for i, linha in enumerate(linhas, start=1):
        tabela.add_row(str(i), linha.strip())
    console.print(tabela)

def apagar_historico():
    if not os.path.exists(HISTORICO_ARQUIVO):
        console.print("[yellow]Nenhum histórico encontrado para apagar.[/]")
        return
    confirm = Prompt.ask("[red]Tem certeza que deseja apagar todo o histórico? (s/n)[/]")
    if confirm.lower() == 's':
        os.remove(HISTORICO_ARQUIVO)
        console.print("[green]Histórico apagado com sucesso![/]")
    else:
        console.print("[cyan]Ação cancelada.[/]")

def iniciar_conversao():
    while True:
        modo = Prompt.ask("[cyan]Escolha o modo[/] ([bold]minimalista[/]/[bold]detalhado[/])", default="minimalista").lower()
        if modo not in ["minimalista", "detalhado"]:
            console.print("[red]Modo inválido![/]")
            continue

        base_origem = Prompt.ask("[cyan]Base de ORIGEM (2 a 36 ou 'S' para sair)[/]").strip()
        if base_origem.lower() == 's':
            return
        while not base_valida(base_origem):
            console.print("[red]Base inválida.[/]")
            base_origem = Prompt.ask("Digite novamente ou 'S' para sair").strip()
            if base_origem.lower() == 's':
                return

        valor = Prompt.ask(f"[cyan]Digite o número na base {base_origem}[/]").strip().upper()
        if valor.lower() == 's':
            return
        invalidos = validar_digitos(valor, base_origem)
        if invalidos:
            console.print(f"[red]Caracteres inválidos para base {base_origem}: {', '.join(invalidos)}[/]")
            continue

        base_destino = Prompt.ask("[cyan]Base de DESTINO (2 a 36 ou 'S' para sair)[/]").strip()
        if base_destino.lower() == 's':
            return
        while not base_valida(base_destino):
            console.print("[red]Base inválida.[/]")
            base_destino = Prompt.ask("Digite novamente ou 'S' para sair").strip()
            if base_destino.lower() == 's':
                return

        try:
            decimal = para_decimal_explicando(valor, base_origem, modo)
            convertido = de_decimal_explicando(decimal, base_destino, modo)
            resultado = f"{valor} (base {base_origem}) -> {convertido} (base {base_destino})"
            console.print(f"\n[bold green]✅ Resultado: {resultado}[/]")
            salvar_em_arquivo(resultado)
        except Exception as e:
            console.print(f"[bold red]Erro:[/] {e}")

        continuar = Prompt.ask("Deseja fazer outra conversão? (s/n)", default="s")
        if continuar.lower() != 's':
            break

def menu_principal():
    while True:
        console.print(Panel.fit("[bold cyan]📚 Conversor de Bases Numéricas[/]", subtitle="com Python + Rich", style="bold green"))
        console.print("[bold magenta]1.[/] Iniciar nova conversão")
        console.print("[bold magenta]2.[/] Ver histórico")
        console.print("[bold magenta]3.[/] Apagar histórico")
        console.print("[bold magenta]4.[/] Sair")

        opcao = Prompt.ask("\n[cyan]Escolha uma opção (1-4)[/]")
        if opcao == '1':
            iniciar_conversao()
        elif opcao == '2':
            ver_historico()
        elif opcao == '3':
            apagar_historico()
        elif opcao == '4':
            console.print("\n[bold blue]Até logo! 👋[/]")
            break
        else:
            console.print("[red]Opção inválida![/]")

# Execução principal
if __name__ == "__main__":
    menu_principal()
