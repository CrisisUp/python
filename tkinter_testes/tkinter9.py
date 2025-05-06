import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import tkinter.font as tkFont
import time

def mostrar_texto():
    texto = campo_texto.get("1.0", "end-1c")
    messagebox.showinfo("Texto digitado", f"Você digitou: {texto}")

def salvar_arquivo():
    arquivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if arquivo:
        with open(arquivo, "w") as f:
            f.write(campo_texto.get("1.0", "end-1c"))

def abrir_arquivo():
    arquivo = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if arquivo:
        with open(arquivo, "r") as f:
            texto = f.read()
            campo_texto.delete("1.0", "end")
            campo_texto.insert("1.0", texto)

def aplicar_estilo(tag, **kwargs):
    try:
        if campo_texto.tag_ranges(tk.SEL):
            campo_texto.tag_configure(tag, **kwargs)
            campo_texto.tag_add(tag, "sel.first", "sel.last")
        else:
            messagebox.showwarning("Aviso", f"Selecione um texto para aplicar o estilo.")
    except tk.TclError:
        messagebox.showwarning("Aviso", "Erro ao aplicar estilo.")

def aplicar_negrito():
    fonte_atual = tkFont.Font(font=campo_texto.cget("font"))
    nova_fonte = fonte_atual.copy()
    nova_fonte.configure(weight="bold")
    aplicar_estilo("negrito", font=nova_fonte)

def aplicar_italico():
    fonte_atual = tkFont.Font(font=campo_texto.cget("font"))
    nova_fonte = fonte_atual.copy()
    nova_fonte.configure(slant="italic")
    aplicar_estilo("italico", font=nova_fonte)

def aplicar_sublinhado():
    aplicar_estilo("sublinhado", underline=True)

def alterar_tamanho_fonte():
    tamanho = simpledialog.askstring("Alterar Tamanho", "Informe o novo tamanho da fonte:")
    if tamanho and tamanho.isdigit():
        fonte = tkFont.Font(font=campo_texto.cget("font"))
        nova_fonte = fonte.copy()
        nova_fonte.configure(size=int(tamanho))
        campo_texto.configure(font=nova_fonte)

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
            popup.destroy()
        else:
            messagebox.showwarning("Aviso", "Campos vazios.")

    popup = tk.Toplevel(janela)
    popup.title("Buscar e Substituir")
    tk.Label(popup, text="Buscar:").pack(pady=5)
    entrada_busca = tk.Entry(popup)
    entrada_busca.pack(pady=5)
    tk.Label(popup, text="Substituir por:").pack(pady=5)
    entrada_substituto = tk.Entry(popup)
    entrada_substituto.pack(pady=5)
    tk.Button(popup, text="Substituir", command=substituir).pack(pady=10)

def atualizar_contador(event=None):
    texto = campo_texto.get("1.0", "end-1c")
    contador.config(text=f"Caracteres: {len(texto)}")

def alternar_tema():
    atual = janela.cget("bg")
    if atual == "white":
        janela.config(bg="black")
        campo_texto.config(bg="black", fg="white")
    else:
        janela.config(bg="white")
        campo_texto.config(bg="white", fg="black")

# Janela principal
janela = tk.Tk()
janela.title("Editor de Texto")
janela.geometry("500x450")
janela.config(bg="white")

# Menu
menu = tk.Menu(janela)
janela.config(menu=menu)

arquivo_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Arquivo", menu=arquivo_menu)
arquivo_menu.add_command(label="Abrir", command=abrir_arquivo)
arquivo_menu.add_command(label="Salvar", command=salvar_arquivo)
arquivo_menu.add_command(label="Sair", command=janela.quit)

editar_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Editar", menu=editar_menu)
editar_menu.add_command(label="Negrito", command=aplicar_negrito)
editar_menu.add_command(label="Itálico", command=aplicar_italico)
editar_menu.add_command(label="Sublinhado", command=aplicar_sublinhado)
editar_menu.add_command(label="Alterar Tamanho da Fonte", command=alterar_tamanho_fonte)
editar_menu.add_command(label="Inserir Data/Hora", command=inserir_data_hora)
editar_menu.add_command(label="Buscar e Substituir", command=buscar_substituir)

# Widgets
tk.Label(janela, text="Digite seu texto:", bg="white").pack(pady=5)
campo_texto = tk.Text(janela, height=15, width=60)
campo_texto.pack(pady=5)

contador = tk.Label(janela, text="Caracteres: 0", bg="white")
contador.pack()

campo_texto.bind("<KeyRelease>", atualizar_contador)

tk.Button(janela, text="Mostrar", command=mostrar_texto).pack(pady=5)
tk.Button(janela, text="Alterar Tema", command=alternar_tema).pack()

janela.mainloop()
