import os
from datetime import datetime
import json
import requests    

arquivo = "tarefas.json"
api_url = "https://raw.githubusercontent.com/sndyduarte/jsonapi/refs/heads/main/tarefas.json"

def menu():
    print("----  Menu de Tarefas  ----")
    print("1. Listar tarefas")
    print("2. Adicionar tarefa")
    print("3. Alterar status da tarefa")
    print("4. Carregar tarefas da API")
    print("5. Remover tarefa")
    print("6. Sair")

def carregar_tarefas():
    if not os.path.exists(arquivo):
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
   
    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)
def salvar_tarefas(tarefas):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)

def carregar_api(url):
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        tarefas_api = resposta.json()

        # Carrega tarefas locais
        tarefas_local = carregar_tarefas()

        # Conjunto com (nome, prazo) para detectar duplicatas
        tarefas_existentes = {(t["tarefa"], t["prazo"]) for t in tarefas_local}

        # IDs já usados
        ids_existentes = {t["id"] for t in tarefas_local}
        proximo_id = max(ids_existentes, default=0) + 1

        novas_tarefas = []

        for tarefa in tarefas_api:
            nome = tarefa.get("tarefa")
            prazo = tarefa.get("prazo")
            status = tarefa.get("status", "pendente")

            # Verifica duplicidade por nome e prazo
            if (nome, prazo) in tarefas_existentes:
                print(f"⚠️ Tarefa duplicada ignorada: {nome} - {prazo}")
                continue

            # Garante ID único
            if "id" not in tarefa or tarefa["id"] in ids_existentes:
                tarefa["id"] = proximo_id
                proximo_id += 1

            # Garante que tenha status válido
            if status not in ["pendente", "em andamento", "concluido"]:
                tarefa["status"] = "pendente"

            tarefas_existentes.add((nome, prazo))
            tarefas_local.append(tarefa)
            novas_tarefas.append(tarefa)

        salvar_tarefas(tarefas_local)

        print(f"🌐 {len(novas_tarefas)} novas tarefas importadas da API!")

    except requests.RequestException as e:
        print(f"❌ Erro ao acessar a API: {e}")
    except ValueError:
        print("❌ Resposta da API não está em formato JSON válido.")

while True:
    menu()
    opcao = input("\nEscolha uma opção: ")

    tarefas = carregar_tarefas()

    if opcao == "1":
        if not tarefas:
            print("\n🚫 Nenhuma tarefa cadastrada.")
        else:
            print("\n✅ Tarefas:")
        
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
                    break  # sai do for sem salvar

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
