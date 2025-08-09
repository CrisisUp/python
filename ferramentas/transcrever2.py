import whisper
import os
from tqdm import tqdm # Importa a biblioteca tqdm para a barra de progresso

def transcrever_audio_whisper(caminho_audio, modelo_whisper="base", output_dir="transcricoes"):
    """
    Transcreve um arquivo de áudio para texto usando o modelo Whisper da OpenAI,
    exibindo uma barra de progresso e salvando o texto em um arquivo.

    Args:
        caminho_audio (str): O caminho completo para o arquivo de áudio.
        modelo_whisper (str): O nome do modelo Whisper a ser usado (ex: "tiny", "base", "small", "medium", "large").
                              Modelos maiores são mais precisos, mas exigem mais recursos e tempo.
        output_dir (str): Diretório onde o arquivo de texto transcrito será salvo.
                          Será criado se não existir.

    Returns:
        str: O texto transcrito do áudio ou uma mensagem de erro.
    """
    if not os.path.exists(caminho_audio):
        return f"❌ Erro: O arquivo de áudio '{caminho_audio}' não foi encontrado. Por favor, verifique o caminho."

    # Garante que o diretório de saída exista
    os.makedirs(output_dir, exist_ok=True)

    try:
        print(f"\n--- Iniciando Transcrição ---")
        print(f"Usando o modelo Whisper: '{modelo_whisper}'")
        print(f"Arquivo de áudio selecionado: '{caminho_audio}'")
        print(f"Carregando modelo Whisper '{modelo_whisper}'... (Isso pode demorar um pouco na primeira vez)")
        
        # Carrega o modelo. Ele será baixado se ainda não estiver presente.
        model = whisper.load_model(modelo_whisper)
        
        print("Modelo carregado com sucesso. Transcrevendo áudio...")
        
        # A transcrição do Whisper não tem um progresso nativo fácil de exibir como percentual.
        # No entanto, podemos simular um prograesso para o "carregamento do modelo"
        # e indicar que a transcrição em si está "processando".
        # Para um progresso real da transcrição, seria preciso segmentar o áudio
        # e transcrever por partes, o que aumenta a complexidade.
        # Por enquanto, vamos indicar que o processamento está em andamento.

        # Uma barra de progresso simples para "processamento"
        with tqdm(total=100, desc="Processando Áudio", unit="%", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}") as pbar:
            # Não é um progresso real, mas indica que algo está acontecendo
            # Para uma barra de progresso precisa, seria necessário integrar com a lógica interna do Whisper
            # ou dividir o áudio em chunks e processar um a um.
            # Aqui, apenas simulamos um carregamento e depois a transcrição
            
            # Simula um "carregamento" inicial
            for i in range(20):
                pbar.update(1)
                # Adicione um pequeno atraso se quiser ver a barra avançar lentamente
                # import time
                # time.sleep(0.01)

            # Executa a transcrição real (que é a parte mais demorada)
            result = model.transcribe(caminho_audio, language="pt", fp16=False) # fp16=False para evitar problemas com GPUs sem suporte a FP16 ou CPU
            
            # Completa a barra de progresso após a transcrição
            pbar.update(80) # Completa o restante da barra

        texto_transcrito = result["text"]
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
        print("   Certifique-se de que o FFmpeg está instalado e acessível no seu PATH.")
        print("   Para instalar o FFmpeg, visite: https://ffmpeg.org/download.html")
        return f"Erro na transcrição: {e}"

if __name__ == "__main__":
    print("Bem-vindo ao Transcritor de Áudio com Whisper!")
    print("Este programa transcreve áudio para texto e salva o resultado em um arquivo.")
    
    # Pergunta ao usuário o caminho do arquivo de áudio
    caminho_do_audio_input = ""
    while True:
        caminho_do_audio_input = input("👉 Por favor, digite o caminho completo do arquivo de áudio (ex: C:\\audios\\meu_audio.mp3): ").strip()
        if os.path.exists(caminho_do_audio_input):
            break
        else:
            print("❗ Arquivo não encontrado. Por favor, verifique o caminho e tente novamente.")
    
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
            print(f"❗ Modelo inválido. Por favor, escolha um dos seguintes: {', '.join(modelos_disponiveis)}")

    # Opcional: define o diretório de saída para os arquivos de transcrição
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