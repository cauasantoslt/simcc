# Participants: 568265 - Roberto Almeida Alvares, 567851 - Fabio Baldo, 566599 - Cauã Santos, 566598 - Amanda Damasceno Martins, 567169- Giovanna Gomes Oliveira

import os
import oracledb
# Importa as configurações do nosso novo arquivo seguro
try:
    import config
except ImportError:
    print("❌ ERRO: Arquivo de configuração 'config.py' não encontrado.")
    print("Crie o arquivo com suas credenciais DB_USER, DB_PASSWORD e DB_DSN.")
    exit()

def conectar_bd():
    try:
        # Usa as credenciais importadas do arquivo config.py
        return oracledb.connect(user=config.DB_USER, password=config.DB_PASSWORD, dsn=config.DB_DSN)
    except oracledb.DatabaseError as e:
        print(f"❌ Erro fatal de conexão com o Oracle: {e}")
        print("Verifique suas credenciais no arquivo config.py e se o banco está acessível.")
        return None

def calcular_perda(area_total, volume_colhido):
    if area_total <= 0:
        return 0
    produtividade_real = volume_colhido / area_total
    produtividade_referencia = 100
    perda = 1 - (produtividade_real / produtividade_referencia)
    return max(0, round(perda, 3))

def avaliar_eficiencia(perda):
    if perda < 0.05:
        return "Alta eficiência"
    elif perda < 0.10:
        return "Eficiência média"
    else:
        return "Baixa eficiência"

def obter_dados_colheita():
    produtor = input("Nome do produtor: ")
    while True:
        try:
            area = float(input("Área colhida (ha): ").replace(',', '.'))
            if area > 0:
                break
            print("❌ A área deve ser um número positivo.")
        except ValueError:
            print("❌ Valor inválido. Por favor, insira um número para a área.")
    
    while True:
        try:
            volume = float(input("Volume colhido (t): ").replace(',', '.'))
            if volume >= 0:
                break
            print("❌ O volume não pode ser um número negativo.")
        except ValueError:
            print("❌ Valor inválido. Por favor, insira um número para o volume.")
            
    return produtor, area, volume

def create_registro(registro):
    conn = conectar_bd()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO colheita_cana (produtor, area, volume, perda, eficiencia)
            VALUES (:1, :2, :3, :4, :5)
        """, [registro["produtor"], registro["area"], registro["volume"], registro["perda"], registro["eficiencia"]])
        conn.commit()
        print("\n✅ Registro inserido no Oracle com sucesso!")
    except oracledb.DatabaseError as e:
        print(f"❌ Erro ao inserir no Oracle: {e}")
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if conn: conn.close()

def read_registros():
    conn = conectar_bd()
    if not conn: return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT produtor, area, volume, perda*100, eficiencia, data_registro FROM colheita_cana ORDER BY data_registro DESC")
        
        print("\n--- 📋 Registros de Colheita no Banco de Dados ---")
        registros = cursor.fetchall()
        if not registros:
            print("Nenhum registro encontrado.")
        else:
            print(f"{'Produtor':<20} | {'Área (ha)':<10} | {'Volume (t)':<12} | {'Perda (%)':<10} | {'Eficiência':<15} | {'Data'}")
            print("-" * 90)
            for row in registros:
                print(f"{row[0]:<20} | {row[1]:<10.2f} | {row[2]:<12.2f} | {row[3]:<10.2f} | {row[4]:<15} | {row[5].strftime('%d/%m/%Y')}")
        print("---------------------------------------------------")
    except oracledb.DatabaseError as e:
        print(f"❌ Erro ao consultar o Oracle: {e}")
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if conn: conn.close()

def update_registro():
    produtor = input("Digite o nome do produtor que deseja atualizar: ")
    
    while True:
        try:
            novo_volume = float(input(f"Digite o novo volume colhido (t) para {produtor}: ").replace(',', '.'))
            if novo_volume >= 0: break
            print("❌ O volume não pode ser negativo.")
        except ValueError:
            print("❌ Valor inválido. Insira um número.")
    
    conn = conectar_bd()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE colheita_cana SET volume = :1 WHERE produtor = :2", [novo_volume, produtor])
        conn.commit()
        if cursor.rowcount > 0:
            print(f"\n✅ Registro do produtor '{produtor}' atualizado com sucesso.")
        else:
            print(f"\n⚠️ Nenhum registro encontrado para o produtor '{produtor}'. Nenhuma alteração foi feita.")
    except oracledb.DatabaseError as e:
        print(f"❌ Erro ao atualizar no Oracle: {e}")
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if conn: conn.close()

def delete_registro():
    produtor = input("Digite o nome do produtor que deseja deletar: ")
    
    confirmacao = input(f"Tem certeza que deseja deletar TODOS os registros de '{produtor}'? (s/n): ").lower()
    if confirmacao != 's':
        print("Operação cancelada.")
        return

    conn = conectar_bd()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM colheita_cana WHERE produtor = :1", [produtor])
        conn.commit()
        if cursor.rowcount > 0:
            print(f"\n✅ Registros do produtor '{produtor}' deletados com sucesso.")
        else:
            print(f"\n⚠️ Nenhum registro encontrado para o produtor '{produtor}'.")
    except oracledb.DatabaseError as e:
        print(f"❌ Erro ao deletar no Oracle: {e}")
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if conn: conn.close()

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_menu():
    print("\n--- 🌾 SIMCC – Sistema de Monitoramento da Colheita de Cana 🌾 ---")
    print("1. Adicionar novo registro de colheita")
    print("2. Ver todos os registros")
    print("3. Atualizar registro de um produtor")
    print("4. Deletar registro de um produtor")
    print("5. Sair")
    return input("Escolha uma opção: ")

def main():
    while True:
        opcao = exibir_menu()
        limpar_tela()
        
        if opcao == '1':
            print("--- Adicionar Novo Registro ---")
            produtor, area, volume = obter_dados_colheita()
            perda = calcular_perda(area, volume)
            eficiencia = avaliar_eficiencia(perda)
            
            registro = {
                "produtor": produtor, "area": area, "volume": volume,
                "perda": perda, "eficiencia": eficiencia
            }
            create_registro(registro)

        elif opcao == '2':
            read_registros()
            
        elif opcao == '3':
            print("--- Atualizar Registro ---")
            update_registro()

        elif opcao == '4':
            print("--- Deletar Registro ---")
            delete_registro()
            
        elif opcao == '5':
            print("Obrigado por usar o SIMCC. Até logo! 👋")
            break
        
        else:
            print("❌ Opção inválida. Por favor, tente novamente.")
        
        input("\nPressione Enter para continuar...")
        limpar_tela()

if __name__ == "__main__":
    main()