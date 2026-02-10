import asyncio
import os
import re
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.functions.messages import GetForumTopicsRequest

SESSION_FILE = "telegram_session"

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

async def gerenciar_pausa(count):
    if count > 0 and count % 1000 == 0:
        print(f"\n\n⏳ Limite de 1.000 mensagens atingido!")
        for i in range(300, 0, -1):
            minutos = i // 60
            segundos = i % 60
            print(f" standby: Retornando em {minutos:02d}:{segundos:02d}...", end='\r')
            await asyncio.sleep(1)
        print("\n🚀 Retomando o trabalho...\n")

async def get_credentials():
    if not os.path.exists(".env"):
        print("⚙️ PRIMEIRA CONFIGURAÇÃO!")
        api_id = input("API ID (número): ").strip()
        api_hash = input("API HASH (código): ").strip()
        with open(".env", "w") as f:
            f.write(f"{api_id}\n{api_hash}\n")
    
    with open(".env", "r") as f:
        linhas = f.readlines()
        if len(linhas) < 2:
            os.remove(".env")
            return await get_credentials()
        return int(linhas[0].strip()), linhas[1].strip()

async def connect_client():
    api_id, api_hash = await get_credentials()
    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        phone = input("Telefone (ex: +5511999999999): ")
        try:
            await client.send_code_request(phone)
            await client.sign_in(phone, input("Código recebido no Telegram: "))
        except SessionPasswordNeededError:
            pwd = input("Senha de 2 etapas (2FA) necessária: ")
            await client.sign_in(password=pwd)
    return client

async def listar_topicos_grupo(client, grupo_entidade):
    print("\n🔍 Buscando tópicos do fórum...")
    try:
        result = await client(GetForumTopicsRequest(
            channel=grupo_entidade,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=50
        ))
        
        topicos = []
        for t in result.topics:
            titulo = getattr(t, 'title', f"Tópico {t.id}")
            topicos.append((t.id, titulo))
            
        if not topicos:
            print("❌ Nenhum tópico encontrado ou o grupo não possui fórum ativo.")
            return None

        for i, (t_id, titulo) in enumerate(topicos, 1):
            print(f"  {i:2d}. {titulo} (ID: {t_id})")
        
        escolha = int(input(f"\nEscolha o tópico (1-{len(topicos)}): "))
        return topicos[escolha-1][0]
    except Exception as e:
        print(f"❌ Erro ao buscar tópicos: {e}")
        return None

async def selecionar_entidade(client, tipo_msg):
    print(f"\n--- SELECIONE A {tipo_msg} DO GRUPO QUE VOCÊ QUER CLONAR ---")
    dialogs = []
    print("⏳ Carregando chats recentes...")
    
    async for d in client.iter_dialogs(limit=40):
        if d.is_channel or d.is_group:
            dialogs.append(d)
    
    for i, d in enumerate(dialogs, 1):
        tipo = "Canal" if d.is_channel else "Grupo"
        print(f"{i:2d}. {d.name[:30]:<30} | {tipo} | ID: {d.id}")
    
    try:
        op = input("\nEscolha o número do canal que deseja clonar ou digite o ID do grupo/canal manualmente digitando  Zero '0' (caso não saiba buscar o ID do canal basta ir na lupa" \
        " do telegram e procurar o bot: userinfobot): ").strip()
        if op == "0" or len(op) > 5:
            manual_id = int(op if op != "0" else input("Digite o ID (ex: -100...): "))
            return await client.get_input_entity(manual_id)
        
        indice = int(op) - 1
        return dialogs[indice].entity
    except Exception as e:
        print(f"❌ Erro na seleção: {e}")
        return None

async def clonar_processo(client, origem, destino, topico_id=None, limite=0):
    count = 0
    erros = 0
    
    params = {'entity': origem, 'reverse': True}
    if topico_id:
        params['reply_to'] = topico_id
    if limite > 0:
        params['limit'] = limite

    print(f"\n🚀 Iniciando clonagem... (Origem: {getattr(origem, 'title', 'ID: '+str(origem))})")
    
    async for msg in client.iter_messages(**params):
        if msg.action:
            continue
            
        try:
            await gerenciar_pausa(count)
        
            await client.send_message(destino, msg)
            
            count += 1
            if count % 5 == 0:
                print(f"✅ {count} mensagens enviadas...", end='\r')
            
            await asyncio.sleep(1.2)
            
        except FloodWaitError as e:
            print(f"\n⚠️ Flood detectado! Aguardando {e.seconds} segundos...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            erros += 1
            print(f"\n⚠️ Erro ao copiar mensagem {msg.id}: {e}")
            if erros > 40: 
                print("\n🔴 Excesso de erros. Verifique suas permissões no destino.")
                break 

    print(f"\n\n✅ Finalizado! Total: {count} | Erros: {erros}")

async def menu_principal():
    client = await connect_client()
    
    while True:
        limpar_tela()
        print(f"""
        ╔══════════════════════════════════════╗
        ║ 𓅂 CLONADOR DE CONTEÚDO TELEGRAM 𓅂  ║
        ║           BY: OLIVEIRA               ║
        ║       † VIVA CRISTO REI! †           ║
        ╠══════════════════════════════════════╣
        ║ 1. Clonar Canal/Grupo Inteiro        ║
        ║ 2. Clonar Tópico Específico (Fórum)  ║
        ║ 3. Limpar Sessão e Sair              ║
        ╚══════════════════════════════════════╝
        """)
        
        opcao = input("Opção: ")
        
        if opcao == "1":
            origem = await selecionar_entidade(client, "ORIGEM")
            destino = await selecionar_entidade(client, "DESTINO")
            if origem and destino:
                await clonar_processo(client, origem, destino)
            
        elif opcao == "2":
            origem = await selecionar_entidade(client, "GRUPO ORIGEM (FÓRUM)")
            if origem:
                topico_id = await listar_topicos_grupo(client, origem)
                if topico_id:
                    destino = await selecionar_entidade(client, "DESTINO")
                    if destino:
                        await clonar_processo(client, origem, destino, topico_id=topico_id)
        
        elif opcao == "3":
            await client.disconnect()
            print("Saindo...")
            break
            
        input("\nPressione ENTER para voltar ao menu...")

if __name__ == "__main__":
    try:
        asyncio.run(menu_principal())
    except KeyboardInterrupt:
        print("\nSaindo com segurança...")