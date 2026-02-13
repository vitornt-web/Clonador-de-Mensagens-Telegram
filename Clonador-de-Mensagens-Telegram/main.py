import asyncio
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.functions.messages import GetForumTopicsRequest

SESSION_FILE = "telegram_session"


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


async def pausa_inteligente(count):
    if count > 0 and count % 800 == 0:
        print("\n⏳ Pausando 4 minutos para evitar FLOOD...\n")
        await asyncio.sleep(240)


async def get_credentials():
    if not os.path.exists(".env"):
        print("⚙️ PRIMEIRA CONFIGURAÇÃO")
        api_id = input("API ID: ")
        api_hash = input("API HASH: ")

        with open(".env", "w") as f:
            f.write(f"{api_id}\n{api_hash}")

    with open(".env") as f:
        api_id, api_hash = f.read().splitlines()

    return int(api_id), api_hash


async def connect_client():
    api_id, api_hash = await get_credentials()

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        phone = input("Telefone (+55...): ")

        try:
            await client.send_code_request(phone)
            await client.sign_in(phone, input("Código: "))
        except SessionPasswordNeededError:
            await client.sign_in(password=input("Senha 2FA: "))

    return client


async def listar_topicos_grupo(client, grupo):
    print("\n🔎 Buscando tópicos...")

    try:
        result = await client(GetForumTopicsRequest(
            grupo,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=200
        ))

        if not result.topics:
            print("❌ Este grupo não possui fórum ativo.")
            return None

        topicos = [(t.id, t.title) for t in result.topics]

        for i, (_, titulo) in enumerate(topicos, 1):
            print(f"{i:2d}. {titulo}")

        escolha = int(input("\nEscolha o tópico: "))
        return topicos[escolha - 1][0]

    except Exception as e:
        print("Erro ao listar tópicos:", e)
        return None


async def selecionar_entidade(client, texto):
    print(f"\n--- {texto} ---")
    dialogs = []

    async for d in client.iter_dialogs(limit=60):
        if d.is_channel or d.is_group:
            dialogs.append(d)

    for i, d in enumerate(dialogs, 1):

        if d.is_channel and not d.is_group:
            tipo = "📢 Canal"
        else:
            tipo = "👥 Grupo"

        print(f"{i:2d}. {d.name[:35]:<35} | {tipo}")

    op = input("\nEscolha número ou digite ID (0 manual): ")

    if op == "0" or len(op) > 4:
        manual = int(op if op != "0" else input("Digite o ID: "))
        return await client.get_input_entity(manual)

    return dialogs[int(op) - 1].entity


# ⭐ ENVIO ULTRA ESTÁVEL
async def enviar_mensagem(client, origem, destino, msg, topico_destino=None):

    if msg.action:
        return

    try:
        # tenta forward
        await client.forward_messages(
            destino,
            msg.id,
            from_peer=origem,
            reply_to=topico_destino if topico_destino else None
        )

    except Exception:

        # fallback copia
        try:
            await client.send_message(
                destino,
                msg.text or "",
                file=msg.media,
                reply_to=topico_destino if topico_destino else None
            )
        except Exception as e:
            print(f"⚠️ Erro ao enviar msg {msg.id}: {e}")


async def clonar(client, origem, destino, topico_origem=None, topico_destino=None):

    print("\n🚀 Iniciando clonagem...\n")

    params = {"entity": origem, "reverse": True}

    if topico_origem:
        params["reply_to"] = topico_origem

    count = 0

    async for msg in client.iter_messages(**params):

        try:
            await pausa_inteligente(count)

            await enviar_mensagem(
                client,
                origem,
                destino,
                msg,
                topico_destino
            )

            count += 1

            if count % 10 == 0:
                print(f"✅ {count} mensagens copiadas...", end="\r")

            await asyncio.sleep(0.9)

        except FloodWaitError as e:
            print(f"\n⚠️ Flood! Esperando {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            print("Erro geral:", e)

    print(f"\n\n✅ FINALIZADO — {count} mensagens copiadas.\n")


async def menu():
    client = await connect_client()

    while True:
        limpar_tela()

        print("""
╔══════════════════════════════════════╗
║        🚀 TELEGRAM CLONER PRO MAX    ║
╠══════════════════════════════════════╣
║ 1️⃣ Canal → Canal 🔥🔥🔥             ║
║ 2️⃣ Canal/Grupo → Chat normal        ║
║ 3️⃣ Tópico → Tópico (fórum)          ║
║ 4️⃣ Canal → Tópico (fórum)           ║
║ 5️⃣ Sair                            ║
╚══════════════════════════════════════╝
        """)

        op = input("Escolha: ")

        # 🔥 CANAL -> CANAL
        if op == "1":
            print("\n📢 Canal de ORIGEM")
            origem = await selecionar_entidade(client, "CANAL ORIGEM")

            print("\n📢 Canal de DESTINO")
            destino = await selecionar_entidade(client, "CANAL DESTINO")

            if origem and destino:
                await clonar(client, origem, destino)

        elif op == "2":
            origem = await selecionar_entidade(client, "ORIGEM")
            destino = await selecionar_entidade(client, "DESTINO")

            if origem and destino:
                await clonar(client, origem, destino)

        elif op == "3":
            origem = await selecionar_entidade(client, "GRUPO ORIGEM")
            topico_origem = await listar_topicos_grupo(client, origem)

            destino = await selecionar_entidade(client, "GRUPO DESTINO")
            topico_destino = await listar_topicos_grupo(client, destino)

            if topico_origem and topico_destino:
                await clonar(client, origem, destino, topico_origem, topico_destino)

        elif op == "4":
            origem = await selecionar_entidade(client, "CANAL ORIGEM")
            destino = await selecionar_entidade(client, "GRUPO DESTINO")

            topico_destino = await listar_topicos_grupo(client, destino)

            if origem and destino and topico_destino:
                await clonar(client, origem, destino, None, topico_destino)

        elif op == "5":
            await client.disconnect()
            break

        input("\nENTER para voltar...")


if __name__ == "__main__":
    asyncio.run(menu())