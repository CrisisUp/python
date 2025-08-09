import os
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import clips_array, TextClip, ColorClip # Para future features se precisar
import json # Para salvar/carregar configurações de saída
import sys # Para sys.exit para saídas limpas
import time # Para um pequeno atraso, se necessário

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
CONFIG_FILE = "video_cutter_config.json"

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
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def formatar_duracao(segundos):
    """Formata a duração de segundos para HH:MM:SS."""
    minutos, segundos_restantes = divmod(int(segundos), 60)
    horas, minutos_restantes = divmod(minutos, 60)
    return f"{horas:02d}:{minutos_restantes:02d}:{segundos_restantes:02d}"

def cortar_video(caminho_video_entrada, caminho_video_saida, inicio_seg, fim_seg):
    """
    Corta um segmento de um arquivo de vídeo.

    Args:
        caminho_video_entrada (str): O caminho completo para o arquivo de vídeo de entrada.
        caminho_video_saida (str): O caminho completo para o arquivo de vídeo de saída.
        inicio_seg (float): O tempo de início do corte em segundos.
        fim_seg (float): O tempo de fim do corte em segundos.

    Returns:
        bool: True se o corte for bem-sucedido, False caso contrário.
    """
    if not os.path.exists(caminho_video_entrada):
        print(f"{Cores.VERMELHO}❌ Erro: O arquivo de vídeo de entrada '{caminho_video_entrada}' não foi encontrado.{Cores.RESET}")
        return False

    clip = None # Inicializa clip para garantir que seja definido
    try:
        print(f"{Cores.CIANO}🔄 Carregando vídeo:{Cores.RESET} '{Cores.NEGRITO}{caminho_video_entrada}{Cores.RESET}'...")
        clip = VideoFileClip(caminho_video_entrada)

        duracao_total_seg = clip.duration
        if inicio_seg < 0 or fim_seg > duracao_total_seg or inicio_seg >= fim_seg:
            print(f"{Cores.VERMELHO}❌ Erro: Tempos de corte inválidos. O vídeo tem {formatar_duracao(duracao_total_seg)} ({duracao_total_seg:.2f} segundos).{Cores.RESET}")
            print(f"{Cores.AMARELO}   Início: {inicio_seg:.2f}s, Fim: {fim_seg:.2f}s.{Cores.RESET}")
            return False

        print(f"{Cores.AMARELO}✂️ Cortando vídeo de {formatar_duracao(inicio_seg)} a {formatar_duracao(fim_seg)}...{Cores.RESET}")
        segmento_cortado = clip.subclip(inicio_seg, fim_seg)

        # Salva o arquivo de saída. O formato é inferido pela extensão do arquivo de saída.
        formato_saida = caminho_video_saida.split('.')[-1]
        
        print(f"{Cores.CIANO}💾 Salvando vídeo cortado em:{Cores.RESET} '{Cores.NEGRITO}{caminho_video_saida}{Cores.RESET}' no formato {Cores.NEGRITO}{formato_saida.upper()}{Cores.RESET}...")
        
        # O write_videofile tem um progresso embutido que já é exibido.
        segmento_cortado.write_videofile(caminho_video_saida, codec="libx264", audio_codec="aac")
        
        print(f"{Cores.VERDE}✅ Corte concluído com sucesso!{Cores.RESET}")
        return True

    except Exception as e:
        print(f"{Cores.VERMELHO}❌ Ocorreu um erro ao cortar o vídeo: {e}{Cores.RESET}")
        print(f"{Cores.AMARELO}   Isso pode ser devido a um arquivo de vídeo corrompido, codecs não suportados ou problemas com o FFmpeg.{Cores.RESET}")
        print(f"{Cores.AMARELO}   Certifique-se de que o FFmpeg está instalado corretamente e acessível no seu PATH.{Cores.RESET}")
        print(f"{Cores.AMARELO}   Você pode baixar o FFmpeg em: {Cores.AZUL}https://ffmpeg.org/download.html{Cores.RESET}")
        return False
    finally:
        if clip:
            clip.close() # Libera os recursos do vídeo

def obter_duracao_video(caminho_video):
    """
    Retorna a duração de um arquivo de vídeo em segundos.
    """
    clip = None
    try:
        clip = VideoFileClip(caminho_video)
        duracao = clip.duration
        return duracao
    except Exception as e:
        print(f"{Cores.VERMELHO}❌ Erro ao obter a duração do vídeo: {e}{Cores.RESET}")
        print(f"{Cores.AMARELO}   Isso pode indicar um arquivo de vídeo corrompido, formato não suportado ou problema com o FFmpeg.{Cores.RESET}")
        print(f"{Cores.AMARELO}   Certifique-se de que o FFmpeg está instalado e acessível no seu PATH.{Cores.RESET}")
        print(f"{Cores.AMARELO}   Você pode baixar o FFmpeg em: {Cores.AZUL}https://ffmpeg.org/download.html{Cores.RESET}")
        return None
    finally:
        if clip:
            clip.close() # Libera os recursos do vídeo

if __name__ == "__main__":
    limpar_tela()

    print(f"{Cores.MAGENTA}{Cores.NEGRITO}--- 🎬 Ferramenta de Corte de Vídeo ---{Cores.RESET}")
    print("Este programa permite cortar um segmento de um arquivo de vídeo.")
    print(f"{Cores.AMARELO}Atenção: O FFmpeg é NECESSÁRIO para esta ferramenta funcionar!{Cores.RESET}")
    print(f"{Cores.AZUL}Link para download do FFmpeg:{Cores.RESET} {Cores.NEGRITO}https://ffmpeg.org/download.html{Cores.RESET}\n")

    config = carregar_config()
    ultimo_diretorio_saida_video = config.get('ultimo_diretorio_saida_video', '') # Vazio para não sugerir um diretório se nunca usado

    while True: # Loop principal para permitir múltiplos cortes
        print(f"{Cores.AMARELO}Dica: No Windows, você pode arrastar o arquivo de vídeo para o terminal e apertar ENTER!{Cores.RESET}")
        caminho_entrada = ""
        while True:
            caminho_entrada = input(f"{Cores.CIANO}👉 Digite o caminho completo do arquivo de vídeo de entrada (ou 'sair' para encerrar): {Cores.RESET}").strip()
            
            if caminho_entrada.lower() == 'sair':
                break
            
            if os.path.exists(caminho_entrada):
                extensao = os.path.splitext(caminho_entrada)[1].lower()
                # Lista de extensões de vídeo comuns que o FFmpeg/MoviePy geralmente suportam
                extensoes_video_validas = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.mpeg', '.mpg']
                
                if extensao in extensoes_video_validas:
                    break
                else:
                    print(f"{Cores.VERMELHO}❗ Extensão de arquivo '{extensao}' não é um formato de vídeo comum. Por favor, verifique ou tente um arquivo diferente.{Cores.RESET}")
                    print(f"{Cores.AMARELO}   Extensões comuns: {', '.join(extensoes_video_validas)}{Cores.RESET}")
            else:
                print(f"{Cores.VERMELHO}❗ Arquivo não encontrado. Por favor, verifique o caminho e tente novamente.{Cores.RESET}")

        if caminho_entrada.lower() == 'sair':
            break 

        duracao_segundos = obter_duracao_video(caminho_entrada)

        if duracao_segundos is None:
            print(f"{Cores.VERMELHO}Não foi possível processar a duração do vídeo. O arquivo pode estar corrompido ou o FFmpeg não está configurado. Pulando para o próximo.{Cores.RESET}")
            continuar = input(f"{Cores.CIANO}Deseja cortar outro vídeo? (s/n): {Cores.RESET}").strip().lower()
            if continuar != 's':
                break
            else:
                limpar_tela()
                continue
        
        print(f"\n{Cores.AZUL}🎬 O vídeo tem uma duração total de: {Cores.NEGRITO}{formatar_duracao(duracao_segundos)}{Cores.RESET} ({duracao_segundos:.2f} segundos).")
        print(f"{Cores.CIANO}Agora, insira os tempos de início e fim para o corte (em segundos).{Cores.RESET}")

        inicio_segundos = -1
        fim_segundos = -1

        while True:
            try:
                inicio_input = input(f"{Cores.AZUL}⏰ Digite o tempo de início do corte (0 a {duracao_segundos:.2f} segundos): {Cores.RESET}").replace(',', '.').strip()
                if inicio_input.lower() == 'sair': raise KeyboardInterrupt
                inicio_segundos = float(inicio_input)
                
                if inicio_segundos < 0 or inicio_segundos >= duracao_segundos:
                    print(f"{Cores.VERMELHO}❗ Tempo de início inválido. Deve ser entre 0 e {duracao_segundos:.2f} segundos.{Cores.RESET}")
                    continue

                fim_input = input(f"{Cores.AZUL}⏱️ Digite o tempo de fim do corte ({inicio_segundos:.2f} a {duracao_segundos:.2f} segundos): {Cores.RESET}").replace(',', '.').strip()
                if fim_input.lower() == 'sair': raise KeyboardInterrupt
                fim_segundos = float(fim_input)

                if fim_segundos <= inicio_segundos or fim_segundos > duracao_segundos:
                    print(f"{Cores.VERMELHO}❗ Tempo de fim inválido. Deve ser maior que o tempo de início e até {duracao_segundos:.2f} segundos.{Cores.RESET}")
                    continue
                break
            except ValueError:
                print(f"{Cores.VERMELHO}❗ Entrada inválida. Por favor, digite um número para o tempo.{Cores.RESET}")
            except KeyboardInterrupt:
                print(f"\n{Cores.AMARELO}Operação cancelada pelo usuário.{Cores.RESET}")
                caminho_entrada = 'sair'
                break

        if caminho_entrada.lower() == 'sair':
            break

        nome_arquivo_original, extensao = os.path.splitext(os.path.basename(caminho_entrada))
        diretorio_original = os.path.dirname(caminho_entrada)
        
        extensao_limpa = extensao.lstrip('.')
        if not extensao_limpa:
            extensao_limpa = 'mp4' # Padrão para MP4 se não houver extensão no original

        caminho_saida_sugerido = os.path.join(diretorio_original, f"{nome_arquivo_original}_cortado.{extensao_limpa}")

        # Sugestão do último diretório usado
        diretorio_base_sugerido = os.path.dirname(caminho_saida_sugerido) if not ultimo_diretorio_saida_video else ultimo_diretorio_saida_video
        nome_arquivo_sugerido = os.path.basename(caminho_saida_sugerido)
        caminho_saida_completo_sugerido = os.path.join(diretorio_base_sugerido, nome_arquivo_sugerido)

        caminho_saida = input(f"📁 {Cores.CIANO}Digite o caminho para salvar o vídeo cortado (Sugestão: {Cores.NEGRITO}{caminho_saida_completo_sugerido}{Cores.RESET}{Cores.CIANO} ou 'sair'): {Cores.RESET}").strip()
        
        if caminho_saida.lower() == 'sair':
            break

        if not caminho_saida:
            caminho_saida = caminho_saida_completo_sugerido
        
        # Garante que o caminho de saída tem uma extensão válida
        if not os.path.splitext(caminho_saida)[1]:
            caminho_saida += f".{extensao_limpa}"

        # Salva o diretório final escolhido para a próxima vez
        config['ultimo_diretorio_saida_video'] = os.path.dirname(caminho_saida)
        salvar_config(config)

        print(f"\n{Cores.CIANO}--- Processando corte... Isso pode levar um tempo. ---{Cores.RESET}")
        if cortar_video(caminho_entrada, caminho_saida, inicio_segundos, fim_segundos):
            print(f"{Cores.VERDE}🎉 Vídeo cortado salvo com sucesso em: {Cores.NEGRITO}{caminho_saida}{Cores.RESET}")
        else:
            print(f"{Cores.VERMELHO}❗ Não foi possível cortar o vídeo. Por favor, verifique os detalhes acima.{Cores.RESET}")

        continuar_processando = input(f"\n{Cores.CIANO}Deseja cortar outro vídeo? (s/n): {Cores.RESET}").strip().lower()
        if continuar_processando != 's':
            break

        limpar_tela()

    print(f"\n{Cores.MAGENTA}👋 Obrigado por usar a ferramenta de corte de vídeo!{Cores.RESET}")
    print(f"{Cores.MAGENTA}--- 🎬 Programa Encerrado ---{Cores.RESET}")