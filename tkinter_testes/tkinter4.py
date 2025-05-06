import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfilename, askopenfilename

# Funções
def mostrar_texto():
    texto = campo_texto.get("1.0", "end-1c")  # Pega o texto do início até o fim, removendo o último \n
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
    campo_texto.tag_configure("negrito", font=("Arial", 12, "bold"))
    campo_texto.tag_add("negrito", "sel.first", "sel.last")

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

# Botão para Negrito
botao_negrito = tk.Button(janela, text="Negrito", command=aplicar_negrito)
botao_negrito.grid(row=4, column=0, padx=10, pady=5)

# Botão para Alterar Tema
botao_tema = tk.Button(janela, text="Alterar Tema", command=alternar_tema)
botao_tema.grid(row=5, column=0, padx=10, pady=5)

# Atualiza o contador de caracteres ao digitar
campo_texto.bind("<KeyRelease>", lambda event: atualizar_contador())

janela.mainloop()
