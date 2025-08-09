import os
from pydub import AudioSegment
from pydub.utils import mediainfo # Para obter a duração do áudio

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
        print(f"❌ Erro: O arquivo de áudio de entrada '{caminho_audio_entrada}' não foi encontrado.")
        return False

    try:
        print(f"🔄 Carregando áudio: '{caminho_audio_entrada}'...")
        audio = AudioSegment.from_file(caminho_audio_entrada)

        duracao_total_ms = len(audio)
        if inicio_ms < 0 or fim_ms > duracao_total_ms or inicio_ms >= fim_ms:
            print(f"❌ Erro: Tempos de corte inválidos. O áudio tem {formatar_duracao(duracao_total_ms / 1000)}.")
            print(f"   Início: {inicio_ms / 1000:.2f}s, Fim: {fim_ms / 1000:.2f}s")
            return False

        segmento_cortado = audio[inicio_ms:fim_ms]

        # Mantém o formato original ou o que foi especificado na saída
        formato_saida = caminho_audio_saida.split('.')[-1]
        
        print(f"💾 Salvando áudio cortado em: '{caminho_audio_saida}' no formato {formato_saida.upper()}...")
        segmento_cortado.export(caminho_audio_saida, format=formato_saida)
        print("✅ Corte concluído com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Ocorreu um erro ao cortar o áudio: {e}")
        print("   Por favor, verifique se o FFmpeg está instalado corretamente e acessível no seu PATH.")
        print("   Você pode baixar o FFmpeg em: https://ffmpeg.org/download.html")
        return False

def obter_duracao_audio(caminho_audio):
    """
    Retorna a duração de um arquivo de áudio em segundos.
    """
    try:
        info = mediainfo(caminho_audio)
        duracao = float(info.get('duration', 0)) # Usar .get para segurança
        return duracao
    except Exception as e:
        print(f"❌ Erro ao obter a duração do áudio: {e}")
        print("   Certifique-se de que o FFmpeg está instalado e acessível no seu PATH.")
        print("   Você pode baixar o FFmpeg em: https://ffmpeg.org/download.html")
        return None

if __name__ == "__main__":
    print("--- ✂️ Ferramenta de Corte de Áudio ---")
    print("Este programa permite cortar um segmento de um arquivo de áudio.")
    print("Certifique-se de ter o FFmpeg instalado para melhor compatibilidade de áudio.")
    print("Link para download do FFmpeg: https://ffmpeg.org/download.html\n")

    while True: # Loop principal para permitir múltiplos cortes
        caminho_entrada = ""
        while True:
            caminho_entrada = input("👉 Digite o caminho completo do arquivo de áudio de entrada (ex: C:\\audios\\original.mp3 ou meu_audio.wav): ").strip()
            if os.path.exists(caminho_entrada):
                break
            else:
                print("❗ Arquivo não encontrado. Por favor, verifique o caminho e tente novamente.")

        duracao_segundos = obter_duracao_audio(caminho_entrada)

        if duracao_segundos is None:
            print("Não foi possível processar a duração do áudio. Por favor, tente outro arquivo.")
            continuar = input("Deseja cortar outro áudio? (s/n): ").strip().lower()
            if continuar != 's':
                break # Sai do loop principal
            else:
                continue # Volta para o início do loop principal para outro arquivo
        
        print(f"\n🎧 O áudio tem uma duração total de: {formatar_duracao(duracao_segundos)} ({duracao_segundos:.2f} segundos).")
        print("Agora, insira os tempos de início e fim para o corte (em segundos).")

        inicio_segundos = -1
        fim_segundos = -1

        while True:
            try:
                # Permite vírgula ou ponto para decimais
                inicio_input = input(f"⏰ Digite o tempo de início do corte (0 a {duracao_segundos:.2f} segundos): ").replace(',', '.').strip()
                inicio_segundos = float(inicio_input)
                
                if inicio_segundos < 0 or inicio_segundos >= duracao_segundos:
                    print(f"❗ Tempo de início inválido. Deve ser entre 0 e {duracao_segundos:.2f} segundos.")
                    continue

                fim_input = input(f"⏱️ Digite o tempo de fim do corte ({inicio_segundos:.2f} a {duracao_segundos:.2f} segundos): ").replace(',', '.').strip()
                fim_segundos = float(fim_input)

                if fim_segundos <= inicio_segundos or fim_segundos > duracao_segundos:
                    print(f"❗ Tempo de fim inválido. Deve ser maior que o tempo de início e até {duracao_segundos:.2f} segundos.")
                    continue
                break
            except ValueError:
                print("❗ Entrada inválida. Por favor, digite um número para o tempo.")

        # Converte para milissegundos para pydub
        inicio_ms = int(inicio_segundos * 1000)
        fim_ms = int(fim_segundos * 1000)

        # Sugere um nome para o arquivo de saída
        nome_arquivo_original, extensao = os.path.splitext(os.path.basename(caminho_entrada))
        diretorio_original = os.path.dirname(caminho_entrada)
        
        # Garante que a extensão seja inferida corretamente ou seja a mesma do original
        extensao_limpa = extensao.lstrip('.') # Remove o ponto inicial da extensão
        if not extensao_limpa: # Caso o arquivo não tenha extensão
            extensao_limpa = 'wav' # Padrão para WAV se não houver extensão

        caminho_saida_sugerido = os.path.join(diretorio_original, f"{nome_arquivo_original}_cortado.{extensao_limpa}")

        caminho_saida = input(f"📁 Digite o caminho para salvar o áudio cortado (Sugestão: {caminho_saida_sugerido}): ").strip()
        if not caminho_saida:
            caminho_saida = caminho_saida_sugerido
        
        # Garante que o caminho de saída tem uma extensão válida
        if not os.path.splitext(caminho_saida)[1]:
            caminho_saida += f".{extensao_limpa}" # Adiciona a extensão sugerida se não houver

        print("\n--- Processando corte... ---")
        if cortar_audio(caminho_entrada, caminho_saida, inicio_ms, fim_ms):
            print(f"🎉 Áudio cortado salvo com sucesso em: {caminho_saida}")
        else:
            print("❗ Não foi possível cortar o áudio. Por favor, verifique os detalhes acima.")

        continuar_processando = input("\nDeseja cortar outro áudio? (s/n): ").strip().lower()
        if continuar_processando != 's':
            break # Sai do loop principal

    print("\n👋 Obrigado por usar a ferramenta de corte de áudio!")
    print("--- ✂️ Programa Encerrado ---")