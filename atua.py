import sqlite3

try:
    # Acessa o banco de dados na pasta instance (padrão do Flask)
    conn = sqlite3.connect('instance/atendimentos.db')
    cursor = conn.cursor()
    
    cursor.execute("ALTER TABLE atendimento ADD COLUMN status VARCHAR(20) DEFAULT 'Concluído'")
    cursor.execute("ALTER TABLE atendimento ADD COLUMN motivo_pendencia TEXT")
    cursor.execute("ALTER TABLE atendimento ADD COLUMN resposta_final TEXT")
    
    conn.commit()
    print("Banco de dados atualizado com sucesso!")
except Exception as e:
    print(f"Aviso (as colunas podem já existir): {e}")
finally:
    conn.close()