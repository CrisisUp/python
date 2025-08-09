import os
from pydub import AudioSegment
from pydub.utils import mediainfo
# Importa CouldntDecodeError, e outros erros de FFmpeg serão capturados por Exception
from pydub.exceptions import CouldntDecodeError 

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

def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def formatar_duracao(segundos):
    """Formata a duração de segundos para MM:SS ou HH:MM:SS."""
    minutos, segundos_restantes = divmod(int(segundos), 60)
    horas, minutos_restantes = divmod(minutos, 60)
    if horas > 0:
        return f"{horas:02d}:{minutos_restantes:02d}:{segundos_restantes:02d}"
    return f"{minutos:02d}:{segundos_restantes:02d}"

def cortar_audio(caminho_audio_entrada, caminho_audio_saida, inicio_ms, fim_ms):
    """
    Corta um segmento de um arquivo de áudio.

    Args:
        caminho_audio_entrada (str): O caminho completo para o arquivo de áudio de entrada.
        caminho_audio_saida (str): O caminho completo para o arquivo de áudio de saída.
        inicio_ms (int): O tempo de início do corte em milissegundos.
        fim_ms (int): O tempo de fim do corte em milissegundos.

    Returns:
        bool: True se o corte for bem-sucedido, False caso contrário.
    """
    if not os.path.exists(caminho_audio_entrada):
        print(f"{Cores.VERMELHO}❌ Erro: O arquivo de áudio de entrada '{caminho_audio_entrada}' não foi encontrado.{Cores.RESET}")
        return False

    try:
        print(f"{Cores.CIANO}🔄 Carregando áudio:{Cores.RESET} '{Cores.NEGRITO}{caminho_audio_entrada}{Cores.RESET}'...")
        audio = AudioSegment.from_file(caminho_audio_entrada)

        duracao_total_ms = len(audio)
        if inicio_ms < 0 or fim_ms > duracao_total_ms or inicio_ms >= fim_ms:
            print(f"{Cores.VERMELHO}❌ Erro: Tempos de corte inválidos. O áudio tem {formatar_duracao(duracao_total_ms / 1000)} ({duracao_total_ms / 1000:.2f}s).{Cores.RESET}")
            print(f"{Cores.AMARELO}   Início: {inicio_ms / 1000:.2f}s, Fim: {fim_ms / 1000:.2f}s.{Cores.RESET}")
            return False

        segmento_cortado = audio[inicio_ms:fim_ms]

        # Mantém o formato original ou o que foi especificado na saída
        formato_saida = caminho_audio_saida.split('.')[-1]
        
        print(f"{Cores.CIANO}💾 Salvando áudio cortado em:{Cores.RESET} '{Cores.NEGRITO}{caminho_audio_saida}{Cores.RESET}' no formato {Cores.NEGRITO}{formato_saida.upper()}{Cores.RESET}...")
        segmento_cortado.export(caminho_audio_saida, format=formato_saida)
        print(f"{Cores.VERDE}✅ Corte concluído com sucesso!{Cores.RESET}")
        return True

    except CouldntDecodeError as e:
        print(f"{Cores.VERMELHO}❌ Erro de decodificação de áudio ao cortar: {e}{Cores.RESET}")
        print(f"{Cores.AMARELO}   Isso pode indicar um arquivo de áudio corrompido ou um formato não suportado. Verifique o FFmpeg.{Cores.RESET}")
        return False
    except Exception as e: # Este bloco agora vai capturar FFmpegRuntimeError e outros erros gerais
        print(f"{Cores.VERMELHO}❌ Ocorreu um erro inesperado (possível problema com FFmpeg) ao cortar o áudio: {e}{Cores.RESET}")
        print(f"{Cores.AMARELO}   Por favor, verifique se o FFmpeg está instalado corretamente e acessível no seu PATH.{Cores.RESET}")
        print(f"{Cores.AMARELO}   Você pode baixar o FFmpeg em: {Cores.AZUL}https://ffmpeg.org/download.html{Cores.RESET}")
        return False

def obter_duracao_audio(caminho_audio):
    """
    Retorna a duração de um arquivo de áudio em segundos.
    """
    try:
        info = mediainfo(caminho_audio)
        duracao = float(info.get('duration', 0))
        return duracao
    except CouldntDecodeError as e:
        print(f"{Cores.VERMELHO}❌ Erro de decodificação de áudio ao obter duração: {e}{Cores.RESET}")
        print(f"{Cores.AMARELO}   Isso pode indicar um arquivo de áudio corrompido ou formato não suportado. Verifique o FFmpeg.{Cores.RESET}")
        return None
    except Exception as e: # Este bloco agora vai capturar FFmpegRuntimeError e outros erros gerais
        print(f"{Cores.VERMELHO}❌ Ocorreu um erro inesperado (possível problema com FFmpeg) ao obter a duração do áudio: {e}{Cores.RESET}")
        print(f"{Cores.AMARELO}   Certifique-se de que o FFmpeg está instalado e acessível no seu PATH.{Cores.RESET}")
        print(f"{Cores.AMARELO}   Você pode baixar o FFmpeg em: {Cores.AZUL}https://ffmpeg.org/download.html{Cores.RESET}")
        return None

if __name__ == "__main__":
    limpar_tela()

    print(f"{Cores.MAGENTA}{Cores.NEGRITO}--- ✂️ Ferramenta de Corte de Áudio ---{Cores.RESET}")
    print("Este programa permite cortar um segmento de um arquivo de áudio.")
    print(f"{Cores.AMARELO}Atenção: Certifique-se de ter o FFmpeg instalado para melhor compatibilidade de áudio!{Cores.RESET}")
    print(f"{Cores.AZUL}Link para download do FFmpeg:{Cores.RESET} {Cores.NEGRITO}https://ffmpeg.org/download.html{Cores.RESET}\n")

    while True: # Loop principal para permitir múltiplos cortes
        print(f"{Cores.AMARELO}Dica: No Windows, você pode arrastar o arquivo de áudio para o terminal e apertar ENTER!{Cores.RESET}")
        caminho_entrada = ""
        while True:
            caminho_entrada = input(f"{Cores.CIANO}👉 Digite o caminho completo do arquivo de áudio de entrada (ou 'sair' para encerrar): {Cores.RESET}").strip()
            
            if caminho_entrada.lower() == 'sair':
                break # Sai do loop de entrada do arquivo
            
            if os.path.exists(caminho_entrada):
                extensao = os.path.splitext(caminho_entrada)[1].lower()
                # Lista de extensões de áudio comuns que o FFmpeg geralmente suporta
                extensoes_audio_validas = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma', '.aiff', '.aif']
                
                if extensao in extensoes_audio_validas:
                    break
                else:
                    print(f"{Cores.VERMELHO}❗ Extensão de arquivo '{extensao}' não é um formato de áudio comum. Por favor, verifique ou tente um arquivo diferente.{Cores.RESET}")
                    print(f"{Cores.AMARELO}   Extensões comuns: {', '.join(extensoes_audio_validas)}{Cores.RESET}")
            else:
                print(f"{Cores.VERMELHO}❗ Arquivo não encontrado. Por favor, verifique o caminho e tente novamente.{Cores.RESET}")

        if caminho_entrada.lower() == 'sair':
            break # Sai do loop principal do programa

        duracao_segundos = obter_duracao_audio(caminho_entrada)

        if duracao_segundos is None:
            print(f"{Cores.VERMELHO}Não foi possível processar a duração do áudio. O arquivo pode estar corrompido ou o FFmpeg não está configurado. Pulando para o próximo.{Cores.RESET}")
            continuar = input(f"{Cores.CIANO}Deseja cortar outro áudio? (s/n): {Cores.RESET}").strip().lower()
            if continuar != 's':
                break
            else:
                limpar_tela()
                continue
        
        print(f"\n{Cores.AZUL}🎧 O áudio tem uma duração total de: {Cores.NEGRITO}{formatar_duracao(duracao_segundos)}{Cores.RESET} ({duracao_segundos:.2f} segundos).")
        print(f"{Cores.CIANO}Agora, insira os tempos de início e fim para o corte (em segundos).{Cores.RESET}")

        inicio_segundos = -1
        fim_segundos = -1

        while True:
            try:
                # Permite vírgula ou ponto para decimais
                inicio_input = input(f"{Cores.AZUL}⏰ Digite o tempo de início do corte (0 a {duracao_segundos:.2f} segundos): {Cores.RESET}").replace(',', '.').strip()
                if inicio_input.lower() == 'sair': raise KeyboardInterrupt # Simula Ctrl+C
                inicio_segundos = float(inicio_input)
                
                if inicio_segundos < 0 or inicio_segundos >= duracao_segundos:
                    print(f"{Cores.VERMELHO}❗ Tempo de início inválido. Deve ser entre 0 e {duracao_segundos:.2f} segundos.{Cores.RESET}")
                    continue

                fim_input = input(f"{Cores.AZUL}⏱️ Digite o tempo de fim do corte ({inicio_segundos:.2f} a {duracao_segundos:.2f} segundos): {Cores.RESET}").replace(',', '.').strip()
                if fim_input.lower() == 'sair': raise KeyboardInterrupt # Simula Ctrl+C
                fim_segundos = float(fim_input)

                if fim_segundos <= inicio_segundos or fim_segundos > duracao_segundos:
                    print(f"{Cores.VERMELHO}❗ Tempo de fim inválido. Deve ser maior que o tempo de início e até {duracao_segundos:.2f} segundos.{Cores.RESET}")
                    continue
                break
            except ValueError:
                print(f"{Cores.VERMELHO}❗ Entrada inválida. Por favor, digite um número para o tempo.{Cores.RESET}")
            except KeyboardInterrupt:
                print(f"\n{Cores.AMARELO}Operação cancelada pelo usuário.{Cores.RESET}")
                caminho_entrada = 'sair' # Define para sair do loop principal
                break


        if caminho_entrada.lower() == 'sair': # Verifica se o usuário cancelou
            break

        # Converte para milissegundos para pydub
        inicio_ms = int(inicio_segundos * 1000)
        fim_ms = int(fim_segundos * 1000)

        # Sugere um nome para o arquivo de saída
        nome_arquivo_original, extensao = os.path.splitext(os.path.basename(caminho_entrada))
        diretorio_original = os.path.dirname(caminho_entrada)
        
        extensao_limpa = extensao.lstrip('.')
        if not extensao_limpa:
            extensao_limpa = 'wav'

        caminho_saida_sugerido = os.path.join(diretorio_original, f"{nome_arquivo_original}_cortado.{extensao_limpa}")

        caminho_saida = input(f"📁 {Cores.CIANO}Digite o caminho para salvar o áudio cortado (Sugestão: {Cores.NEGRITO}{caminho_saida_sugerido}{Cores.RESET}{Cores.CIANO} ou 'sair'): {Cores.RESET}").strip()
        
        if caminho_saida.lower() == 'sair':
            break

        if not caminho_saida:
            caminho_saida = caminho_saida_sugerido
        
        if not os.path.splitext(caminho_saida)[1]:
            caminho_saida += f".{extensao_limpa}"

        print(f"\n{Cores.CIANO}--- Processando corte... ---{Cores.RESET}")
        if cortar_audio(caminho_entrada, caminho_saida, inicio_ms, fim_ms):
            print(f"{Cores.VERDE}🎉 Áudio cortado salvo com sucesso em: {Cores.NEGRITO}{caminho_saida}{Cores.RESET}")
        else:
            print(f"{Cores.VERMELHO}❗ Não foi possível cortar o áudio. Por favor, verifique os detalhes acima.{Cores.RESET}")

        continuar_processando = input(f"\n{Cores.CIANO}Deseja cortar outro áudio? (s/n): {Cores.RESET}").strip().lower()
        if continuar_processando != 's':
            break

        limpar_tela()

    print(f"\n{Cores.MAGENTA}👋 Obrigado por usar a ferramenta de corte de áudio!{Cores.RESET}")
    print(f"{Cores.MAGENTA}--- ✂️ Programa Encerrado ---{Cores.RESET}")