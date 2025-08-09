import whisper
import os
from tqdm import tqdm
from pydub import AudioSegment # Necessário para segmentar o áudio

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
                               (Padrão: 15 segundos). Ajuste para otimizar desempenho vs. granularidade da barra.

    Returns:
        str: O texto transcrito do áudio ou uma mensagem de erro.
    """
    if not os.path.exists(caminho_audio):
        return f"❌ Erro: O arquivo de áudio '{caminho_audio}' não foi encontrado. Por favor, verifique o caminho."

    os.makedirs(output_dir, exist_ok=True)

    try:
        print(f"\n--- Iniciando Transcrição ---")
        print(f"Usando o modelo Whisper: '{modelo_whisper}'")
        print(f"Arquivo de áudio selecionado: '{caminho_audio}'")
        print(f"Carregando modelo Whisper '{modelo_whisper}'... (Isso pode demorar um pouco na primeira vez)")
        
        model = whisper.load_model(modelo_whisper)
        print("Modelo carregado com sucesso.")

        print(f"Preparando áudio para transcrição segmentada (chunks de {chunk_length_ms / 1000:.0f}s)...")
        audio = AudioSegment.from_file(caminho_audio)
        audio_length_ms = len(audio)

        # Divide o áudio em chunks
        chunks = []
        for i in range(0, audio_length_ms, chunk_length_ms):
            chunks.append(audio[i:i + chunk_length_ms])

        full_transcription = []
        
        # Barra de progresso para a transcrição real dos chunks
        print("Iniciando transcrição do áudio...")
        with tqdm(total=len(chunks), desc="Transcrevendo", unit="chunk", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}") as pbar:
            for i, chunk in enumerate(chunks):
                # Transcreve cada chunk
                # Nota: Salvar chunks temporariamente pode ser necessário para arquivos muito grandes
                # ou para evitar problemas de memória, mas pydub geralmente lida bem com isso.
                
                # Podemos otimizar não salvando no disco cada chunk, mas passando o BytesIO
                # No entanto, para simplicidade e robustez com Whisper, carregar do disco é seguro.
                temp_chunk_path = f"temp_chunk_{i}.wav"
                chunk.export(temp_chunk_path, format="wav")

                # Define o suppress_tokens para evitar que o Whisper transcreva silêncio ou música.
                # 'no_speech' é útil para pular partes sem fala.
                # 'fp16=False' é recomendado para garantir compatibilidade e evitar erros em CPUs ou GPUs sem suporte a FP16.
                result = model.transcribe(temp_chunk_path, language="pt", fp16=False, suppress_tokens=[-1])
                full_transcription.append(result["text"])
                os.remove(temp_chunk_path) # Remove o arquivo temporário

                pbar.update(1) # Atualiza a barra de progresso

        texto_transcrito = " ".join(full_transcription).strip() # Junta todas as transcrições dos chunks
        print(f"\n--- Transcrição Concluída ---")
        print(f"Transcrição: {texto_transcrito}")

        # Salva o texto em um arquivo
        nome_arquivo_base = os.path.splitext(os.path.basename(caminho_audio))[0]
        caminho_arquivo_saida = os.path.join(output_dir, f"{nome_arquivo_base}_transcricao.txt")
        
        with open(caminho_arquivo_saida, "w", encoding="utf-8") as f:
            f.write(texto_transcrito)
        print(f"💾 Transcrição salva em: '{caminho_arquivo_saida}'")

        return texto_transcrito
        
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado durante a transcrição com Whisper: {e}")
        print("   Por favor, verifique se o FFmpeg está instalado corretamente e acessível no seu PATH.")
        print("   Você pode baixar o FFmpeg em: https://ffmpeg.org/download.html")
        print("   Verifique também se o modelo Whisper ('base', 'small', etc.) foi baixado com sucesso.")
        return f"Erro na transcrição: {e}"

# O bloco __main__ permanece o mesmo
if __name__ == "__main__":
    print("Bem-vindo ao Transcritor de Áudio com Whisper!")
    print("Este programa transcreve áudio para texto e salva o resultado em um arquivo.")
    
    caminho_do_audio_input = ""
    while True:
        caminho_do_audio_input = input("👉 Por favor, digite o caminho completo do arquivo de áudio (ex: C:\\audios\\meu_audio.mp3): ").strip()
        if os.path.exists(caminho_do_audio_input):
            break
        else:
            print("❗ Arquivo não encontrado. Por favor, verifique o caminho e tente novamente.")
    
    modelos_disponiveis = ["tiny", "base", "small", "medium", "large"]
    modelo_padrao = "base"
    
    while True:
        modelo_escolhido_input = input(
            f"Escolha um modelo Whisper ({', '.join(modelos_disponiveis)}). "
            f"Padrão é '{modelo_padrao}'. (Pressione Enter para usar o padrão): "
        ).strip().lower()

        if not modelo_escolhido_input:
            modelo_a_usar = modelo_padrao
            break
        elif modelo_escolhido_input in modelos_disponiveis:
            modelo_a_usar = modelo_escolhido_input
            break
        else:
            print(f"❗ Modelo inválido. Por favor, escolha um dos seguintes: {', '.join(modelos_disponiveis)}")

    diretorio_saida_transcricao = input(f"📁 Digite o nome do diretório para salvar as transcrições (Padrão: 'transcricoes'): ").strip()
    if not diretorio_saida_transcricao:
        diretorio_saida_transcricao = "transcricoes"

    # Chama a função de transcrição com as entradas do usuário
    transcricao_final = transcrever_audio_whisper(
        caminho_do_audio_input, 
        modelo_whisper=modelo_a_usar,
        output_dir=diretorio_saida_transcricao
    )
    
    print("\n--- Processo de Transcrição Concluído ---")
    print("👋 Obrigado por usar o Transcritor de Áudio!")