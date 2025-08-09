import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
import time # Para simular um atraso em algumas operações da GUI
import glob # Para limpar arquivos temporários

# Importa as bibliotecas para processamento de áudio/vídeo
from pydub import AudioSegment
from pydub.utils import mediainfo
from pydub.exceptions import CouldntDecodeError
# A linha abaixo precisa do moviepy instalado, conforme resolvemos antes
from moviepy.editor import VideoFileClip


# --- Definição de Cores ANSI (ainda úteis para logs internos ou fallback, mas GUI define suas próprias cores) ---
class Cores:
    RESET = '\033[0m'
    NEGRITO = '\033[1m'
    VERMELHO = '\033[31m'
    VERDE = '\033[32m'
    AMARELO = '\033[33m'
    AZUL = '\033[34m'
    CIANO = '\033[36m'
    MAGENTA = '\033[35m'

# --- Funções Auxiliares Comuns ---
CONFIG_FILE = "media_tool_config.json" # Arquivo de configuração único

def carregar_config():
    """Carrega as configurações do arquivo JSON."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"{Cores.AMARELO}Aviso: Arquivo de configuração '{CONFIG_FILE}' corrompido. Criando um novo.{Cores.RESET}")
            return {}
    return {}

def salvar_config(config):
    """Salva as configurações no arquivo JSON."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def limpar_tela():
    """Limpa a tela do terminal (menos relevante para GUI, mas mantido)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def formatar_duracao(segundos):
    """Formata a duração de segundos para HH:MM:SS."""
    minutos, segundos_restantes = divmod(int(segundos), 60)
    horas, minutos_restantes = divmod(minutos, 60)
    return f"{horas:02d}:{minutos_restantes:02d}:{segundos_restantes:02d}"

def limpar_temporarios():
    """Remove quaisquer arquivos temporários de chunk restantes."""
    temp_files = glob.glob("temp_chunk_*.wav")
    for f in temp_files:
        try:
            os.remove(f)
        except OSError as e:
            print(f"{Cores.AMARELO}Aviso: Não foi possível remover o arquivo temporário '{f}': {e}{Cores.RESET}")

# --- Funções de Processamento (Adaptadas para GUI) ---

# Transcrição de Áudio
# A função Whisper será importada aqui dentro da função,
# pois o modelo só precisa ser carregado uma vez para evitar atrasos na GUI.
_whisper_model = None # Variável global para armazenar o modelo Whisper carregado

def get_whisper_model(model_name="base", progress_callback=None):
    """Carrega o modelo Whisper uma única vez."""
    global _whisper_model
    if _whisper_model is None:
        if progress_callback:
            progress_callback(f"Carregando modelo Whisper '{model_name}'... (Primeira vez pode demorar e baixar dados)")
        try:
            import whisper # Importa whisper aqui para carregamento sob demanda
            _whisper_model = whisper.load_model(model_name)
            if progress_callback:
                progress_callback("Modelo Whisper carregado com sucesso!")
        except Exception as e:
            if progress_callback:
                progress_callback(f"Erro ao carregar modelo Whisper: {e}", "error")
            raise e
    return _whisper_model

def transcrever_audio_gui(caminho_audio, modelo_whisper, output_dir, progress_callback):
    """Transcreve áudio para texto para a GUI."""
    progress_callback("Iniciando transcrição...", "info")
    
    if not os.path.exists(caminho_audio):
        progress_callback(f"Erro: Arquivo '{caminho_audio}' não encontrado.", "error")
        return "Erro: Arquivo não encontrado."

    os.makedirs(output_dir, exist_ok=True)
    
    try:
        model = get_whisper_model(modelo_whisper, progress_callback)
        progress_callback(f"Preparando áudio para transcrição...", "info")

        audio = AudioSegment.from_file(caminho_audio)
        audio_length_ms = len(audio)
        chunk_length_ms = 15000 # 15 segundos

        chunks = []
        for i in range(0, audio_length_ms, chunk_length_ms):
            chunks.append(audio[i:i + chunk_length_ms])

        full_transcription = []
        
        progress_callback(f"Transcrevendo {len(chunks)} segmentos...", "info")
        for i, chunk in enumerate(chunks):
            temp_chunk_path = f"temp_chunk_{i}.wav"
            chunk.export(temp_chunk_path, format="wav")

            # Aqui você pode tentar dar um feedback mais granular com base no chunk_length_ms
            progress_callback(f"Processando segmento {i+1}/{len(chunks)}...", "progress")
            
            result = model.transcribe(temp_chunk_path, language="pt", fp16=False, suppress_tokens=[-1])
            full_transcription.append(result["text"])
            os.remove(temp_chunk_path)
            
            # Atualiza o progresso visualmente (se a GUI tiver uma barra)
            # A lógica da barra de progresso do Tkinter será na aba, não aqui.

        texto_transcrito = " ".join(full_transcription).strip()
        
        # Salva o texto em um arquivo
        nome_arquivo_base = os.path.splitext(os.path.basename(caminho_audio))[0]
        caminho_arquivo_saida = os.path.join(output_dir, f"{nome_arquivo_base}_transcricao.txt")
        
        with open(caminho_arquivo_saida, "w", encoding="utf-8") as f:
            f.write(texto_transcrito)
        
        progress_callback(f"Transcrição concluída! Salva em: '{caminho_arquivo_saida}'", "success")
        return texto_transcrito
        
    except Exception as e:
        progress_callback(f"Erro na transcrição: {e}. Verifique FFmpeg/modelo.", "error")
        return f"Erro: {e}"
    finally:
        limpar_temporarios() # Garante a limpeza, mesmo se ocorrer um erro


# Corte de Áudio/Vídeo
def cortar_midia_gui(caminho_entrada, caminho_saida, inicio_seg, fim_seg, is_video=True, progress_callback=None):
    """Corta áudio ou vídeo para a GUI."""
    progress_callback("Iniciando corte...", "info")

    if not os.path.exists(caminho_entrada):
        progress_callback(f"Erro: Arquivo '{caminho_entrada}' não encontrado.", "error")
        return False

    clip = None
    try:
        if is_video:
            clip = VideoFileClip(caminho_entrada)
        else:
            clip = AudioSegment.from_file(caminho_entrada)
        
        duracao_total_seg = clip.duration if is_video else (len(clip) / 1000)

        if inicio_seg < 0 or fim_seg > duracao_total_seg or inicio_seg >= fim_seg:
            progress_callback(f"Erro: Tempos de corte inválidos. Mídia tem {formatar_duracao(duracao_total_seg)}.", "error")
            return False

        progress_callback(f"Cortando de {formatar_duracao(inicio_seg)} a {formatar_duracao(fim_seg)}...", "info")
        
        if is_video:
            segmento_cortado = clip.subclip(inicio_seg, fim_seg)
            # MoviePy já tem barra de progresso no write_videofile
            segmento_cortado.write_videofile(caminho_saida, codec="libx264", audio_codec="aac")
        else:
            # Pydub trabalha em ms
            segmento_cortado = clip[int(inicio_seg * 1000):int(fim_seg * 1000)]
            segmento_cortado.export(caminho_saida, format=caminho_saida.split('.')[-1])

        progress_callback(f"Corte concluído! Salvo em: '{caminho_saida}'", "success")
        return True

    except (CouldntDecodeError, Exception) as e: # Catch all general exceptions for moviepy/pydub errors
        error_msg = f"Erro no corte: {e}. Verifique se o FFmpeg está instalado e o arquivo não está corrompido."
        progress_callback(error_msg, "error")
        return False
    finally:
        if clip and is_video: # close only for VideoFileClip
            clip.close()


def obter_duracao_midia_gui(caminho_midia, is_video=True):
    """Obtém a duração de áudio ou vídeo para a GUI."""
    clip = None
    try:
        if is_video:
            clip = VideoFileClip(caminho_midia)
            duracao = clip.duration
        else:
            audio = AudioSegment.from_file(caminho_midia)
            duracao = len(audio) / 1000 # Convertendo ms para segundos
        return duracao
    except Exception as e:
        print(f"Erro ao obter duração: {e}") # Log para console
        return None
    finally:
        if clip and is_video:
            clip.close()


# --- Classes Tkinter para as Abas ---

class TranscribeTab(tk.Frame):
    def __init__(self, master, config_ref):
        super().__init__(master)
        self.config = config_ref
        self.caminho_audio = ""
        
        # Widgets
        ttk.Label(self, text="Caminho do Arquivo de Áudio:").pack(pady=5)
        self.entry_audio_path = ttk.Entry(self, width=60)
        self.entry_audio_path.pack(pady=5)
        ttk.Button(self, text="Selecionar Arquivo", command=self.selecionar_audio).pack(pady=5)

        ttk.Label(self, text="Modelo Whisper:").pack(pady=5)
        self.modelos_disponiveis = ["tiny", "base", "small", "medium", "large"]
        self.modelo_selecionado = tk.StringVar(self)
        # Tenta carregar o último modelo usado
        last_model = self.config.get('ultimo_modelo_whisper', 'base')
        if last_model not in self.modelos_disponiveis:
            last_model = 'base' # Fallback se o último for inválido
        self.modelo_selecionado.set(last_model)
        ttk.OptionMenu(self, self.modelo_selecionado, self.modelo_selecionado.get(), *self.modelos_disponiveis, command=self.salvar_modelo_selecionado).pack(pady=5)

        ttk.Label(self, text="Diretório de Saída:").pack(pady=5)
        self.entry_output_dir = ttk.Entry(self, width=60)
        # Tenta carregar o último diretório usado
        last_output_dir = self.config.get('ultimo_diretorio_saida_transcricao', 'transcricoes')
        self.entry_output_dir.insert(0, last_output_dir)
        self.entry_output_dir.pack(pady=5)

        self.btn_transcrever = ttk.Button(self, text="Transcrever Áudio", command=self.iniciar_transcricao)
        self.btn_transcrever.pack(pady=10)

        # Área de log/resultado
        ttk.Label(self, text="Status/Resultado:").pack(pady=5)
        self.text_resultado = tk.Text(self, height=10, width=70, state=tk.DISABLED, wrap=tk.WORD)
        self.text_resultado.pack(pady=5)

        # Barra de progresso (para o futuro, se necessário uma barra além do texto de status)
        # self.progress_bar = ttk.Progressbar(self, orient='horizontal', length=400, mode='determinate')
        # self.progress_bar.pack(pady=5)

    def selecionar_audio(self):
        filetypes = [("Arquivos de Áudio", "*.mp3 *.wav *.flac *.m4a *.ogg"), ("Todos os arquivos", "*.*")]
        filepath = filedialog.askopenfilename(title="Selecione um arquivo de Áudio", filetypes=filetypes)
        if filepath:
            self.caminho_audio = filepath
            self.entry_audio_path.delete(0, tk.END)
            self.entry_audio_path.insert(0, filepath)
            self.update_status(f"Arquivo selecionado: {os.path.basename(filepath)}", "info")
        else:
            self.update_status("Seleção de arquivo cancelada.", "info")

    def salvar_modelo_selecionado(self, model_name):
        self.config['ultimo_modelo_whisper'] = model_name
        salvar_config(self.config)
        self.update_status(f"Modelo Whisper definido para: {model_name}", "info")

    def update_status(self, message, message_type="info"):
        self.text_resultado.config(state=tk.NORMAL)
        self.text_resultado.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.text_resultado.config(state=tk.DISABLED)
        self.text_resultado.see(tk.END) # Auto-scroll to end

        if message_type == "error":
            messagebox.showerror("Erro na Transcrição", message)
        elif message_type == "success":
            messagebox.showinfo("Sucesso", message)
            
    def iniciar_transcricao(self):
        audio_path = self.entry_audio_path.get()
        model_name = self.modelo_selecionado.get()
        output_dir = self.entry_output_dir.get()

        if not audio_path:
            self.update_status("Por favor, selecione um arquivo de áudio primeiro.", "warning")
            return
        
        # Salva o diretório de saída para a próxima vez
        self.config['ultimo_diretorio_saida_transcricao'] = output_dir
        salvar_config(self.config)

        self.update_status("Processando...", "info")
        self.btn_transcrever.config(state=tk.DISABLED) # Desabilita o botão para evitar cliques múltiplos
        # Inicia a transcrição em uma nova thread
        threading.Thread(target=self._executar_transcricao_thread, args=(audio_path, model_name, output_dir)).start()

    def _executar_transcricao_thread(self, audio_path, model_name, output_dir):
        # A lógica de transcrição está aqui, no background
        try:
            transcricao_final = transcrever_audio_gui(audio_path, model_name, output_dir, self.update_status)
            # Atualiza o resultado principal (se for o caso)
            self.update_status("Transcrição finalizada. Verifique o resultado na área de status.", "info")
            if "Erro" in transcricao_final: # Se a função de transcrição retornar um erro
                 self.update_status(f"Falha na Transcrição: {transcricao_final}", "error")
        except Exception as e:
            self.update_status(f"Erro inesperado no thread de transcrição: {e}", "error")
        finally:
            self.master.after(0, self.btn_transcrever.config, {'state': tk.NORMAL}) # Reabilita o botão na thread principal


class CutVideoAudioTab(tk.Frame):
    def __init__(self, master, config_ref):
        super().__init__(master)
        self.config = config_ref
        self.caminho_midia = ""
        self.is_video = tk.BooleanVar(value=True) # Variável para controlar se é vídeo ou áudio
        self.duracao_midia = 0.0

        # Widgets
        ttk.Label(self, text="Caminho do Arquivo (Vídeo/Áudio):").pack(pady=5)
        self.entry_media_path = ttk.Entry(self, width=60)
        self.entry_media_path.pack(pady=5)
        ttk.Button(self, text="Selecionar Arquivo", command=self.selecionar_midia).pack(pady=5)

        ttk.Radiobutton(self, text="Vídeo", variable=self.is_video, value=True, command=self.on_media_type_change).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Radiobutton(self, text="Áudio", variable=self.is_video, value=False, command=self.on_media_type_change).pack(side=tk.LEFT, padx=10, pady=5)
        self.is_video.set(True) # Padrão para vídeo

        ttk.Label(self, text="Duração Total:").pack(pady=5)
        self.label_duration = ttk.Label(self, text="00:00:00 (0.00s)")
        self.label_duration.pack(pady=5)

        ttk.Label(self, text="Início do Corte (segundos):").pack(pady=5)
        self.entry_start_time = ttk.Entry(self, width=15)
        self.entry_start_time.pack(pady=5)

        ttk.Label(self, text="Fim do Corte (segundos):").pack(pady=5)
        self.entry_end_time = ttk.Entry(self, width=15)
        self.entry_end_time.pack(pady=5)

        ttk.Label(self, text="Diretório de Saída:").pack(pady=5)
        self.entry_output_dir = ttk.Entry(self, width=60)
        # Tenta carregar o último diretório usado
        last_output_dir_video = self.config.get('ultimo_diretorio_saida_video', '')
        self.entry_output_dir.insert(0, last_output_dir_video)
        self.entry_output_dir.pack(pady=5)
        ttk.Button(self, text="Selecionar Diretório de Saída", command=self.selecionar_diretorio_saida).pack(pady=5)


        self.btn_cortar = ttk.Button(self, text="Cortar Mídia", command=self.iniciar_corte)
        self.btn_cortar.pack(pady=10)

        # Área de log/resultado
        ttk.Label(self, text="Status/Resultado:").pack(pady=5)
        self.text_resultado = tk.Text(self, height=10, width=70, state=tk.DISABLED, wrap=tk.WORD)
        self.text_resultado.pack(pady=5)

    def on_media_type_change(self):
        # Limpa o caminho e a duração quando o tipo de mídia muda
        self.caminho_midia = ""
        self.entry_media_path.delete(0, tk.END)
        self.label_duration.config(text="00:00:00 (0.00s)")
        self.update_status(f"Tipo de mídia alterado para: {'Vídeo' if self.is_video.get() else 'Áudio'}", "info")


    def selecionar_midia(self):
        if self.is_video.get():
            filetypes = [("Arquivos de Vídeo", "*.mp4 *.avi *.mov *.mkv *.webm"), ("Todos os arquivos", "*.*")]
            title = "Selecione um arquivo de Vídeo"
        else:
            filetypes = [("Arquivos de Áudio", "*.mp3 *.wav *.flac *.m4a *.ogg"), ("Todos os arquivos", "*.*")]
            title = "Selecione um arquivo de Áudio"

        filepath = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if filepath:
            self.caminho_midia = filepath
            self.entry_media_path.delete(0, tk.END)
            self.entry_media_path.insert(0, filepath)
            
            self.update_status(f"Arquivo selecionado: {os.path.basename(filepath)}", "info")
            self.obter_e_mostrar_duracao()
        else:
            self.update_status("Seleção de arquivo cancelada.", "info")
            self.label_duration.config(text="00:00:00 (0.00s)")


    def selecionar_diretorio_saida(self):
        directory = filedialog.askdirectory(title="Selecione o Diretório de Saída")
        if directory:
            self.entry_output_dir.delete(0, tk.END)
            self.entry_output_dir.insert(0, directory)
            self.update_status(f"Diretório de saída selecionado: {directory}", "info")
        else:
            self.update_status("Seleção de diretório cancelada.", "info")


    def obter_e_mostrar_duracao(self):
        self.duracao_midia = obter_duracao_midia_gui(self.caminho_midia, self.is_video.get())
        if self.duracao_midia is not None:
            self.label_duration.config(text=f"{formatar_duracao(self.duracao_midia)} ({self.duracao_midia:.2f}s)")
            self.update_status(f"Duração do arquivo: {formatar_duracao(self.duracao_midia)}", "info")
        else:
            self.label_duration.config(text="Erro ao obter duração.")
            self.update_status("Não foi possível obter a duração do arquivo. Verifique se o FFmpeg está configurado e o arquivo está válido.", "error")

    def update_status(self, message, message_type="info"):
        self.text_resultado.config(state=tk.NORMAL)
        self.text_resultado.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.text_resultado.config(state=tk.DISABLED)
        self.text_resultado.see(tk.END) # Auto-scroll to end

        if message_type == "error":
            messagebox.showerror("Erro na Operação", message)
        elif message_type == "success":
            messagebox.showinfo("Sucesso", message)

    def iniciar_corte(self):
        media_path = self.entry_media_path.get()
        output_dir = self.entry_output_dir.get()
        
        if not media_path:
            self.update_status("Por favor, selecione um arquivo para cortar.", "warning")
            return

        try:
            start_time = float(self.entry_start_time.get().replace(',', '.'))
            end_time = float(self.entry_end_time.get().replace(',', '.'))
        except ValueError:
            self.update_status("Tempos de início e fim devem ser números válidos.", "error")
            return

        # Salva o último diretório de saída para vídeos/áudios
        self.config['ultimo_diretorio_saida_video'] = output_dir
        salvar_config(self.config)

        self.update_status("Processando corte...", "info")
        self.btn_cortar.config(state=tk.DISABLED)
        threading.Thread(target=self._executar_corte_thread, args=(media_path, output_dir, start_time, end_time)).start()

    def _executar_corte_thread(self, media_path, output_dir, start_time, end_time):
        try:
            nome_arquivo_original, extensao = os.path.splitext(os.path.basename(media_path))
            extensao_limpa = extensao.lstrip('.')
            if not extensao_limpa:
                extensao_limpa = 'mp4' if self.is_video.get() else 'wav' # Padrão para mp4/wav
            
            output_filepath = os.path.join(output_dir, f"{nome_arquivo_original}_cortado.{extensao_limpa}")

            sucesso = cortar_midia_gui(media_path, output_filepath, start_time, end_time, self.is_video.get(), self.update_status)
            if sucesso:
                self.update_status(f"Corte finalizado. Arquivo salvo em: {output_filepath}", "info")
            else:
                self.update_status(f"Falha no corte para {os.path.basename(media_path)}. Verifique os logs.", "error")
        except Exception as e:
            self.update_status(f"Erro inesperado no thread de corte: {e}", "error")
        finally:
            self.master.after(0, self.btn_cortar.config, {'state': tk.NORMAL})


class MainApplication:
    def __init__(self, master):
        self.master = master
        master.title("Ferramenta de Transcrição e Corte de Mídia")
        master.geometry("700x600") # Tamanho inicial da janela
        
        self.config = carregar_config() # Carrega configurações globais

        # Cria o Notebook (widget de abas)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Adiciona a aba de Transcrição
        self.transcribe_tab = TranscribeTab(self.notebook, self.config)
        self.notebook.add(self.transcribe_tab, text="Transcrever Áudio")

        # Adiciona a aba de Corte
        self.cut_tab = CutVideoAudioTab(self.notebook, self.config)
        self.notebook.add(self.cut_tab, text="Cortar Vídeo/Áudio")

        # Configura o fechamento da janela para limpar temporários
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        limpar_temporarios()
        self.master.destroy() # Fecha a janela


if __name__ == "__main__":
    # Importa whisper aqui, se o usuário tiver instalado.
    # Apenas para o import inicial funcionar, o load_model real é lazy-loaded.
    try:
        import whisper
    except ImportError:
        messagebox.showerror("Erro de Dependência", "A biblioteca 'openai-whisper' não está instalada. "
                                                 "Instale com 'uv pip install openai-whisper' "
                                                 "para usar a função de Transcrição.")
    
    # Importa moviepy e pydub, verifica se estão disponíveis
    try:
        from moviepy.editor import VideoFileClip # Para moviepy
        from pydub import AudioSegment, utils # Para pydub
    except ImportError:
        messagebox.showerror("Erro de Dependência", "As bibliotecas 'moviepy' ou 'pydub' não estão instaladas. "
                                                 "Instale com 'uv pip install moviepy==1.0.3 pydub' "
                                                 "para usar a função de Corte.")

    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()