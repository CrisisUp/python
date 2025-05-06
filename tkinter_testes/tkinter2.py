import tkinter as tk
from tkinter import messagebox

# Função para mostrar o texto digitado
def mostrar_texto():
    texto = campo_texto.get("1.0", "end-1c").strip()
    if not texto:
        messagebox.showwarning("Aviso", "Por favor, digite algo antes de enviar.")
        return
    messagebox.showinfo("Texto digitado", f"Você digitou: {texto}")
    campo_texto.delete("1.0", "end")
    atualizar_contador()  # Atualiza o contador após limpar

# Função para salvar o texto em um arquivo
def salvar_em_arquivo():
    texto = campo_texto.get("1.0", "end-1c").strip()
    if not texto:
        messagebox.showwarning("Aviso", "Não há texto para salvar.")
        return
    with open("texto_salvo.txt", "w", encoding="utf-8") as f:
        f.write(texto)
    messagebox.showinfo("Sucesso", "Texto salvo em 'texto_salvo.txt'.")

# Função para atualizar o contador de caracteres
def atualizar_contador(event=None):
    texto = campo_texto.get("1.0", "end-1c")
    contador_var.set(f"{len(texto)} caracteres")

# Criação da janela principal
janela = tk.Tk()
janela.title("Editor de Texto Interativo")
janela.geometry("400x300")
janela.configure(bg="#ffffff")

# Rótulo
tk.Label(janela, text="Digite um texto:", font=("Arial", 12), bg="#ffffff").pack(pady=5)

# Campo de entrada de múltiplas linhas
campo_texto = tk.Text(janela, height=6, width=40, font=("Arial", 11), bg="#f0f0f0")
campo_texto.pack(pady=5)

# Contador de caracteres
contador_var = tk.StringVar()
contador_var.set("0 caracteres")
contador_label = tk.Label(janela, textvariable=contador_var, font=("Arial", 10), bg="#ffffff", fg="#333333")
contador_label.pack()

# Botões
botoes_frame = tk.Frame(janela, bg="#ffffff")
botoes_frame.pack(pady=10)

tk.Button(botoes_frame, text="Mostrar", command=mostrar_texto, width=12, bg="#dff0d8").grid(row=0, column=0, padx=5)
tk.Button(botoes_frame, text="Salvar", command=salvar_em_arquivo, width=12, bg="#d9edf7").grid(row=0, column=1, padx=5)

# Atualiza o contador a cada tecla pressionada
campo_texto.bind("<KeyRelease>", atualizar_contador)

# Inicia o loop da interface
janela.mainloop()
