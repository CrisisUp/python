import os
from pydub import AudioSegment
from pydub.utils import mediainfo # Para obter a duração do áudio

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
        print(f"Erro: O arquivo de áudio de entrada '{caminho_audio_entrada}' não foi encontrado.")
        return False

    try:
        print(f"Carregando áudio: '{caminho_audio_entrada}'...")
        audio = AudioSegment.from_file(caminho_audio_entrada)

        # Verifica se os tempos de corte são válidos
        duracao_total_ms = len(audio)
        if inicio_ms < 0 or fim_ms > duracao_total_ms or inicio_ms >= fim_ms:
            print(f"Erro: Tempos de corte inválidos. O áudio tem {duracao_total_ms / 1000:.2f} segundos.")
            print(f"Início: {inicio_ms / 1000:.2f}s, Fim: {fim_ms / 1000:.2f}s")
            return False

        # Realiza o corte
        segmento_cortado = audio[inicio_ms:fim_ms]

        # Salva o arquivo de saída. O formato é inferido pela extensão do arquivo de saída.
        print(f"Salvando áudio cortado em: '{caminho_audio_saida}'...")
        segmento_cortado.export(caminho_audio_saida, format=caminho_audio_saida.split('.')[-1])
        print("Corte concluído com sucesso!")
        return True

    except Exception as e:
        print(f"Ocorreu um erro ao cortar o áudio: {e}")
        print("Certifique-se de que o FFmpeg está instalado e acessível no seu PATH.")
        return False

def obter_duracao_audio(caminho_audio):
    """
    Retorna a duração de um arquivo de áudio em segundos.
    """
    try:
        info = mediainfo(caminho_audio)
        duracao = float(info['duration'])
        return duracao
    except Exception as e:
        print(f"Erro ao obter a duração do áudio: {e}")
        print("Certifique-se de que o FFmpeg está instalado e acessível no seu PATH.")
        return None

if __name__ == "__main__":
    print("--- Ferramenta de Corte de Áudio ---")

    while True:
        caminho_entrada = input("Digite o caminho completo do arquivo de áudio de entrada (ex: C:\\audios\\original.mp3): ").strip()
        if os.path.exists(caminho_entrada):
            break
        else:
            print("Arquivo não encontrado. Por favor, verifique o caminho e tente novamente.")

    duracao_segundos = obter_duracao_audio(caminho_entrada)

    if duracao_segundos is None:
        print("Não foi possível processar a duração do áudio. Saindo.")
    else:
        print(f"\nO áudio tem uma duração de: {duracao_segundos:.2f} segundos.")
        print("Você pode inserir os tempos de início e fim em segundos para o corte.")

        while True:
            try:
                inicio_segundos = float(input(f"Digite o tempo de início do corte (em segundos, 0 a {duracao_segundos:.2f}): ").replace(',', '.'))
                if inicio_segundos < 0 or inicio_segundos > duracao_segundos:
                    print("Tempo de início inválido. Fora do intervalo do áudio.")
                    continue

                fim_segundos = float(input(f"Digite o tempo de fim do corte (em segundos, {inicio_segundos:.2f} a {duracao_segundos:.2f}): ").replace(',', '.'))
                if fim_segundos <= inicio_segundos or fim_segundos > duracao_segundos:
                    print("Tempo de fim inválido. Deve ser maior que o tempo de início e dentro do intervalo do áudio.")
                    continue
                break
            except ValueError:
                print("Entrada inválida. Por favor, digite um número.")

        # Converte para milissegundos, pois pydub trabalha com milissegundos
        inicio_ms = int(inicio_segundos * 1000)
        fim_ms = int(fim_segundos * 1000)

        # Sugere um nome para o arquivo de saída
        nome_arquivo_original, extensao = os.path.splitext(os.path.basename(caminho_entrada))
        diretorio_original = os.path.dirname(caminho_entrada)
        caminho_saida_sugerido = os.path.join(diretorio_original, f"{nome_arquivo_original}_cortado{extensao}")

        caminho_saida = input(f"Digite o caminho para salvar o áudio cortado (Sugestão: {caminho_saida_sugerido}): ").strip()
        if not caminho_saida:
            caminho_saida = caminho_saida_sugerido

        print("\nProcessando corte...")
        if cortar_audio(caminho_entrada, caminho_saida, inicio_ms, fim_ms):
            print(f"Áudio cortado salvo com sucesso em: {caminho_saida}")
        else:
            print("Não foi possível cortar o áudio.")

    print("\n--- Processo Concluído ---")