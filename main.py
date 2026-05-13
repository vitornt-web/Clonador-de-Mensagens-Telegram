import asyncio
import os
import re
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    FloodWaitError
)
from telethon.tl.functions.messages import GetForumTopicsRequest
from telethon.tl.functions.channels import CreateChannelRequest

SESSION_FOLDER = "sessions"


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


async def gerenciar_pausa(count):

    if count > 0 and count % 1000 == 0:

        print(f"\n\nLimite de 1.000 mensagens atingido!")

        for i in range(300, 0, -1):

            minutos = i // 60
            segundos = i % 60

            print(
                f" standby: Retornando em "
                f"{minutos:02d}:{segundos:02d}...",
                end='\r'
            )

            await asyncio.sleep(1)

        print("\nRetomando o trabalho...\n")


####################################################
# CONTAS
####################################################

async def listar_sessoes():

    if not os.path.exists(SESSION_FOLDER):
        os.makedirs(SESSION_FOLDER)

    arquivos = [
        f.replace(".session", "")
        for f in os.listdir(SESSION_FOLDER)
        if f.endswith(".session")
    ]

    return arquivos


async def criar_nova_conta():

    limpar_tela()

    print("""
=====================================
         NOVA CONTA TELEGRAM
=====================================
""")

    nome = input("\nNome da conta/sessão: ").strip()

    api_id = input("API ID: ").strip()
    api_hash = input("API HASH: ").strip()

    client = TelegramClient(
        os.path.join(SESSION_FOLDER, nome),
        int(api_id),
        api_hash
    )

    await client.connect()

    if not await client.is_user_authorized():

        phone = input("Telefone (+55...): ")

        try:

            await client.send_code_request(phone)

            await client.sign_in(
                phone,
                input("Código recebido: ")
            )

        except SessionPasswordNeededError:

            pwd = input("Senha 2FA: ")

            await client.sign_in(password=pwd)

    print("\nConta adicionada com sucesso!")

    input("\nENTER para continuar...")

    return client


async def selecionar_conta():

    while True:

        limpar_tela()

        sessoes = await listar_sessoes()

        print("""
╔══════════════════════════════════════╗
║         CONTAS TELEGRAM             ║
╠══════════════════════════════════════╣
""")

        if sessoes:

            for i, s in enumerate(sessoes, 1):

                print(f"║ {i:2d}. {s:<33} ║")

        else:

            print("║ Nenhuma conta encontrada.           ║")

        print("╠══════════════════════════════════════╣")
        print("║ 0. Adicionar nova conta             ║")
        print("╚══════════════════════════════════════╝")

        escolha = input("\nEscolha: ").strip()

        # ADICIONAR CONTA
        if escolha == "0":

            client = await criar_nova_conta()

            return client

        # USAR CONTA EXISTENTE
        try:

            indice = int(escolha) - 1

            session_name = sessoes[indice]

            api_id = input("\nAPI ID da conta: ").strip()
            api_hash = input("API HASH da conta: ").strip()

            client = TelegramClient(
                os.path.join(SESSION_FOLDER, session_name),
                int(api_id),
                api_hash
            )

            await client.connect()

            if not await client.is_user_authorized():

                print("\nSessão inválida.")
                input("ENTER...")
                continue

            print(f"\nEntrando na conta: {session_name}")

            await asyncio.sleep(1)

            return client

        except Exception as e:

            print(f"\nErro: {e}")
            input("ENTER...")


####################################################
# LISTAR TÓPICOS
####################################################

async def listar_topicos_grupo(client, grupo_entidade):

    print("\nBuscando tópicos do fórum...")

    try:

        result = await client(GetForumTopicsRequest(
            grupo_entidade,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=150
        ))

        topicos = []

        if hasattr(result, 'topics'):

            for t in result.topics:

                titulo = getattr(t, 'title', f"Tópico {t.id}")

                topicos.append((t.id, titulo))

        if not topicos:

            print("Nenhum tópico encontrado.")
            return None

        for i, (t_id, titulo) in enumerate(topicos, 1):

            print(f"{i:2d}. {titulo} (ID: {t_id})")

        escolha = int(
            input(f"\nEscolha o tópico (1-{len(topicos)}): ")
        )

        return topicos[escolha - 1][0]

    except Exception as e:

        print(f"Erro ao buscar tópicos: {e}")
        return None


####################################################
# SELECIONAR ENTIDADE
####################################################

async def selecionar_entidade(client, tipo_msg):

    print(f"\n--- SELECIONE {tipo_msg} ---")

    dialogs = []

    print("Carregando chats recentes...")

    async for d in client.iter_dialogs(limit=50):

        if d.is_channel or d.is_group:
            dialogs.append(d)

    for i, d in enumerate(dialogs, 1):

        tipo = "Canal" if d.is_channel else "Grupo"

        print(
            f"{i:2d}. "
            f"{d.name[:35]:<35} | "
            f"{tipo}"
        )

    try:

        op = input(
            "\nEscolha número "
            "ou digite 0 para ID manual: "
        ).strip()

        if op == "0":

            manual_id = int(
                input("Digite o ID (ex: -100...): ")
            )

            entidade = await client.get_input_entity(manual_id)

        else:

            indice = int(op) - 1

            entidade = dialogs[indice].entity

        return entidade

    except Exception as e:

        print(f"Erro na seleção: {e}")
        return None


####################################################
# LISTAR CANAIS PROTEGIDOS
####################################################

async def listar_canais_protegidos(client):

    protegidos = []

    print("\nBuscando canais protegidos...\n")

    async for d in client.iter_dialogs(limit=100):

        try:

            entidade = d.entity

            if getattr(entidade, "noforwards", False):

                protegidos.append(d)

        except:
            pass

    if not protegidos:

        print("Nenhum canal protegido encontrado.")
        return None

    for i, d in enumerate(protegidos, 1):

        print(f"{i:2d}. {d.name}")

    escolha = int(input("\nEscolha o canal: "))

    return protegidos[escolha - 1].entity


####################################################
# CRIAR CANAL BACKUP
####################################################

async def criar_canal_backup(client, nome_original):

    novo_nome = f"{nome_original} (BACKUP)"

    print(f"\nCriando canal: {novo_nome}")

    resultado = await client(CreateChannelRequest(
        title=novo_nome,
        about="Backup automático",
        megagroup=False
    ))

    canal = resultado.chats[0]

    return canal


####################################################
# CLONAGEM NORMAL
####################################################

async def clonar_processo(
    client,
    origem,
    destino,
    topico_origem=None,
    topico_destino=None
):

    count = 0
    erros = 0

    params = {
        'entity': origem,
        'reverse': True
    }

    if topico_origem:
        params['reply_to'] = topico_origem

    print(f"\nIniciando clonagem...")

    async for msg in client.iter_messages(**params):

        if msg.action:
            continue

        try:

            await gerenciar_pausa(count)

            if topico_destino:

                await client.send_message(
                    destino,
                    msg,
                    comment_to=topico_destino
                )

            else:

                await client.send_message(
                    destino,
                    msg
                )

            count += 1

            if count % 5 == 0:

                print(
                    f"{count} mensagens enviadas...",
                    end='\r'
                )

            await asyncio.sleep(1.1)

        except FloodWaitError as e:

            print(
                f"\nFlood detectado! "
                f"Aguardando {e.seconds} segundos..."
            )

            await asyncio.sleep(e.seconds)

        except Exception as e:

            erros += 1

            print(
                f"\nErro ao copiar "
                f"mensagem {msg.id}: {e}"
            )

            if erros > 40:
                break

    print(
        f"\n\nFinalizado! "
        f"Total: {count} | Erros: {erros}"
    )


####################################################
# CLONAGEM PROTEGIDA
####################################################

async def clonar_conteudo_protegido(client):

    origem = await listar_canais_protegidos(client)

    if not origem:
        return

    entidade = await client.get_entity(origem)

    canal_backup = await criar_canal_backup(
        client,
        entidade.title
    )

    print(
        f"\nCanal backup criado: "
        f"{canal_backup.title}"
    )

    count = 0

    async for msg in client.iter_messages(
        origem,
        reverse=True
    ):

        if msg.action:
            continue

        try:

            texto = msg.text or ""

            arquivo = None

            if msg.media:

                print(
                    f"Baixando mídia "
                    f"({msg.id})..."
                )

                arquivo = await msg.download_media()

            await client.send_message(
                canal_backup,
                texto,
                file=arquivo
            )

            if arquivo and os.path.exists(arquivo):
                os.remove(arquivo)

            count += 1

            if count % 5 == 0:

                print(
                    f"{count} mensagens copiadas...",
                    end="\r"
                )

            await asyncio.sleep(1.3)

        except FloodWaitError as e:

            print(
                f"\nFlood detectado "
                f"({e.seconds}s)"
            )

            await asyncio.sleep(e.seconds)

        except Exception as e:

            print(f"\nErro: {e}")

    print(
        f"\n\nBackup finalizado! "
        f"{count} mensagens copiadas."
    )


####################################################
# MENU PRINCIPAL
####################################################

async def menu_principal():

    client = await selecionar_conta()

    while True:

        limpar_tela()

        print(f"""
╔══════════════════════════════════════╗
║ 𓅂 CLONADOR DE CONTEÚDO TELEGRAM 𓅂  ║
║           BY: OLIVEIRA               ║
║       † VIVA CRISTO REI! †           ║
╠══════════════════════════════════════╣
║ 1. Canal → Canal                     ║
║ 2. Canal → Tópico                    ║
║ 3. Tópico → Canal                    ║
║ 4. Tópico → Tópico                   ║
║ 5. Clonagem Protegida                ║
║ 6. Trocar Conta                      ║
║ 7. Sair                              ║
╚══════════════════════════════════════╝
""")

        opcao = input("Opção: ")

        if opcao == "1":

            origem = await selecionar_entidade(
                client,
                "CANAL ORIGEM"
            )

            destino = await selecionar_entidade(
                client,
                "CANAL DESTINO"
            )

            await clonar_processo(
                client,
                origem,
                destino
            )

        elif opcao == "2":

            origem = await selecionar_entidade(
                client,
                "CANAL ORIGEM"
            )

            destino = await selecionar_entidade(
                client,
                "GRUPO DESTINO"
            )

            topico_destino = await listar_topicos_grupo(
                client,
                destino
            )

            await clonar_processo(
                client,
                origem,
                destino,
                None,
                topico_destino
            )

        elif opcao == "3":

            origem = await selecionar_entidade(
                client,
                "GRUPO ORIGEM"
            )

            topico_origem = await listar_topicos_grupo(
                client,
                origem
            )

            destino = await selecionar_entidade(
                client,
                "CANAL DESTINO"
            )

            await clonar_processo(
                client,
                origem,
                destino,
                topico_origem,
                None
            )

        elif opcao == "4":

            origem = await selecionar_entidade(
                client,
                "GRUPO ORIGEM"
            )

            topico_origem = await listar_topicos_grupo(
                client,
                origem
            )

            destino = await selecionar_entidade(
                client,
                "GRUPO DESTINO"
            )

            topico_destino = await listar_topicos_grupo(
                client,
                destino
            )

            await clonar_processo(
                client,
                origem,
                destino,
                topico_origem,
                topico_destino
            )

        elif opcao == "5":

            await clonar_conteudo_protegido(client)

        elif opcao == "6":

            await client.disconnect()

            client = await selecionar_conta()

        elif opcao == "7":

            await client.disconnect()

            print("Saindo...")

            break

        input("\nPressione ENTER para voltar ao menu...")


if __name__ == "__main__":

    try:
        asyncio.run(menu_principal())

    except KeyboardInterrupt:

        print("\nSaindo com segurança...")