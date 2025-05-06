import tkinter as tk
from tkinter import font, filedialog, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def aplicar_estilo(estilo):
    try:
        inicio, fim = campo_texto.index("sel.first"), campo_texto.index("sel.last")
        campo_texto.tag_add(estilo, inicio, fim)
    except tk.TclError:
        messagebox.showwarning("Seleção vazia", "Selecione o texto para aplicar o estilo.")

def mudar_cor():
    try:
        inicio, fim = campo_texto.index("sel.first"), campo_texto.index("sel.last")
        campo_texto.tag_add("cor", inicio, fim)
    except tk.TclError:
        messagebox.showwarning("Seleção vazia", "Selecione o texto para mudar a cor.")

def mudar_fonte(*args):
    atualizar_tags()

def mudar_tamanho(*args):
    atualizar_tags()

def justificar_texto(alinhamento):
    campo_texto.tag_configure("justificado", justify=alinhamento)
    campo_texto.tag_add("justificado", "1.0", "end")

def atualizar_tags():
    nova_fonte = fonte_var.get()
    novo_tamanho = int(tamanho_var.get())
    fonte_formatada = font.Font(family=nova_fonte, size=novo_tamanho)

    campo_texto.configure(font=fonte_formatada)
    campo_texto.tag_configure("negrito", font=fonte_formatada.copy().configure(weight="bold"))
    campo_texto.tag_configure("italico", font=fonte_formatada.copy().configure(slant="italic"))
    campo_texto.tag_configure("cor", foreground="blue")

def salvar_pdf():
    texto = campo_texto.get("1.0", "end-1c")
    if not texto.strip():
        messagebox.showwarning("Aviso", "O texto está vazio.")
        return

    caminho = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if caminho:
        c = canvas.Canvas(caminho, pagesize=A4)
        largura, altura = A4
        linhas = texto.split('\n')
        y = altura - 50
        for linha in linhas:
            c.drawString(40, y, linha)
            y -= 15
        c.save()
        messagebox.showinfo("Salvo", "PDF salvo com sucesso!")

# Janela principal
janela = tk.Tk()
janela.title("Editor de Texto")
janela.geometry("600x500")

# Combobox de fontes e tamanhos
fonte_var = tk.StringVar(value="Arial")
tamanho_var = tk.StringVar(value="12")

fontes_disponiveis = sorted(font.families())
tamanhos = [str(t) for t in range(8, 33, 2)]

tk.OptionMenu(janela, fonte_var, *fontes_disponiveis, command=mudar_fonte).pack(side="left", padx=5)
tk.OptionMenu(janela, tamanho_var, *tamanhos, command=mudar_tamanho).pack(side="left", padx=5)

# Botões de estilo
tk.Button(janela, text="Negrito", command=lambda: aplicar_estilo("negrito")).pack(side="left", padx=5)
tk.Button(janela, text="Itálico", command=lambda: aplicar_estilo("italico")).pack(side="left", padx=5)
tk.Button(janela, text="Cor azul", command=mudar_cor).pack(side="left", padx=5)

# Botões de justificação
tk.Button(janela, text="Esquerda", command=lambda: justificar_texto("left")).pack(side="left", padx=5)
tk.Button(janela, text="Centro", command=lambda: justificar_texto("center")).pack(side="left", padx=5)
tk.Button(janela, text="Direita", command=lambda: justificar_texto("right")).pack(side="left", padx=5)

# Área de texto
campo_texto = tk.Text(janela, wrap="word", undo=True)
campo_texto.pack(expand=True, fill="both", pady=10)

# Botão para salvar em PDF
tk.Button(janela, text="Exportar como PDF", command=salvar_pdf).pack(pady=10)

# Configuração inicial de fontes
atualizar_tags()

janela.mainloop()
