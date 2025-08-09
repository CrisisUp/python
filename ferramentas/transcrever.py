import whisper
import os # Importa o módulo os para lidar com caminhos de arquivo

def transcrever_audio_whisper(caminho_audio, modelo_whisper="base"):
    """
    Transcreve um arquivo de áudio para texto usando o modelo Whisper da OpenAI.

    Args:
        caminho_audio (str): O caminho completo para o arquivo de áudio.
        modelo_whisper (str): O nome do modelo Whisper a ser usado (ex: "tiny", "base", "small", "medium", "large").
                              Modelos maiores são mais precisos, mas exigem mais recursos e tempo.

    Returns:
        str: O texto transcrito do áudio ou uma mensagem de erro.
    """
    if not os.path.exists(caminho_audio):
        return f"Erro: O arquivo de áudio '{caminho_audio}' não foi encontrado. Por favor, verifique o caminho."

    try:
        print(f"\n--- Iniciando Transcrição ---")
        print(f"Usando o modelo Whisper: '{modelo_whisper}'")
        print(f"Arquivo de áudio selecionado: '{caminho_audio}'")
        print(f"Carregando modelo Whisper '{modelo_whisper}'... (Isso pode demorar um pouco na primeira vez)")
        
        # Carrega o modelo. Ele será baixado se ainda não estiver presente.
        model = whisper.load_model(modelo_whisper)
        
        print("Modelo carregado com sucesso. Transcrevendo áudio...")
        
        # Realiza a transcrição. 'language="pt"' especifica o idioma português.
        result = model.transcribe(caminho_audio, language="pt")

        texto_transcrito = result["text"]
        print(f"\n--- Transcrição Concluída ---")
        print(f"Transcrição: {texto_transcrito}")
        return texto_transcrito
        
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a transcrição com Whisper: {e}")
        print("Certifique-se de que o FFmpeg está instalado e acessível no seu PATH.")
        print("Para instalar o FFmpeg, visite: https://ffmpeg.org/download.html")
        return f"Erro na transcrição: {e}"

if __name__ == "__main__":
    print("Bem-vindo ao Transcritor de Áudio com Whisper!")
    
    # Pergunta ao usuário o caminho do arquivo de áudio
    caminho_do_audio_input = input("Por favor, digite o caminho completo do arquivo de áudio (ex: C:\\audios\\meu_audio.mp3): ").strip()
    
    # Opcional: permite ao usuário escolher o modelo
    modelos_disponiveis = ["tiny", "base", "small", "medium", "large"]
    modelo_padrao = "base"
    
    while True:
        modelo_escolhido_input = input(
            f"Escolha um modelo Whisper ({', '.join(modelos_disponiveis)}). "
            f"Padrão é '{modelo_padrao}'. (Pressione Enter para usar o padrão): "
        ).strip().lower()

        if not modelo_escolhido_input: # Se o usuário pressionar Enter
            modelo_a_usar = modelo_padrao
            break
        elif modelo_escolhido_input in modelos_disponiveis:
            modelo_a_usar = modelo_escolhido_input
            break
        else:
            print(f"Modelo inválido. Por favor, escolha um dos seguintes: {', '.join(modelos_disponiveis)}")

    # Chama a função de transcrição com as entradas do usuário
    transcricao_final = transcrever_audio_whisper(caminho_do_audio_input, modelo_whisper=modelo_a_usar)
    
    # Exibe a transcrição final (já impressa dentro da função, mas repetimos para clareza)
    # print(f"\n--- Transcrição Final ---")
    # print(transcricao_final) # Isso será a mensagem de erro se algo deu errado