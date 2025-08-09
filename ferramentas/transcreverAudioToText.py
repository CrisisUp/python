import whisper

def transcrever_audio_whisper(caminho_audio, modelo_whisper="base"):
    try:
        print(f"Carregando modelo Whisper '{modelo_whisper}'...")
        model = whisper.load_model(modelo_whisper)
        print("Modelo carregado. Transcrevendo áudio...")
        result = model.transcribe(caminho_audio, language="pt") # "pt" para português

        texto_transcrito = result["text"]
        print(f"Transcrição: {texto_transcrito}")
        return texto_transcrito
    except FileNotFoundError:
        print(f"Erro: O arquivo de áudio '{caminho_audio}' não foi encontrado.")
        return f"Erro: O arquivo de áudio '{caminho_audio}' não foi encontrado."
    except Exception as e:
        print(f"Ocorreu um erro durante a transcrição com Whisper: {e}")
        return f"Ocorreu um erro durante a transcrição com Whisper: {e}"

if __name__ == "__main__":
    caminho_do_seu_audio = "seu_audio.wav" # Ou "seu_audio.mp3", etc.
    # Modelos disponíveis: "tiny", "base", "small", "medium", "large"
    # "base" é um bom ponto de partida para equilíbrio entre velocidade e precisão.
    # "medium" ou "large" oferecem melhor precisão mas são mais lentos e exigem mais recursos.
    transcricao_final_whisper = transcrever_audio_whisper(caminho_do_seu_audio, modelo_whisper="base")
    print(f"\n--- Transcrição Completa com Whisper ---")
    print(transcricao_final_whisper)