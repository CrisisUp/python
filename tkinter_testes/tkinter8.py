import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.simpledialog import askstring
import time

# Funções
def mostrar_texto():
    texto = campo_texto.get("1.0", "end-1c")
    messagebox.showinfo("Texto digitado", f"Você digitou: {texto}")

def salvar_arquivo():
    arquivo = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if arquivo:
        with open(arquivo, "w") as f:
            f.write(campo_texto.get("1.0", "end-1c"))

def abrir_arquivo():
    arquivo = askopenfilename(filetypes=[("Text files", "*.txt")])
    if arquivo:
        with open(arquivo, "r") as f:
            texto = f.read()
            campo_texto.delete("1.0", "end")
            campo_texto.insert("1.0", texto)

def aplicar_negrito():
    try:
        if campo_texto.tag_ranges(tk.SEL):
            campo_texto.tag_configure("negrito", font=("Arial", 12, "bold"))
            campo_texto.tag_add("negrito", "sel.first", "sel.last")
        else:
            messagebox.showwarning("Aviso", "Selecione um texto para aplicar o negrito.")
    except tk.TclError:
        messagebox.showwarning("Aviso", "Nenhum texto selecionado!")

def aplicar_italico():
    try:
        if campo_texto.tag_ranges(tk.SEL):
            current_font = campo_texto.tag_cget("sel", "font")  # Pega a fonte atual
            if current_font:
                # Se houver fonte configurada, usa o tamanho atual
                campo_texto.tag_configure("italico", font=(current_font[0], current_font[1], "italic"))
            else:
                # Se não houver fonte configurada, usa uma fonte padrão
                campo_texto.tag_configure("italico", font=("Arial", 12, "italic"))
            campo_texto.tag_add("italico", "sel.first", "sel.last")
        else:
            messagebox.showwarning("Aviso", "Selecione um texto para aplicar o itálico.")
    except tk.TclError:
        messagebox.showwarning("Aviso", "Nenhum texto selecionado!")

def aplicar_sublinhado():
    try:
        if campo_texto.tag_ranges(tk.SEL):
            campo_texto.tag_configure("sublinhado", underline=True)
            campo_texto.tag_add("sublinhado", "sel.first", "sel.last")
        else:
            messagebox.showwarning("Aviso", "Selecione um texto para aplicar o sublinhado.")
    except tk.TclError:
        messagebox.showwarning("Aviso", "Nenhum texto selecionado!")

def alterar_tamanho_fonte():
    tamanho = askstring("Alterar Tamanho", "Informe o novo tamanho da fonte:")
    if tamanho and tamanho.isdigit():
        campo_texto.config(font=("Arial", int(tamanho)))

def inserir_data_hora():
    data_hora = time.strftime("%d/%m/%Y %H:%M:%S")
    campo_texto.insert(tk.INSERT, data_hora)

def buscar_substituir():
    def substituir():
        texto_busca = entrada_busca.get()
        texto_substituto = entrada_substituto.get()
        if texto_busca and texto_substituto:
            texto = campo_texto.get("1.0", "end-1c")
            novo_texto = texto.replace(texto_busca, texto_substituto)
            campo_texto.delete("1.0", "end")
            campo_texto.insert("1.0", novo_texto)
            busca_popup.destroy()
        else:
            messagebox.showwarning("Aviso", "Texto de busca ou substituição vazio!")

    busca_popup = tk.Toplevel(janela)
    busca_popup.title("Buscar e Substituir")

    tk.Label(busca_popup, text="Texto a buscar:").pack(pady=5)
    entrada_busca = tk.Entry(busca_popup)
    entrada_busca.pack(pady=5)

    tk.Label(busca_popup, text="Texto substituto:").pack(pady=5)
    entrada_substituto = tk.Entry(busca_popup)
    entrada_substituto.pack(pady=5)

    tk.Button(busca_popup, text="Substituir", command=substituir).pack(pady=5)

def atualizar_contador():
    contador.config(text=f"Caracteres: {len(campo_texto.get('1.0', 'end-1c'))}")

def alternar_tema():
    if janela.cget("bg") == "black":
        janela.config(bg="white")
        campo_texto.config(bg="white", fg="black")
    else:
        janela.config(bg="black")
        campo_texto.config(bg="black", fg="white")

# Configuração da Janela
janela = tk.Tk()
janela.title("Editor de Texto")
janela.geometry("400x400")

# Menu
menu = tk.Menu(janela)
janela.config(menu=menu)

# Adicionando um menu "Arquivo"
arquivo_menu = tk.Menu(menu)
menu.add_cascade(label="Arquivo", menu=arquivo_menu)
arquivo_menu.add_command(label="Abrir", command=abrir_arquivo)
arquivo_menu.add_command(label="Salvar", command=salvar_arquivo)
arquivo_menu.add_command(label="Sair", command=janela.quit)

# Adicionando um menu "Editar"
editar_menu = tk.Menu(menu)
menu.add_cascade(label="Editar", menu=editar_menu)
editar_menu.add_command(label="Negrito", command=aplicar_negrito)
editar_menu.add_command(label="Itálico", command=aplicar_italico)
editar_menu.add_command(label="Sublinhado", command=aplicar_sublinhado)
editar_menu.add_command(label="Alterar Tamanho da Fonte", command=alterar_tamanho_fonte)
editar_menu.add_command(label="Inserir Data/Hora", command=inserir_data_hora)
editar_menu.add_command(label="Buscar e Substituir", command=buscar_substituir)

# Label de Texto
texto_label = tk.Label(janela, text="Digite um texto:")
texto_label.grid(row=0, column=0, padx=10, pady=5)

# Widget Text
campo_texto = tk.Text(janela, height=10, width=40)
campo_texto.grid(row=1, column=0, padx=10, pady=5)

# Contador de caracteres
contador = tk.Label(janela, text="Caracteres: 0")
contador.grid(row=2, column=0, padx=10, pady=5)

# Botão para Mostrar o Texto
botao = tk.Button(janela, text="Mostrar", command=mostrar_texto)
botao.grid(row=3, column=0, padx=10, pady=5)

# Botão para Alterar Tema
botao_tema = tk.Button(janela, text="Alterar Tema", command=alternar_tema)
botao_tema.grid(row=4, column=0, padx=10, pady=5)

# Atualiza o contador de caracteres ao digitar
campo_texto.bind("<KeyRelease>", lambda event: atualizar_contador())

janela.mainloop()
