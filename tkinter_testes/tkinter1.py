import tkinter as tk
from tkinter import messagebox

def mostrar_texto():
    texto = campo_texto.get("1.0", "end-1c")  # Pega o texto do início até o fim, removendo o último \n
    messagebox.showinfo("Texto digitado", f"Você digitou: {texto}")

janela = tk.Tk()
janela.title("Exemplo com Text")
janela.geometry("300x200")

tk.Label(janela, text="Digite um texto:").pack(pady=5)

# Widget Text para várias linhas
campo_texto = tk.Text(janela, height=5, width=30)
campo_texto.pack(pady=5)

tk.Button(janela, text="Mostrar", command=mostrar_texto).pack(pady=10)

janela.mainloop()
