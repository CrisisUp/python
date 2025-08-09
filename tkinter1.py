import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox # Para exibir pop-ups de mensagem

# --- Definição de Cores ANSI (ainda úteis para debug no console, mas menos na GUI) ---
# Em GUIs, as cores são definidas pelos widgets, não por códigos ANSI.
# Mas vamos mantê-las por enquanto para os prints de debug se necessário.
class Cores:
    RESET = '\033[0m'
    NEGRITO = '\033[1m'
    VERMELHO = '\033[31m'
    VERDE = '\033[32m'
    AMARELO = '\033[33m'
    AZUL = '\033[34m'
    CIANO = '\033[36m'
    MAGENTA = '\033[35m'

# --- Funções Auxiliares (do seu código atual) ---
# Você precisaria importar ou redefinir funções como formatar_duracao, etc.,
# se a gente fosse colocar tudo em um único arquivo.
# Por enquanto, vamos manter este exemplo simples.

def selecionar_arquivo_audio_ou_video():
    """Abre uma caixa de diálogo para o usuário selecionar um arquivo de áudio/vídeo."""
    # Define os tipos de arquivo que podem ser selecionados
    filetypes = [
        ("Arquivos de Áudio/Vídeo", "*.mp3 *.wav *.flac *.m4a *.ogg *.mp4 *.avi *.mov *.mkv *.webm"),
        ("Todos os arquivos", "*.*")
    ]
    # Abre a caixa de diálogo e retorna o caminho do arquivo selecionado
    filepath = filedialog.askopenfilename(
        title="Selecione um arquivo de Áudio ou Vídeo",
        filetypes=filetypes
    )
    return filepath

def mostrar_mensagem(titulo, mensagem, tipo="info"):
    """Exibe uma caixa de mensagem pop-up."""
    if tipo == "info":
        messagebox.showinfo(titulo, mensagem)
    elif tipo == "warning":
        messagebox.showwarning(titulo, mensagem)
    elif tipo == "error":
        messagebox.showerror(titulo, mensagem)

class AplicativoGUI:
    def __init__(self, master):
        self.master = master
        master.title("Ferramenta de Mídia Python")
        master.geometry("500x300") # Define o tamanho inicial da janela

        # Rótulo para exibir o caminho do arquivo selecionado
        self.label_filepath = tk.Label(master, text="Nenhum arquivo selecionado.")
        self.label_filepath.pack(pady=10) # pack() organiza o widget na janela

        # Botão para selecionar arquivo
        self.btn_selecionar = tk.Button(master, text="Selecionar Arquivo", command=self.ao_clicar_selecionar_arquivo)
        self.btn_selecionar.pack(pady=5)

        # Botão Exemplo de Ação (onde você chamaria suas funções de processamento)
        self.btn_acao_exemplo = tk.Button(master, text="Processar (Exemplo)", command=self.executar_acao_exemplo, state=tk.DISABLED)
        self.btn_acao_exemplo.pack(pady=5)

        # Campo para exibir o resultado ou mensagens
        self.text_resultado = tk.Text(master, height=5, width=40, state=tk.DISABLED)
        self.text_resultado.pack(pady=10)

        self.caminho_arquivo_selecionado = "" # Variável para armazenar o caminho do arquivo

    def ao_clicar_selecionar_arquivo(self):
        self.caminho_arquivo_selecionado = selecionar_arquivo_audio_ou_video()
        if self.caminho_arquivo_selecionado:
            self.label_filepath.config(text=f"Arquivo: {os.path.basename(self.caminho_arquivo_selecionado)}")
            self.btn_acao_exemplo.config(state=tk.NORMAL) # Ativa o botão de ação
            self.atualizar_resultado("Arquivo selecionado com sucesso!")
        else:
            self.label_filepath.config(text="Nenhum arquivo selecionado.")
            self.btn_acao_exemplo.config(state=tk.DISABLED) # Desativa o botão de ação
            self.atualizar_resultado("Seleção de arquivo cancelada.")

    def executar_acao_exemplo(self):
        if self.caminho_arquivo_selecionado:
            self.atualizar_resultado(f"Processando: {os.path.basename(self.caminho_arquivo_selecionado)}...")
            # Aqui você chamaria sua função de transcrição ou corte
            # Ex: resultado = transcrever_audio_whisper(self.caminho_arquivo_selecionado, "base", "transcricoes_gui")
            # Para um exemplo simples:
            import time
            time.sleep(2) # Simula um processamento
            self.atualizar_resultado(f"Processamento concluído para {os.path.basename(self.caminho_arquivo_selecionado)}! (Texto: Exemplo de resultado)")
            mostrar_mensagem("Sucesso", "Processamento de exemplo finalizado!")
        else:
            self.atualizar_resultado("Nenhum arquivo para processar.")
            mostrar_mensagem("Aviso", "Selecione um arquivo primeiro!")

    def atualizar_resultado(self, texto):
        self.text_resultado.config(state=tk.NORMAL) # Habilita para edição
        self.text_resultado.delete(1.0, tk.END) # Limpa o conteúdo
        self.text_resultado.insert(tk.END, texto) # Insere o novo texto
        self.text_resultado.config(state=tk.DISABLED) # Desabilita novamente

if __name__ == "__main__":
    root = tk.Tk() # Cria a janela principal
    app = AplicativoGUI(root) # Cria uma instância do nosso aplicativo GUI
    root.mainloop() # Inicia o loop de eventos da GUI (mantém a janela aberta)