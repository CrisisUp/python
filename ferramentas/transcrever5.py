import whisper
import os
from tqdm import tqdm
from pydub import AudioSegment
import json # Para salvar/carregar configurações

# --- Definição de Cores ANSI ---
class Cores:
    RESET = '\033[0m'
    NEGRITO = '\033[1m'
    VERMELHO = '\033[31m'
    VERDE = '\033[32m'
    AMARELO = '\033[33m'
    AZUL = '\033[34m'
    CIANO = '\033[36m'
    MAGENTA = '\033[35m'

# --- Funções Auxiliares de Configuração ---
CONFIG_FILE = "transcriber_config.json"

def carregar_config():
    """Carrega as configurações do arquivo JSON."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_config(config):
    """Salva as configurações no arquivo JSON."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Funções Principais ---
def transcrever_audio_whisper(caminho_audio, modelo_whisper="base", output_dir="transcricoes", chunk_length_ms=15000):
    """
    Transcreve um arquivo de áudio para texto usando o modelo Whisper da OpenAI,
    exibindo uma barra de progresso real baseada na segmentação do áudio e
    salvando o texto em um arquivo.

    Args:
        caminho_audio (str): O caminho completo para o arquivo de áudio.
        modelo_whisper (str): O nome do modelo Whisper a ser usado (ex: "tiny", "base", "small", "medium", "large").
                              Modelos maiores são mais precisos, mas exigem mais recursos e tempo.
        output_dir (str): Diretório onde o arquivo de texto transcrito será salvo.
                          Será criado se não existir.
        chunk_length_ms (int): Duração de cada segmento de áudio em milissegundos para a transcrição.
                               (Padrão: 15 segundos).

    Returns:
        str: O texto transcrito do áudio ou uma mensagem de erro.
    """
    if not os.path.exists(caminho_audio):
        return f"{Cores.VERMELHO}❌ Erro: O arquivo de áudio '{caminho_audio}' não foi encontrado. Por favor, verifique o caminho.{Cores.RESET}"

    os.makedirs(output_dir, exist_ok=True)

    try:
        print(f"\n{Cores.CIANO}--- Iniciando Transcrição ---{Cores.RESET}")
        print(f"{Cores.AZUL}Usando o modelo Whisper:{Cores.RESET} '{Cores.NEGRITO}{modelo_whisper}{Cores.RESET}'")
        print(f"{Cores.AZUL}Arquivo de áudio selecionado:{Cores.RESET} '{Cores.NEGRITO}{caminho_audio}{Cores.RESET}'")
        print(f"{Cores.AMARELO}Carregando modelo Whisper '{modelo_whisper}'... (Isso pode demorar um pouco na primeira vez){Cores.RESET}")
        
        model = whisper.load_model(modelo_whisper)
        print(f"{Cores.VERDE}Modelo carregado com sucesso.{Cores.RESET}")

        print(f"{Cores.AMARELO}Preparando áudio para transcrição segmentada (chunks de {chunk_length_ms / 1000:.0f}s)...{Cores.RESET}")
        audio = AudioSegment.from_file(caminho_audio)
        audio_length_ms = len(audio)

        chunks = []
        for i in range(0, audio_length_ms, chunk_length_ms):
            chunks.append(audio[i:i + chunk_length_ms])

        full_transcription = []
        
        print(f"{Cores.CIANO}Iniciando transcrição do áudio...{Cores.RESET}")
        with tqdm(total=len(chunks), desc=f"{Cores.VERDE}Transcrevendo{Cores.RESET}", unit="chunk", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}") as pbar:
            for i, chunk in enumerate(chunks):
                temp_chunk_path = f"temp_chunk_{i}.wav"
                chunk.export(temp_chunk_path, format="wav")

                result = model.transcribe(temp_chunk_path, language="pt", fp16=False, suppress_tokens=[-1])
                full_transcription.append(result["text"])
                os.remove(temp_chunk_path)

                pbar.update(1)

        texto_transcrito = " ".join(full_transcription).strip()
        print(f"\n{Cores.VERDE}--- Transcrição Concluída ---{Cores.RESET}")
        print(f"{Cores.NEGRITO}Transcrição:{Cores.RESET} {texto_transcrito}")

        nome_arquivo_base = os.path.splitext(os.path.basename(caminho_audio))[0]
        caminho_arquivo_saida = os.path.join(output_dir, f"{nome_arquivo_base}_transcricao.txt")
        
        with open(caminho_arquivo_saida, "w", encoding="utf-8") as f:
            f.write(texto_transcrito)
        print(f"{Cores.VERDE}💾 Transcrição salva em: '{caminho_arquivo_saida}'{Cores.RESET}")

        return texto_transcrito
        
    except Exception as e:
        print(f"{Cores.VERMELHO}❌ Ocorreu um erro inesperado durante a transcrição com Whisper: {e}{Cores.RESET}")
        print(f"{Cores.AMARELO}   Por favor, verifique se o FFmpeg está instalado corretamente e acessível no seu PATH.{Cores.RESET}")
        print(f"{Cores.AMARELO}   Você pode baixar o FFmpeg em: {Cores.AZUL}https://ffmpeg.org/download.html{Cores.RESET}")
        print(f"{Cores.AMARELO}   Verifique também se o modelo Whisper ('base', 'small', etc.) foi baixado com sucesso.{Cores.RESET}")
        return f"Erro na transcrição: {e}"

if __name__ == "__main__":
    limpar_tela() # Limpa a tela no início

    print(f"{Cores.MAGENTA}{Cores.NEGRITO}Bem-vindo ao Transcritor de Áudio com Whisper!{Cores.RESET}")
    print("Este programa transcreve áudio para texto e salva o resultado em um arquivo.\n")
    
    # Carrega configurações anteriores
    config = carregar_config()
    ultimo_diretorio_saida = config.get('ultimo_diretorio_saida', 'transcricoes') # Pega o último ou usa 'transcricoes'

    while True: # Loop principal para permitir múltiplas transcrições
        caminho_do_audio_input = ""
        while True:
            caminho_do_audio_input = input(f"{Cores.CIANO}👉 Por favor, digite o caminho completo do arquivo de áudio (ex: C:\\audios\\meu_audio.mp3): {Cores.RESET}").strip()
            if os.path.exists(caminho_do_audio_input):
                break
            else:
                print(f"{Cores.VERMELHO}❗ Arquivo não encontrado. Por favor, verifique o caminho e tente novamente.{Cores.RESET}")
        
        modelos_disponiveis = ["tiny", "base", "small", "medium", "large"]
        modelo_padrao_idx = modelos_disponiveis.index("base") if "base" in modelos_disponiveis else 0

        print(f"\n{Cores.CIANO}Escolha um modelo Whisper:{Cores.RESET}")
        for i, modelo in enumerate(modelos_disponiveis):
            print(f"  {Cores.NEGRITO}[{i+1}]{Cores.RESET} {modelo.capitalize()}{' (Padrão)' if i == modelo_padrao_idx else ''}")
        
        modelo_a_usar = modelo_padrao_idx
        while True:
            escolha_modelo = input(
                f"{Cores.CIANO}Digite o NÚMERO correspondente ao modelo (ou ENTER para '{modelos_disponiveis[modelo_padrao_idx]}'): {Cores.RESET}"
            ).strip()

            if not escolha_modelo: # Se o usuário pressionar Enter
                modelo_a_usar = modelos_disponiveis[modelo_padrao_idx]
                break
            try:
                idx = int(escolha_modelo) - 1
                if 0 <= idx < len(modelos_disponiveis):
                    modelo_a_usar = modelos_disponiveis[idx]
                    break
                else:
                    print(f"{Cores.VERMELHO}❗ Número inválido. Por favor, digite um número entre 1 e {len(modelos_disponiveis)}.{Cores.RESET}")
            except ValueError:
                print(f"{Cores.VERMELHO}❗ Entrada inválida. Por favor, digite o NÚMERO ou pressione ENTER.{Cores.RESET}")

        # Pergunta o diretório de saída, sugerindo o último usado
        diretorio_saida_transcricao = input(f"{Cores.CIANO}📁 Digite o nome do diretório para salvar as transcrições (Padrão ou Último Usado: '{ultimo_diretorio_saida}'): {Cores.RESET}").strip()
        if not diretorio_saida_transcricao:
            diretorio_saida_transcricao = ultimo_diretorio_saida
        
        # Salva o diretório escolhido para uso futuro
        config['ultimo_diretorio_saida'] = diretorio_saida_transcricao
        salvar_config(config)

        # Chama a função de transcrição com as entradas do usuário
        transcricao_final = transcrever_audio_whisper(
            caminho_do_audio_input, 
            modelo_whisper=modelo_a_usar,
            output_dir=diretorio_saida_transcricao
        )
        
        print(f"\n{Cores.MAGENTA}--- Processo de Transcrição Concluído ---{Cores.RESET}")
        
        # Pergunta se o usuário deseja transcrever outro áudio
        continuar_processando = input(f"{Cores.CIANO}Deseja transcrever outro áudio? (s/n): {Cores.RESET}").strip().lower()
        if continuar_processando != 's':
            break # Sai do loop principal
        
        limpar_tela() # Limpa a tela para a próxima transcrição

    print(f"\n{Cores.MAGENTA}👋 Obrigado por usar o Transcritor de Áudio!{Cores.RESET}")
    print(f"{Cores.MAGENTA}--- Programa Encerrado ---{Cores.RESET}")