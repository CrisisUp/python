import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from tkinter import font as tkfont
from bs4 import BeautifulSoup  # Instale com: pip install beautifulsoup4

def aplicar_estilo(tag, font_options):
    try:
        start, end = campo_texto.index("sel.first"), campo_texto.index("sel.last")
        campo_texto.tag_add(tag, start, end)
        campo_texto.tag_configure(tag, font=font_options)
    except tk.TclError:
        messagebox.showwarning("Aviso", "Selecione um trecho do texto para aplicar o estilo.")

def aplicar_cor():
    cor = colorchooser.askcolor()[1]
    if cor:
        try:
            start, end = campo_texto.index("sel.first"), campo_texto.index("sel.last")
            tag_cor = f"cor_{cor}"
            campo_texto.tag_add(tag_cor, start, end)
            campo_texto.tag_configure(tag_cor, foreground=cor)
        except tk.TclError:
            messagebox.showwarning("Aviso", "Selecione um trecho do texto para aplicar a cor.")

def aplicar_negrito():
    aplicar_estilo("negrito", tkfont.Font(campo_texto, campo_texto.cget("font")).copy().actual() | {'weight': 'bold'})

def aplicar_italico():
    aplicar_estilo("italico", tkfont.Font(campo_texto, campo_texto.cget("font")).copy().actual() | {'slant': 'italic'})

def aplicar_sublinhado():
    aplicar_estilo("sublinhado", tkfont.Font(campo_texto, campo_texto.cget("font")).copy().actual() | {'underline': True})

def salvar_arquivo():
    arquivo = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
    if arquivo:
        texto_final = campo_texto.get("1.0", "end-1c")
        html = texto_final
        tags = campo_texto.tag_names()

        for tag in tags:
            if tag in ["negrito", "italico", "sublinhado"] or tag.startswith("cor_"):
                ranges = campo_texto.tag_ranges(tag)
                for i in range(0, len(ranges), 2):
                    start = ranges[i]
                    end = ranges[i+1]
                    trecho = campo_texto.get(start, end)
                    if not trecho.strip():
                        continue
                    if tag.startswith("cor_"):
                        cor = tag.replace("cor_", "")
                        styled = f'<span style="color:{cor}">{trecho}</span>'
                    elif tag == "negrito":
                        styled = f"<b>{trecho}</b>"
                    elif tag == "italico":
                        styled = f"<i>{trecho}</i>"
                    elif tag == "sublinhado":
                        styled = f"<u>{trecho}</u>"
                    html = html.replace(trecho, styled, 1)

        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(f"<html><body>{html}</body></html>")

def abrir_arquivo():
    arquivo = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")])
    if arquivo:
        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo_html = f.read()

        soup = BeautifulSoup(conteudo_html, "html.parser")
        campo_texto.delete("1.0", tk.END)

        def inserir_com_tag(tag, texto, cor=None):
            pos = campo_texto.index(tk.INSERT)
            campo_texto.insert(tk.INSERT, texto)
            fim = campo_texto.index(tk.INSERT)
            if tag == "negrito":
                aplicar_estilo(tag, tkfont.Font(weight="bold"))
            elif tag == "italico":
                aplicar_estilo(tag, tkfont.Font(slant="italic"))
            elif tag == "sublinhado":
                aplicar_estilo(tag, tkfont.Font(underline=True))
            elif tag == "cor" and cor:
                campo_texto.tag_add(f"cor_{cor}", pos, fim)
                campo_texto.tag_configure(f"cor_{cor}", foreground=cor)
            campo_texto.tag_add(tag if tag != "cor" else f"cor_{cor}", pos, fim)

        for elemento in soup.body.descendants:
            if isinstance(elemento, str):
                campo_texto.insert(tk.END, elemento)
            elif elemento.name == "b":
                inserir_com_tag("negrito", elemento.text)
            elif elemento.name == "i":
                inserir_com_tag("italico", elemento.text)
            elif elemento.name == "u":
                inserir_com_tag("sublinhado", elemento.text)
            elif elemento.name == "span" and elemento.has_attr("style"):
                cor = elemento["style"].split(":")[-1]
                inserir_com_tag("cor", elemento.text, cor.strip())

# Interface
janela = tk.Tk()
janela.title("Editor de Texto Tkinter")

campo_texto = tk.Text(janela, wrap="word", undo=True, font=("Arial", 12))
campo_texto.pack(expand=True, fill="both")

frame_botoes = tk.Frame(janela)
frame_botoes.pack()

tk.Button(frame_botoes, text="Negrito", command=aplicar_negrito).pack(side="left", padx=2)
tk.Button(frame_botoes, text="Itálico", command=aplicar_italico).pack(side="left", padx=2)
tk.Button(frame_botoes, text="Sublinhado", command=aplicar_sublinhado).pack(side="left", padx=2)
tk.Button(frame_botoes, text="Cor da Fonte", command=aplicar_cor).pack(side="left", padx=2)
tk.Button(frame_botoes, text="Salvar", command=salvar_arquivo).pack(side="left", padx=2)
tk.Button(frame_botoes, text="Abrir", command=abrir_arquivo).pack(side="left", padx=2)

janela.mainloop()
