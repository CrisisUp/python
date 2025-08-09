import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
import time 
import glob 

# Importa as bibliotecas para processamento de áudio/vídeo
from pydub import AudioSegment
from pydub.utils import mediainfo
from pydub.exceptions import CouldntDecodeError
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
CONFIG_FILE = "media_tool_config.json"

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
_whisper_model = None 

def get_whisper_model(model_name="base", progress_callback=None):
    """Carrega o modelo Whisper uma única vez."""
    global _whisper_model
    if _whisper_model is None:
        if progress_callback:
            progress_callback(f"Carregando modelo Whisper '{model_name}'... (Primeira vez pode demorar e baixar dados)", "info", True) 
        try:
            import whisper 
            _whisper_model = whisper.load_model(model_name)
            if progress_callback:
                progress_callback("Modelo Whisper carregado com sucesso!", "success", True)
        except Exception as e:
            if progress_callback:
                progress_callback(f"Erro ao carregar modelo Whisper: {e}", "error", True)
            raise e
    return _whisper_model

def transcrever_audio_gui(caminho_audio, modelo_whisper, output_dir, progress_callback):
    """Transcreve áudio para texto para a GUI."""
    progress_callback("Iniciando transcrição...", "info")
    
    if not os.path.exists(caminho_audio):
        progress_callback(f"Erro: Arquivo '{caminho_audio}' não encontrado.", "error", True)
        return "Erro: Arquivo não encontrado."

    os.makedirs(output_dir, exist_ok=True)
    
    try:
        model = get_whisper_model(modelo_whisper, progress_callback)
        progress_callback(f"Preparando áudio para transcrição...", "info")

        audio = AudioSegment.from_file(caminho_audio)
        audio_length_ms = len(audio)
        chunk_length_ms = 15000 

        chunks = []
        for i in range(0, audio_length_ms, chunk_length_ms):
            chunks.append(audio[i:i + chunk_length_ms])

        full_transcription = []
        
        progress_callback(f"Transcrevendo {len(chunks)} segmentos...", "info")
        for i, chunk in enumerate(chunks):
            temp_chunk_path = f"temp_chunk_{i}.wav"
            chunk.export(temp_chunk_path, format="wav")

            progress_callback(f"Processando segmento {i+1}/{len(chunks)}...", "progress")
            
            result = model.transcribe(temp_chunk_path, language="pt", fp16=False, suppress_tokens=[-1])
            full_transcription.append(result["text"])
            os.remove(temp_chunk_path)
            
        texto_transcrito = " ".join(full_transcription).strip()
        
        # Salva o texto em um arquivo
        nome_arquivo_base = os.path.splitext(os.path.basename(caminho_audio))[0]
        caminho_arquivo_saida = os.path.join(output_dir, f"{nome_arquivo_base}_transcricao.txt")
        
        with open(caminho_arquivo_saida, "w", encoding="utf-8") as f:
            f.write(texto_transcrito)
        
        progress_callback(f"Transcrição concluída! Salva em: '{caminho_arquivo_saida}'", "success", True)
        return texto_transcrito
        
    except Exception as e:
        progress_callback(f"Erro na transcrição: {e}. Verifique FFmpeg/modelo.", "error", True)
        return f"Erro: {e}"
    finally:
        limpar_temporarios() 


# Corte de Áudio/Vídeo
def cortar_midia_gui(caminho_entrada, caminho_saida, inicio_seg, fim_seg, is_video=True, progress_callback=None):
    """Corta áudio ou vídeo para a GUI."""
    progress_callback("Iniciando corte...", "info")

    if not os.path.exists(caminho_entrada):
        progress_callback(f"Erro: Arquivo '{caminho_entrada}' não encontrado.", "error", True)
        return False

    clip = None 
    try:
        if is_video:
            clip = VideoFileClip(caminho_entrada)
        else:
            clip = AudioSegment.from_file(caminho_entrada)
        
        duracao_total_seg = clip.duration if is_video else (len(clip) / 1000)

        if inicio_seg < 0 or fim_seg > duracao_total_seg or inicio_seg >= fim_seg:
            progress_callback(f"Erro: Tempos de corte inválidos. Mídia tem {formatar_duracao(duracao_total_seg)}.", "error", True)
            return False

        progress_callback(f"Cortando de {formatar_duracao(inicio_seg)} a {formatar_duracao(fim_seg)}...", "info")
        
        if is_video:
            segmento_cortado = clip.subclip(inicio_seg, fim_seg)
            segmento_cortado.write_videofile(caminho_saida, codec="libx264", audio_codec="aac",
                                                logger=None) # Desativa log do MoviePy no console
        else:
            segmento_cortado = clip[int(inicio_seg * 1000):int(fim_seg * 1000)]
            segmento_cortado.export(caminho_saida, format=caminho_saida.split('.')[-1])

        progress_callback(f"Corte concluído! Salvo em: '{caminho_saida}'", "success", True)
        return True

    except (CouldntDecodeError, Exception) as e: 
        error_msg = f"Erro no corte: {e}. Verifique se o FFmpeg está instalado e o arquivo não está corrompido."
        progress_callback(error_msg, "error", True)
        return False
    finally:
        if clip and is_video: 
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
            duracao = len(audio) / 1000 
        return duracao
    except Exception as e:
        print(f"Erro ao obter duração: {e}") 
        return None
    finally:
        if clip and is_video:
            clip.close()


# --- Classes Tkinter para as Abas ---

class TranscribeTab(tk.Frame):
    def __init__(self, master, config_ref):
        super().__init__(master, padx=20, pady=20) # Aumenta o padding da aba
        self.config = config_ref
        self.caminho_audio = ""
        
        # --- Widgets da Aba Transcrição ---
        ttk.Label(self, text="Arquivo de Áudio:").pack(pady=(10,0), anchor='w')
        
        frame_file_selection = ttk.Frame(self)
        frame_file_selection.pack(fill='x', pady=5)
        self.entry_audio_path = ttk.Entry(frame_file_selection, width=50)
        self.entry_audio_path.pack(side=tk.LEFT, expand=True, fill='x')
        ttk.Button(frame_file_selection, text="Selecionar", command=self.selecionar_audio).pack(side=tk.RIGHT, padx=10)

        ttk.Label(self, text="Modelo Whisper:").pack(pady=(10,0), anchor='w')
        self.modelos_disponiveis = ["tiny", "base", "small", "medium", "large"]
        self.modelo_selecionado = tk.StringVar(self)
        last_model = self.config.get('ultimo_modelo_whisper', 'base')
        if last_model not in self.modelos_disponiveis:
            last_model = 'base' 
        self.modelo_selecionado.set(last_model)
        ttk.OptionMenu(self, self.modelo_selecionado, self.modelo_selecionado.get(), *self.modelos_disponiveis, command=self.salvar_modelo_selecionado).pack(pady=5, anchor='w')

        ttk.Label(self, text="Diretório de Saída:").pack(pady=(10,0), anchor='w')
        frame_output_dir = ttk.Frame(self)
        frame_output_dir.pack(fill='x', pady=5)
        self.entry_output_dir = ttk.Entry(frame_output_dir, width=50)
        last_output_dir = self.config.get('ultimo_diretorio_saida_transcricao', os.path.join(os.getcwd(), 'transcricoes')) 
        self.entry_output_dir.insert(0, last_output_dir)
        self.entry_output_dir.pack(side=tk.LEFT, expand=True, fill='x')
        ttk.Button(frame_output_dir, text="Abrir Pasta", command=self.selecionar_diretorio_saida).pack(side=tk.RIGHT, padx=10)


        self.btn_transcrever = ttk.Button(self, text="Transcrever Áudio", command=self.iniciar_transcricao, style="Accent.TButton")
        self.btn_transcrever.pack(pady=20)

        # Área de log/resultado
        ttk.Label(self, text="Status/Resultado:").pack(pady=(10,0), anchor='w')
        self.text_resultado = tk.Text(self, height=10, width=70, state=tk.DISABLED, wrap=tk.WORD) # Font style is global
        self.text_resultado.pack(pady=5, fill='both', expand=True)

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

    def selecionar_diretorio_saida(self):
        directory = filedialog.askdirectory(title="Selecione o Diretório de Saída para Transcrições")
        if directory:
            self.entry_output_dir.delete(0, tk.END)
            self.entry_output_dir.insert(0, directory)
            self.update_status(f"Diretório de saída selecionado: {directory}", "info")
            self.config['ultimo_diretorio_saida_transcricao'] = directory 
            salvar_config(self.config)
        else:
            self.update_status("Seleção de diretório cancelada.", "info")

    def salvar_modelo_selecionado(self, model_name):
        self.config['ultimo_modelo_whisper'] = model_name
        salvar_config(self.config)
        self.update_status(f"Modelo Whisper definido para: {model_name}", "info")

    def update_status(self, message, message_type="info", show_popup=False):
        self.text_resultado.config(state=tk.NORMAL)
        if message_type == "error":
            color = "#dc3545" 
        elif message_type == "success":
            color = "#28a745" 
        elif message_type == "warning":
            color = "#ffc107" 
        elif message_type == "progress":
            color = "#17a2b8" # Azul Ciano para progresso
        else:
            color = "#007bff" 
        
        self.text_resultado.tag_config(message_type, foreground=color)
        self.text_resultado.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n", message_type)
        self.text_resultado.config(state=tk.DISABLED)
        self.text_resultado.see(tk.END) 

        if show_popup: 
            if message_type == "error":
                messagebox.showerror("Erro na Transcrição", message)
            elif message_type == "success":
                messagebox.showinfo("Sucesso", message)
            elif message_type == "warning":
                messagebox.showwarning("Aviso", message)
            else:
                messagebox.showinfo("Informação", message)

            
    def iniciar_transcricao(self):
        audio_path = self.entry_audio_path.get()
        model_name = self.modelo_selecionado.get()
        output_dir = self.entry_output_dir.get()

        if not audio_path:
            self.update_status("Por favor, selecione um arquivo de áudio primeiro.", "warning", True)
            return
        
        extensao = os.path.splitext(audio_path)[1].lower()
        extensoes_audio_validas = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma', '.aiff', '.aif']
        if extensao not in extensoes_audio_validas:
            self.update_status(f"Aviso: Extensão '{extensao}' pode não ser um formato de áudio suportado. Tente .mp3, .wav, .flac.", "warning", True)
        
        self.update_status("Processando...", "info")
        self.btn_transcrever.config(state=tk.DISABLED) 
        threading.Thread(target=self._executar_transcricao_thread, args=(audio_path, model_name, output_dir)).start()

    def _executar_transcricao_thread(self, audio_path, model_name, output_dir):
        try:
            transcricao_final = transcrever_audio_gui(audio_path, model_name, output_dir, self.update_status)
            self.update_status("Transcrição finalizada. Verifique o resultado na área de status.", "info")
            if "Erro" in transcricao_final: 
                 self.update_status(f"Falha na Transcrição: {transcricao_final}", "error")
        except Exception as e:
            self.update_status(f"Erro inesperado no thread de transcrição: {e}", "error", True)
        finally:
            self.master.after(0, self.btn_transcrever.config, {'state': tk.NORMAL}) 


class CutVideoAudioTab(tk.Frame):
    def __init__(self, master, config_ref):
        super().__init__(master, padx=20, pady=20) # Aumenta o padding da aba
        self.config = config_ref
        self.caminho_midia = ""
        self.is_video = tk.BooleanVar(value=True) 
        self.duracao_midia = 0.0

        # --- Widgets da Aba Corte ---
        ttk.Label(self, text="Arquivo de Mídia (Vídeo ou Áudio):").pack(pady=(10,0), anchor='w')
        frame_file_selection = ttk.Frame(self)
        frame_file_selection.pack(fill='x', pady=5)
        self.entry_media_path = ttk.Entry(frame_file_selection, width=50)
        self.entry_media_path.pack(side=tk.LEFT, expand=True, fill='x')
        ttk.Button(frame_file_selection, text="Selecionar", command=self.selecionar_midia).pack(side=tk.RIGHT, padx=10)

        frame_media_type = ttk.Frame(self)
        frame_media_type.pack(pady=5, anchor='w')
        ttk.Label(frame_media_type, text="Tipo de Mídia:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_media_type, text="Vídeo", variable=self.is_video, value=True, command=self.on_media_type_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_media_type, text="Áudio", variable=self.is_video, value=False, command=self.on_media_type_change).pack(side=tk.LEFT, padx=5)
        self.is_video.set(True) 

        ttk.Label(self, text="Duração Total:").pack(pady=(10,0), anchor='w')
        self.label_duration = ttk.Label(self, text="00:00:00 (0.00s)")
        self.label_duration.pack(pady=5, anchor='w')

        # Frame para os campos de tempo (lado a lado)
        frame_time_inputs = ttk.Frame(self)
        frame_time_inputs.pack(fill='x', pady=5)

        # Início do Corte
        ttk.Label(frame_time_inputs, text="Início (segundos):").pack(side=tk.LEFT, padx=(0,5), anchor='w')
        self.entry_start_time = ttk.Entry(frame_time_inputs, width=15, validate='key')
        self.reg_val_cmd = self.register(self.validate_numeric_input) # Registra a validação
        self.entry_start_time.config(validatecommand=(self.reg_val_cmd, '%P'))
        self.entry_start_time.pack(side=tk.LEFT, padx=(0,20), expand=True, fill='x')

        # Fim do Corte
        ttk.Label(frame_time_inputs, text="Fim (segundos):").pack(side=tk.LEFT, padx=(0,5), anchor='w')
        self.entry_end_time = ttk.Entry(frame_time_inputs, width=15, validate='key')
        self.entry_end_time.config(validatecommand=(self.reg_val_cmd, '%P'))
        self.entry_end_time.pack(side=tk.LEFT, expand=True, fill='x')

        ttk.Label(self, text="Exemplos de tempo:").pack(pady=(5,0), anchor='w')
        self.label_time_examples = ttk.Label(self, text="") # Vai ser atualizado dinamicamente
        self.label_time_examples.pack(pady=2, anchor='w')


        ttk.Label(self, text="Diretório de Saída:").pack(pady=(10,0), anchor='w')
        frame_output_dir_cut = ttk.Frame(self)
        frame_output_dir_cut.pack(fill='x', pady=5)
        self.entry_output_dir = ttk.Entry(frame_output_dir_cut, width=50)
        last_output_dir_video = self.config.get('ultimo_diretorio_saida_video', os.path.join(os.getcwd(), 'cortes')) 
        self.entry_output_dir.insert(0, last_output_dir_video)
        self.entry_output_dir.pack(side=tk.LEFT, expand=True, fill='x')
        ttk.Button(frame_output_dir_cut, text="Abrir Pasta", command=self.selecionar_diretorio_saida).pack(side=tk.RIGHT, padx=10)


        self.btn_cortar = ttk.Button(self, text="Cortar Mídia", command=self.iniciar_corte, style="Cut.TButton")
        self.btn_cortar.pack(pady=20)

        # Área de log/resultado
        ttk.Label(self, text="Status/Resultado:").pack(pady=(10,0), anchor='w')
        self.text_resultado = tk.Text(self, height=10, width=70, state=tk.DISABLED, wrap=tk.WORD)
        self.text_resultado.pack(pady=5, fill='both', expand=True)

    def validate_numeric_input(self, P):
        """Valida que apenas números e um único ponto/vírgula são digitados."""
        if P == "" or P.replace('.', '', 1).replace(',', '', 1).isdigit():
            # Permite string vazia, ou string que vira número após remover um . ou ,
            return True
        else:
            return False

    def on_media_type_change(self):
        self.caminho_midia = ""
        self.entry_media_path.delete(0, tk.END)
        self.label_duration.config(text="00:00:00 (0.00s)")
        self.entry_start_time.delete(0, tk.END)
        self.entry_end_time.delete(0, tk.END)
        self.label_time_examples.config(text="") # Limpa exemplos
        self.update_status(f"Tipo de mídia alterado para: {'Vídeo' if self.is_video.get() else 'Áudio'}", "info")


    def selecionar_midia(self):
        if self.is_video.get():
            filetypes = [("Arquivos de Vídeo", "*.mp4 *.avi *.mov *.mkv *.webm *.flv *.wmv *.mpeg *.mpg"), ("Todos os arquivos", "*.*")]
            title = "Selecione um arquivo de Vídeo"
        else:
            filetypes = [("Arquivos de Áudio", "*.mp3 *.wav *.flac *.m4a *.ogg *.aac *.wma *.aiff *.aif"), ("Todos os arquivos", "*.*")]
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
            self.label_time_examples.config(text="") # Limpa exemplos


    def selecionar_diretorio_saida(self):
        directory = filedialog.askdirectory(title="Selecione o Diretório de Saída para Cortes")
        if directory:
            self.entry_output_dir.delete(0, tk.END)
            self.entry_output_dir.insert(0, directory)
            self.update_status(f"Diretório de saída selecionado: {directory}", "info")
            self.config['ultimo_diretorio_saida_video'] = directory 
            salvar_config(self.config)
        else:
            self.update_status("Seleção de diretório cancelada.", "info")


    def obter_e_mostrar_duracao(self):
        extensao = os.path.splitext(self.caminho_midia)[1].lower()
        if self.is_video.get():
            validas = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.mpeg', '.mpg']
        else:
            validas = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma', '.aiff', '.aif']

        if extensao not in validas:
            self.update_status(f"Aviso: Extensão '{extensao}' pode não ser um formato válido para o tipo de mídia selecionado.", "warning", True)
            self.label_duration.config(text="Erro de extensão.")
            self.duracao_midia = 0.0
            self.label_time_examples.config(text="") # Limpa exemplos
            return

        self.duracao_midia = obter_duracao_midia_gui(self.caminho_midia, self.is_video.get())
        if self.duracao_midia is not None:
            self.label_duration.config(text=f"{formatar_duracao(self.duracao_midia)} ({self.duracao_midia:.2f}s)")
            self.update_status(f"Duração do arquivo: {formatar_duracao(self.duracao_midia)}", "info")
            self.update_time_examples(self.duracao_midia) # Atualiza exemplos de tempo
        else:
            self.label_duration.config(text="Erro ao obter duração.")
            self.update_status("Não foi possível obter a duração do arquivo. Verifique se o FFmpeg está configurado e o arquivo está válido.", "error", True)
            self.label_time_examples.config(text="") # Limpa exemplos
            
    def update_time_examples(self, duration):
        # Gera exemplos baseados na duração total
        ex_start = 0.0
        ex_end = duration / 2
        ex_middle_start = duration / 4
        ex_middle_end = duration * 3 / 4

        # Arredonda para 2 casas decimais para exemplos mais limpos
        ex_start_str = f"{ex_start:.2f}".replace('.', ',')
        ex_end_str = f"{ex_end:.2f}".replace('.', ',')
        ex_middle_start_str = f"{ex_middle_start:.2f}".replace('.', ',')
        ex_middle_end_str = f"{ex_middle_end:.2f}".replace('.', ',')

        examples_text = (f"Ex: {ex_start_str} (início) a {ex_end_str} (metade); "
                         f"{ex_middle_start_str} a {ex_middle_end_str} (segmento do meio); "
                         f"0 (início) a {duration:.2f} (fim)")
        self.label_time_examples.config(text=examples_text)


    def update_status(self, message, message_type="info", show_popup=False):
        self.text_resultado.config(state=tk.NORMAL)
        if message_type == "error":
            color = "#dc3545" 
        elif message_type == "success":
            color = "#28a745" 
        elif message_type == "warning":
            color = "#ffc107" 
        elif message_type == "progress":
            color = "#17a2b8" 
        else:
            color = "#007bff" 
        
        self.text_resultado.tag_config(message_type, foreground=color)
        self.text_resultado.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n", message_type)
        self.text_resultado.config(state=tk.DISABLED)
        self.text_resultado.see(tk.END) 

        if show_popup: 
            if message_type == "error":
                messagebox.showerror("Erro na Operação", message)
            elif message_type == "success":
                messagebox.showinfo("Sucesso", message)
            elif message_type == "warning":
                messagebox.showwarning("Aviso", message)
            else:
                messagebox.showinfo("Informação", message)

    def iniciar_corte(self):
        media_path = self.entry_media_path.get()
        output_dir = self.entry_output_dir.get()
        
        if not media_path:
            self.update_status("Por favor, selecione um arquivo para cortar.", "warning", True)
            return

        # Validação mais robusta dos tempos
        try:
            start_time = float(self.entry_start_time.get().replace(',', '.'))
            end_time = float(self.entry_end_time.get().replace(',', '.'))

            if not (0 <= start_time < self.duracao_midia and start_time < end_time <= self.duracao_midia):
                 self.update_status(f"Tempos de corte inválidos. Início deve ser >= 0, Fim <= Duração Total ({self.duracao_midia:.2f}s) e Fim > Início.", "error", True)
                 return

        except ValueError:
            self.update_status("Tempos de início e fim devem ser números válidos (ex: 10, 15.5).", "error", True)
            return

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
                extensao_limpa = 'mp4' if self.is_video.get() else 'wav' 
            
            output_filepath = os.path.join(output_dir, f"{nome_arquivo_original}_cortado.{extensao_limpa}")

            sucesso = cortar_midia_gui(media_path, output_filepath, start_time, end_time, self.is_video.get(), self.update_status)
            if sucesso:
                self.update_status(f"Corte finalizado. Arquivo salvo em: {output_filepath}", "success")
            else:
                self.update_status(f"Falha no corte para {os.path.basename(media_path)}. Verifique os logs.", "error")
        except Exception as e:
            self.update_status(f"Erro inesperado no thread de corte: {e}", "error", True)
        finally:
            self.master.after(0, self.btn_cortar.config, {'state': tk.NORMAL})


class MainApplication:
    def __init__(self, master):
        self.master = master
        master.title("Ferramenta de Transcrição e Corte de Mídia")
        master.geometry("700x650") # Aumenta um pouco a altura para acomodar o novo layout
        master.minsize(600, 550) # Define um tamanho mínimo para a janela

        # --- Configuração de Estilos e Temas ---
        self.style = ttk.Style()
        self.style.theme_use('clam') 
        
        # Aumenta a fonte padrão para todos os widgets
        default_font_size = 11 # Aumenta a fonte base
        heading_font_size = 12 # Para títulos de widgets
        button_font_size = 12 # Para botões principais

        default_font = ("Arial", default_font_size)
        heading_font = ("Arial", heading_font_size, "bold")
        large_button_font = ("Arial", button_font_size, "bold") 

        # Configura fonte para todos os widgets ttk por padrão
        self.style.configure('.', font=default_font) 
        self.style.configure("TLabel", foreground="#333333") 
        self.style.configure("TEntry", fieldbackground="white", borderwidth=1, relief="solid")
        self.style.configure("TText", background="#f8f9fa", foreground="#333333", font=("Arial", default_font_size)) # Usa a fonte padrão aqui também

        # Estilos para os botões de ação principal (Transcrever e Cortar)
        self.style.configure("Accent.TButton", 
                             font=large_button_font, 
                             foreground="white", 
                             background="#007bff", 
                             padding=10, 
                             relief="flat", 
                             borderwidth=0)
        self.style.map("Accent.TButton", 
                       background=[("active", "#0056b3"), ("pressed", "#004085")])

        self.style.configure("Cut.TButton", 
                             font=large_button_font, 
                             foreground="white", 
                             background="#ff6600", 
                             padding=10, 
                             relief="flat", 
                             borderwidth=0)
        self.style.map("Cut.TButton", 
                       background=[("active", "#cc5200"), ("pressed", "#993d00")])

        # Estilo para os Labels que são cabeçalhos de seção
        self.style.configure("Heading.TLabel", font=heading_font, foreground="#4a7a8c") # Cor do texto do cabeçalho

        # TNotebook (abas)
        primary_color = "#4a7a8c" 
        secondary_color = "#e0e0e0" 
        button_text_color = "white"

        self.style.configure("TNotebook", background=primary_color, foreground=button_text_color)
        self.style.configure("TNotebook.Tab", 
                             background=secondary_color, 
                             foreground="#333333", # Texto escuro na aba não selecionada
                             font=("Arial", 11, "bold"), # Fonte ligeiramente maior e negrito para as abas
                             padding=[15, 8]) # Mais padding para as abas
        self.style.map("TNotebook.Tab", background=[("selected", primary_color)], 
                                        foreground=[("selected", button_text_color)])
        master.configure(bg=primary_color)


        self.config = carregar_config() 

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.transcribe_tab = TranscribeTab(self.notebook, self.config)
        self.notebook.add(self.transcribe_tab, text="Transcrever Áudio")

        self.cut_tab = CutVideoAudioTab(self.notebook, self.config)
        self.notebook.add(self.cut_tab, text="Cortar Vídeo/Áudio")

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        limpar_temporarios()
        self.master.destroy() 


if __name__ == "__main__":
    try:
        import whisper
    except ImportError:
        messagebox.showerror("Erro de Dependência", "A biblioteca 'openai-whisper' não está instalada. "
                                                 "Instale com 'uv pip install openai-whisper' "
                                                 "para usar a função de Transcrição.")
    
    try:
        from moviepy.editor import VideoFileClip 
        from pydub import AudioSegment, utils 
    except ImportError:
        messagebox.showerror("Erro de Dependência", "As bibliotecas 'moviepy' (v1.0.3) ou 'pydub' não estão instaladas. "
                                                 "Instale com 'uv pip install moviepy==1.0.3 pydub' "
                                                 "para usar a função de Corte.")

    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()