# Importa bibliotecas necessárias
import os  # Manipulação de arquivos e diretórios
from datetime import datetime  # Manipulação de datas
import json  # Leitura e escrita de arquivos JSON
import requests  # Requisições HTTP para carregar dados externos
import unicodedata  # Para remover acentos de strings

# Define o nome do arquivo local para armazenar tarefas
arquivo = "tarefas.json"

# URL do arquivo de tarefas hospedado no GitHub (atuando como uma API)
api_url = "https://raw.githubusercontent.com/sndyduarte/jsonapi/refs/heads/main/tarefas.json"

# Função auxiliar para normalizar texto (remove acentos, ignora maiúsculas/minúsculas)
def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8").lower()

# Função que exibe o menu principal com as opções
def menu():
    print("----  Menu de Tarefas  ----")
    print("1. Listar tarefas")
    print("2. Adicionar tarefa")
    print("3. Alterar status da tarefa")
    print("4. Carregar tarefas da API")
    print("5. Remover tarefa")
    print("6. Sair")

# Carrega tarefas do arquivo local ou cria um novo arquivo vazio se não existir
def carregar_tarefas():
    if not os.path.exists(arquivo):
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)  # Cria arquivo com lista vazia

    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)  # Retorna lista de tarefas carregada

# Salva a lista de tarefas no arquivo JSON
def salvar_tarefas(tarefas):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)

# Carrega tarefas da API (arquivo remoto) e adiciona à lista local, evitando duplicatas
def carregar_api(url):
    try:
        resposta = requests.get(url)  # Faz a requisição HTTP
        resposta.raise_for_status()  # Lança erro se status != 200
        tarefas_api = resposta.json()  # Converte resposta em lista de tarefas

        tarefas_local = carregar_tarefas()  # Tarefas locais atuais

        # Detecta duplicatas com base em (tarefa, prazo), ignorando maiúsculas/minúsculas e acentos
        tarefas_existentes = {
            (normalizar(t["tarefa"]), t["prazo"]) for t in tarefas_local
        }

        # Coleta IDs existentes
        ids_existentes = {t["id"] for t in tarefas_local}
        proximo_id = max(ids_existentes, default=0) + 1  # Define novo ID

        novas_tarefas = []  # Lista para armazenar tarefas novas

        for tarefa in tarefas_api:
            nome = tarefa.get("tarefa")
            prazo = tarefa.get("prazo")
            status = tarefa.get("status", "pendente")

            if (normalizar(nome), prazo) in tarefas_existentes:
                print(f"⚠️ Tarefa duplicada ignorada: {nome} - {prazo}")
                continue

            if "id" not in tarefa or tarefa["id"] in ids_existentes:
                tarefa["id"] = proximo_id
                proximo_id += 1

            if status not in ["pendente", "em andamento", "concluido"]:
                tarefa["status"] = "pendente"

            tarefas_existentes.add((normalizar(nome), prazo))
            tarefas_local.append(tarefa)
            novas_tarefas.append(tarefa)

        salvar_tarefas(tarefas_local)

        print(f"🌐 {len(novas_tarefas)} novas tarefas importadas da API!")

    except requests.RequestException as e:
        print(f"❌ Erro ao acessar a API: {e}")
    except ValueError:
        print("❌ Resposta da API não está em formato JSON válido.")

# Loop principal do programa
while True:
    menu()
    opcao = input("\nEscolha uma opção: ")
    tarefas = carregar_tarefas()

    if opcao == "1":
        if not tarefas:
            print("\n🚫 Nenhuma tarefa cadastrada.")
        else:
            print("\nTarefas:")

        status_emojis = {
            "pendente": "⏳",
            "em andamento": "🛠️",
            "concluido": "✅"
        }

        for t in tarefas:
            status = status_emojis.get(t["status"], "❓")
            print(f'[{t["id"]}] {t["tarefa"]} - {t["prazo"]} - {status}')

    elif opcao == "2":
        nome = input("📝 Nome da tarefa: ")
        prazo = input("📅 Prazo (DD/MM/AAAA): ")

        try:
            datetime.strptime(prazo, "%d/%m/%Y")
        except ValueError:
            print("❌ Data inválida!")
            continue

        if any(normalizar(t["tarefa"]) == normalizar(nome) and t["prazo"] == prazo for t in tarefas):
            print("⚠️ Tarefa com mesmo nome e prazo já existente! Informe uma tarefa nova.")
            continue

        print("\n🔄 Escolha o status inicial da tarefa:")
        print("1. Pendente")
        print("2. Em andamento")
        print("3. Concluído")
        escolha_status = input("Digite o número da opção: ")

        if escolha_status == "1":
            status = "pendente"
        elif escolha_status == "2":
            status = "em andamento"
        elif escolha_status == "3":
            status = "concluido"
        else:
            print("❌ Opção inválida para status.")
            continue

        novo_id = max([t["id"] for t in tarefas], default=0) + 1

        nova = {
            "id": novo_id,
            "tarefa": nome,
            "prazo": prazo,
            "status": status
        }

        tarefas.append(nova)
        salvar_tarefas(tarefas)
        print("✅ Tarefa adicionada!")

    elif opcao == "3":
        id_alterar = int(input("🆔 ID da tarefa para alterar o status: "))
        encontrou = False

        for t in tarefas:
            if t["id"] == id_alterar:
                print("\n🔄 Escolha o novo status:")
                print("1. Pendente")
                print("2. Em andamento")
                print("3. Concluído")
                escolha_status = input("Digite o número da opção: ")

                if escolha_status == "1":
                    t["status"] = "pendente"
                elif escolha_status == "2":
                    t["status"] = "em andamento"
                elif escolha_status == "3":
                    t["status"] = "concluido"
                else:
                    print("❌ Opção inválida.")
                    break

                encontrou = True
                break

        if encontrou:
            salvar_tarefas(tarefas)
            print("✅ Status da tarefa atualizado!")
        else:
            print("❌ ID não encontrado.")

    elif opcao == "4":
        carregar_api(api_url)
        tarefas = carregar_tarefas()

    elif opcao == "5":
        id_remover = int(input("🗑️ ID da tarefa a remover: "))
        tarefas_novas = [t for t in tarefas if t["id"] != id_remover]

        if len(tarefas_novas) == len(tarefas):
            print("❌ ID não encontrado.")
        else:
            salvar_tarefas(tarefas_novas)
            print("🗑️ Tarefa removida com sucesso!")

    elif opcao == "6":
        print("👋 Até a próxima!")
        break

    else:
        print("❌ Opção inválida.")
