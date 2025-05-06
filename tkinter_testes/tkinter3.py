import tkinter as tk
from tkinter import messagebox

# =================== Funções ===================

def mostrar_texto():
    texto = campo_texto.get("1.0", "end-1c").strip()
    if not texto:
        messagebox.showwarning("Aviso", "Por favor, digite algo antes de enviar.")
        return
    messagebox.showinfo("Texto digitado", f"Você digitou: {texto}")
    campo_texto.delete("1.0", "end")
    atualizar_contador()

def salvar_em_arquivo():
    texto = campo_texto.get("1.0", "end-1c").strip()
    if not texto:
        messagebox.showwarning("Aviso", "Não há texto para salvar.")
        return
    with open("texto_salvo.txt", "w", encoding="utf-8") as f:
        f.write(texto)
    messagebox.showinfo("Sucesso", "Texto salvo em 'texto_salvo.txt'.")

def atualizar_contador(event=None):
    texto = campo_texto.get("1.0", "end-1c")
    contador_var.set(f"{len(texto)} caracteres")

def alternar_tema():
    global tema_escuro
    tema_escuro = not tema_escuro
    aplicar_tema()

def aplicar_tema():
    if tema_escuro:
        cor_fundo = "#2e2e2e"
        cor_texto = "#ffffff"
        cor_campo = "#3c3f41"
        cor_botao = "#444"
    else:
        cor_fundo = "#ffffff"
        cor_texto = "#000000"
        cor_campo = "#f0f0f0"
        cor_botao = "#d9edf7"

    janela.configure(bg=cor_fundo)
    rotulo.configure(bg=cor_fundo, fg=cor_texto)
    campo_texto.configure(bg=cor_campo, fg=cor_texto, insertbackground=cor_texto)
    contador_label.configure(bg=cor_fundo, fg=cor_texto)
    botoes_frame.configure(bg=cor_fundo)
    botao_mostrar.configure(bg=cor_botao)
    botao_salvar.configure(bg=cor_botao)
    botao_tema.configure(bg=cor_botao)

# =================== Interface ===================

janela = tk.Tk()
janela.title("Editor de Texto Interativo")
janela.geometry("400x320")

tema_escuro = False

rotulo = tk.Label(janela, text="Digite um texto:", font=("Arial", 12))
rotulo.pack(pady=5)

campo_texto = tk.Text(janela, height=6, width=40, font=("Arial", 11))
campo_texto.pack(pady=5)

contador_var = tk.StringVar()
contador_var.set("0 caracteres")
contador_label = tk.Label(janela, textvariable=contador_var, font=("Arial", 10))
contador_label.pack()

botoes_frame = tk.Frame(janela)
botoes_frame.pack(pady=10)

botao_mostrar = tk.Button(botoes_frame, text="Mostrar", command=mostrar_texto, width=12)
botao_mostrar.grid(row=0, column=0, padx=5)

botao_salvar = tk.Button(botoes_frame, text="Salvar", command=salvar_em_arquivo, width=12)
botao_salvar.grid(row=0, column=1, padx=5)

# Botão de tema
botao_tema = tk.Button(janela, text="Alternar Tema", command=alternar_tema)
botao_tema.pack(pady=5)

campo_texto.bind("<KeyRelease>", atualizar_contador)
aplicar_tema()
janela.mainloop()
