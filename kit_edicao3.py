import customtkinter as ctk
from tkinter import filedialog, messagebox
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

# --- Configuração Global do CustomTkinter ---
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue")

# --- Funções Auxiliares Comuns ---
CONFIG_FILE = "media_tool_config.json"

def carregar_config():
    """Carrega as configurações do arquivo JSON."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showwarning("Aviso", f"Arquivo de configuração '{CONFIG_FILE}' corrompido. Criando um novo.")
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
            print(f"Aviso: Não foi possível remover o arquivo temporário '{f}': {e}") # Log para console

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
                progress_callback(f"Erro ao carregar modelo Whisper: {e}\nVerifique sua conexão e se o modelo existe.", "error", True)
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

        # Validação de tempo aqui também (dupla verificação, mas essencial para robustez)
        if inicio_seg < 0 or fim_seg > duracao_total_seg or inicio_seg >= duracao_total_seg or inicio_seg >= fim_seg:
            progress_callback(f"Erro: Tempos de corte inválidos. Mídia tem {formatar_duracao(duracao_total_seg)}.", "error", True)
            return False

        progress_callback(f"Cortando de {formatar_duracao(inicio_seg)} a {formatar_duracao(fim_seg)}...", "info")
        
        if is_video:
            segmento_cortado = clip.subclip(inicio_seg, fim_seg)
            segmento_cortado.write_videofile(caminho_saida, codec="libx264", audio_codec="aac",
                                                logger=None) # logger=None para evitar logs excessivos no console
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


# --- Classes CustomTkinter para as Abas ---

class TranscribeTab(ctk.CTkFrame):
    def __init__(self, master, config_ref):
        super().__init__(master, fg_color="transparent")
        self.config = config_ref
        self.caminho_audio = ""

        # --- Widgets da Aba Transcrição ---
        ctk.CTkLabel(self, text="Arquivo de Áudio:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,0), anchor='w')

        frame_file_selection = ctk.CTkFrame(self, fg_color="transparent")
        frame_file_selection.pack(fill='x', pady=5)
        self.entry_audio_path = ctk.CTkEntry(frame_file_selection, width=400, font=ctk.CTkFont(size=13))
        self.entry_audio_path.pack(side="left", expand=True, fill='x')
        ctk.CTkButton(frame_file_selection, text="Selecionar", command=self.selecionar_audio, width=100, font=ctk.CTkFont(size=12)).pack(side="right", padx=10)

        ctk.CTkLabel(self, text="Modelo Whisper:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,0), anchor='w')
        self.modelos_disponiveis = ["tiny", "base", "small", "medium", "large"]
        self.modelo_selecionado = ctk.StringVar(self)
        last_model = self.config.get('ultimo_modelo_whisper', 'base')
        if last_model not in self.modelos_disponiveis:
            last_model = 'base'
        self.modelo_selecionado.set(last_model)
        ctk.CTkOptionMenu(self, variable=self.modelo_selecionado, values=self.modelos_disponiveis, command=self.salvar_modelo_selecionado, font=ctk.CTkFont(size=13)).pack(pady=5, anchor='w')

        ctk.CTkLabel(self, text="Diretório de Saída:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,0), anchor='w')
        frame_output_dir = ctk.CTkFrame(self, fg_color="transparent")
        frame_output_dir.pack(fill='x', pady=5)
        self.entry_output_dir = ctk.CTkEntry(frame_output_dir, width=400, font=ctk.CTkFont(size=13))
        last_output_dir = self.config.get('ultimo_diretorio_saida_transcricao', os.path.join(os.getcwd(), 'transcricoes'))
        self.entry_output_dir.insert(0, last_output_dir)
        self.entry_output_dir.pack(side="left", expand=True, fill='x')
        ctk.CTkButton(frame_output_dir, text="Abrir Pasta", command=self.selecionar_diretorio_saida, width=100, font=ctk.CTkFont(size=12)).pack(side="right", padx=10)


        self.btn_transcrever = ctk.CTkButton(self, text="Transcrever Áudio", command=self.iniciar_transcricao,
                                              font=ctk.CTkFont(size=15, weight="bold"), height=40, fg_color="#007bff", hover_color="#0056b3")
        self.btn_transcrever.pack(pady=20)

        # Área de log/resultado
        ctk.CTkLabel(self, text="Status/Resultado:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,0), anchor='w')
        self.text_resultado = ctk.CTkTextbox(self, height=150, width=580, state="disabled", wrap="word", font=ctk.CTkFont(size=12))
        self.text_resultado.pack(pady=5, fill='both', expand=True)

    def selecionar_audio(self):
        filetypes = [("Arquivos de Áudio", "*.mp3 *.wav *.flac *.m4a *.ogg"), ("Todos os arquivos", "*.*")]
        filepath = filedialog.askopenfilename(title="Selecione um arquivo de Áudio", filetypes=filetypes)
        if filepath:
            self.caminho_audio = filepath
            self.entry_audio_path.delete(0, "end")
            self.entry_audio_path.insert(0, filepath)
            self.update_status(f"Arquivo selecionado: {os.path.basename(filepath)}", "info")
        else:
            self.update_status("Seleção de arquivo cancelada.", "info")

    def selecionar_diretorio_saida(self):
        directory = filedialog.askdirectory(title="Selecione o Diretório de Saída para Transcrições")
        if directory:
            self.entry_output_dir.delete(0, "end")
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
        # CORREÇÃO AQUI: Não usamos tag_configure diretamente em CTkTextbox
        self.text_resultado.configure(state="normal")
        # Podemos mudar a cor do TEXTO INSERIDO, mas não do widget em si
        # Ou simplesmente inserir o texto sem cores, dependendo da simplicidade desejada.
        # Para uma cor simples:
        if message_type == "error":
            # CTkTextbox não suporta tags com cores tão facilmente como tk.Text
            # Vamos simplesmente inserir o texto sem tags coloridas aqui para evitar o erro
            # As cores do pop-up continuarão funcionando
            prefix = "[ERRO] "
        elif message_type == "success":
            prefix = "[SUCESSO] "
        elif message_type == "warning":
            prefix = "[AVISO] "
        elif message_type == "progress":
            prefix = "[PROCESSO] "
        else:
            prefix = ""

        self.text_resultado.insert("end", f"[{time.strftime('%H:%M:%S')}] {prefix}{message}\n")
        self.text_resultado.configure(state="disabled")
        self.text_resultado.see("end")

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
        self.btn_transcrever.configure(state="disabled")
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
            self.master.after(0, self.btn_transcrever.configure, {'state': "normal"})


class CutVideoAudioTab(ctk.CTkFrame):
    def __init__(self, master, config_ref):
        super().__init__(master, fg_color="transparent")
        self.config = config_ref
        self.caminho_midia = ""
        self.is_video = ctk.BooleanVar(value=True)
        self.duracao_midia = 0.0

        # --- Widgets da Aba Corte ---
        ctk.CTkLabel(self, text="Arquivo de Mídia (Vídeo ou Áudio):", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,0), anchor='w')
        frame_file_selection = ctk.CTkFrame(self, fg_color="transparent")
        frame_file_selection.pack(fill='x', pady=5)
        self.entry_media_path = ctk.CTkEntry(frame_file_selection, width=400, font=ctk.CTkFont(size=13))
        self.entry_media_path.pack(side="left", expand=True, fill='x')
        ctk.CTkButton(frame_file_selection, text="Selecionar", command=self.selecionar_midia, width=100, font=ctk.CTkFont(size=12)).pack(side="right", padx=10)

        frame_media_type = ctk.CTkFrame(self, fg_color="transparent")
        frame_media_type.pack(pady=5, anchor='w')
        ctk.CTkLabel(frame_media_type, text="Tipo de Mídia:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5)
        ctk.CTkRadioButton(frame_media_type, text="Vídeo", variable=self.is_video, value=True, command=self.on_media_type_change, font=ctk.CTkFont(size=13)).pack(side="left", padx=5)
        ctk.CTkRadioButton(frame_media_type, text="Áudio", variable=self.is_video, value=False, command=self.on_media_type_change, font=ctk.CTkFont(size=13)).pack(side="left", padx=5)
        self.is_video.set(True)

        ctk.CTkLabel(self, text="Duração Total:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,0), anchor='w')
        self.label_duration = ctk.CTkLabel(self, text="00:00:00 (0.00s)", font=ctk.CTkFont(size=13, weight="bold"))
        self.label_duration.pack(pady=5, anchor='w')

        # Frame para os campos de tempo (lado a lado)
        frame_time_inputs = ctk.CTkFrame(self, fg_color="transparent")
        frame_time_inputs.pack(fill='x', pady=5)

        # Início do Corte
        ctk.CTkLabel(frame_time_inputs, text="Início (segundos):", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0,5), anchor='w')
        self.entry_start_time = ctk.CTkEntry(frame_time_inputs, width=120, font=ctk.CTkFont(size=13))
        self.entry_start_time.pack(side="left", padx=(0,20), expand=True, fill='x')

        # Fim do Corte
        ctk.CTkLabel(frame_time_inputs, text="Fim (segundos):", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0,5), anchor='w')
        self.entry_end_time = ctk.CTkEntry(frame_time_inputs, width=120, font=ctk.CTkFont(size=13))
        self.entry_end_time.pack(side="left", expand=True, fill='x')

        ctk.CTkLabel(self, text="Exemplos de tempo:", font=ctk.CTkFont(size=12, slant="italic")).pack(pady=(5,0), anchor='w')
        self.label_time_examples = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11))
        self.label_time_examples.pack(pady=2, anchor='w')

        ctk.CTkLabel(self, text="Diretório de Saída:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,0), anchor='w')
        frame_output_dir_cut = ctk.CTkFrame(self, fg_color="transparent")
        frame_output_dir_cut.pack(fill='x', pady=5)
        self.entry_output_dir = ctk.CTkEntry(frame_output_dir_cut, width=400, font=ctk.CTkFont(size=13))
        last_output_dir_video = self.config.get('ultimo_diretorio_saida_video', os.path.join(os.getcwd(), 'cortes'))
        self.entry_output_dir.insert(0, last_output_dir_video)
        self.entry_output_dir.pack(side="left", expand=True, fill='x')
        ctk.CTkButton(frame_output_dir_cut, text="Abrir Pasta", command=self.selecionar_diretorio_saida, width=100, font=ctk.CTkFont(size=12)).pack(side="right", padx=10)


        self.btn_cortar = ctk.CTkButton(self, text="Cortar Mídia", command=self.iniciar_corte,
                                         font=ctk.CTkFont(size=15, weight="bold"), height=40, fg_color="#ff6600", hover_color="#cc5200")
        self.btn_cortar.pack(pady=20)

        # Área de log/resultado
        ctk.CTkLabel(self, text="Status/Resultado:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,0), anchor='w')
        self.text_resultado = ctk.CTkTextbox(self, height=150, width=580, state="disabled", wrap="word", font=ctk.CTkFont(size=12))
        self.text_resultado.pack(pady=5, fill='both', expand=True)

    # Nova função de validação para CustomTkinter.CTkEntry
    def validate_numeric_input(self, text):
        # Esta função de validação será usada nos binds diretamente (não via validatecommand)
        if text == "": return True
        try:
            float(text.replace(',', '.'))
            return True
        except ValueError:
            return False

    def on_media_type_change(self):
        self.caminho_midia = ""
        self.entry_media_path.delete(0, "end")
        self.label_duration.configure(text="00:00:00 (0.00s)")
        self.entry_start_time.delete(0, "end")
        self.entry_end_time.delete(0, "end")
        self.label_time_examples.configure(text="")
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
            self.entry_media_path.delete(0, "end")
            self.entry_media_path.insert(0, filepath)

            self.update_status(f"Arquivo selecionado: {os.path.basename(filepath)}", "info")
            self.obter_e_mostrar_duracao()
        else:
            self.update_status("Seleção de arquivo cancelada.", "info")
            self.label_duration.configure(text="00:00:00 (0.00s)")
            self.label_time_examples.configure(text="")


    def selecionar_diretorio_saida(self):
        directory = filedialog.askdirectory(title="Selecione o Diretório de Saída para Cortes")
        if directory:
            self.entry_output_dir.delete(0, "end")
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
            self.label_duration.configure(text="Erro de extensão.")
            self.duracao_midia = 0.0
            self.label_time_examples.configure(text="")
            return

        self.duracao_midia = obter_duracao_midia_gui(self.caminho_midia, self.is_video.get())
        if self.duracao_midia is not None:
            self.label_duration.configure(text=f"{formatar_duracao(self.duracao_midia)} ({self.duracao_midia:.2f}s)")
            self.update_status(f"Duração do arquivo: {formatar_duracao(self.duracao_midia)}", "info")
            self.update_time_examples(self.duracao_midia)
        else:
            self.label_duration.configure(text="Erro ao obter duração.")
            self.update_status("Não foi possível obter a duração do arquivo. Verifique se o FFmpeg está configurado e o arquivo está válido.", "error", True)
            self.label_time_examples.configure(text="")

    def update_time_examples(self, duration):
        ex_start = 0.0
        ex_end = duration / 2
        ex_middle_start = duration / 4
        ex_middle_end = duration * 3 / 4

        ex_start_str = f"{ex_start:.2f}".replace('.', ',', 1)
        ex_end_str = f"{ex_end:.2f}".replace('.', ',', 1)
        ex_middle_start_str = f"{ex_middle_start:.2f}".replace('.', ',', 1)
        ex_middle_end_str = f"{ex_middle_end:.2f}".replace('.', ',', 1)

        examples_text = (f"Ex: {ex_start_str} (início) a {ex_end_str} (metade); "
                         f"{ex_middle_start_str} a {ex_middle_end_str} (segmento do meio); "
                         f"0,00 a {duration:.2f} (fim)")
        self.label_time_examples.configure(text=examples_text)


    def update_status(self, message, message_type="info", show_popup=False):
        self.text_resultado.configure(state="normal")
        # Removendo a tag_configure para resolver o AttributeError
        # CTkTextbox não suporta tags diretamente como tk.Text
        # As cores nos pop-ups (messagebox) ainda funcionarão.
        self.text_resultado.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.text_resultado.configure(state="disabled")
        self.text_resultado.see("end")

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

        # Validação de que os campos não estão vazios
        if not self.entry_start_time.get() or not self.entry_end_time.get():
            self.update_status("Por favor, preencha os tempos de início e fim do corte.", "warning", True)
            return

        # Validação mais robusta dos tempos de input
        try:
            start_time_str = self.entry_start_time.get().replace(',', '.')
            end_time_str = self.entry_end_time.get().replace(',', '.')

            start_time = float(start_time_str)
            end_time = float(end_time_str)

            # --- VALIDAÇÃO LÓGICA APRIMORADA FINAL ---
            # 0.0 <= start_time < self.duracao_midia: Início deve ser >= 0 E menor que a duração total
            # start_time < end_time <= self.duracao_midia: Fim deve ser > Início E menor ou igual à duração total
            if not (0.0 <= start_time < self.duracao_midia and start_time < end_time <= self.duracao_midia):
                 self.update_status(f"Tempos de corte inválidos. "
                                    f"Início ({start_time:.2f}s) deve ser >= 0,00s. "
                                    f"Fim ({end_time:.2f}s) deve ser <= {self.duracao_midia:.2f}s. "
                                    f"E Fim deve ser ESTRITAMENTE MAIOR que Início.", "error", True)
                 return

        except ValueError:
            self.update_status("Tempos de início e fim devem ser números válidos (ex: 10 ou 15,5).", "error", True)
            return

        # Salva o diretório final escolhido para a próxima vez
        self.config['ultimo_diretorio_saida_video'] = output_dir
        salvar_config(self.config)

        self.update_status("Processando corte...", "info")
        self.btn_cortar.configure(state="disabled")
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
            self.master.after(0, self.btn_cortar.configure, {'state': "normal"})


class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ferramenta de Transcrição e Corte de Mídia")
        self.geometry("700x650")
        self.minsize(600, 550)

        # --- Configuração de Fontes ---
        # Definimos as fontes aqui e as passamos para os widgets nas classes das abas
        self.base_font_size = 12
        self.label_font = ctk.CTkFont(size=self.base_font_size + 1)
        self.heading_font = ctk.CTkFont(size=self.base_font_size + 2, weight="bold")
        self.input_font = ctk.CTkFont(size=self.base_font_size + 1)
        self.button_font_small = ctk.CTkFont(size=self.base_font_size)
        self.button_font_large = ctk.CTkFont(size=self.base_font_size + 3, weight="bold")
        self.text_box_font = ctk.CTkFont(size=self.base_font_size)
        self.tab_button_font = ctk.CTkFont(size=self.base_font_size + 2, weight="bold")


        self.config = carregar_config()

        # CTkTabview é o equivalente a ttk.Notebook no CustomTkinter
        self.tab_view = ctk.CTkTabview(self, width=650, height=550)
        self.tab_view.pack(padx=20, pady=20, fill="both", expand=True)

        # Configurar a fonte dos botões das abas APÓS a criação do CTkTabview
        # Usamos o acesso ao atributo interno _segmented_button
        # e configuramos a fonte de seus botões internos.
        # Esta é a forma mais robusta e testada que encontrei para controlar a fonte das abas.
        self.tab_view._segmented_button.configure(font=self.tab_button_font)


        # Adiciona as abas
        # Passa a master (tab_view.add("Nome da Aba")) e a config_ref
        self.transcribe_tab = TranscribeTab(self.tab_view.add("Transcrever Áudio"), self.config)
        self.transcribe_tab.pack(fill="both", expand=True, padx=10, pady=10)

        self.cut_tab = CutVideoAudioTab(self.tab_view.add("Cortar Vídeo/Áudio"), self.config)
        self.cut_tab.pack(fill="both", expand=True, padx=10, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        limpar_temporarios()
        self.destroy()


if __name__ == "__main__":
    # Verificação de dependências antes de iniciar a GUI
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

    app = MainApplication()
    app.mainloop()