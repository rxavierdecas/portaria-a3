"""Dados de demonstração (pessoas do mockup + histórico de movimentações)."""

import random
from datetime import datetime, time, timedelta

from portaria.database.connection import Database
from portaria.repositories._datas import para_texto
from portaria.utils.validators import calcular_digitos_cpf

# (nome, 9 primeiros dígitos do CPF, telefone, empresa, tipo, motivo, entrada hoje, saída hoje)
_PESSOAS: tuple[tuple[str, str, str, str, str, str, time, time | None], ...] = (
    ("Maria Silva", "123456789", "31988887777", "ACME Ltda", "Visitante", "Reunião comercial", time(8, 15), None),
    ("João Pereira", "987654321", "31977776666", "UNA", "Funcionário", "Expediente", time(7, 50), time(12, 30)),
    ("Ana Costa", "111222333", "31966665555", "Clima Frio", "Prestador", "Manutenção do ar-condicionado", time(9, 20), None),
    ("Carlos Lima", "444555666", "31955554444", "Particular", "Visitante", "Entrevista de emprego", time(10, 5), time(11, 40)),
    ("Fernanda Alves", "888999000", "31944443333", "UNA", "Funcionário", "Expediente", time(7, 45), None),
)


def popular_dados_demo(db: Database, dias_historico: int = 10) -> bool:
    """Insere os dados de exemplo se ainda não houver pessoas. Retorna True se inseriu."""
    sorteio = random.Random(42)
    agora = datetime.now().replace(second=0, microsecond=0)
    hoje = agora.date()

    with db.connect() as conn:
        if conn.execute("SELECT COUNT(*) FROM pessoas").fetchone()[0] > 0:
            return False

        for nome, base_cpf, telefone, empresa, tipo, motivo, entrada_hoje, saida_hoje in _PESSOAS:
            cpf = base_cpf + calcular_digitos_cpf(base_cpf)
            criado_em = datetime.combine(hoje - timedelta(days=dias_historico), time(8, 0))
            cursor = conn.execute(
                """
                INSERT INTO pessoas (nome, cpf, telefone, empresa, tipo_acesso, motivo, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (nome, cpf, telefone, empresa, tipo, motivo, para_texto(criado_em)),
            )
            pessoa_id = cursor.lastrowid

            movimentos: list[tuple[datetime, datetime | None]] = []
            for dias_atras in range(dias_historico, 0, -1):
                dia = hoje - timedelta(days=dias_atras)
                frequente = tipo == "Funcionário"
                if dia.weekday() >= 5 or sorteio.random() > (0.9 if frequente else 0.35):
                    continue
                entrada = datetime.combine(dia, time(7 + sorteio.randint(0, 3), sorteio.choice((0, 15, 30, 45))))
                saida = entrada + timedelta(minutes=sorteio.randint(40, 540))
                movimentos.append((entrada, saida))

            entrada = datetime.combine(hoje, entrada_hoje)
            if entrada <= agora:
                saida = datetime.combine(hoje, saida_hoje) if saida_hoje else None
                movimentos.append((entrada, saida if saida and saida <= agora else None))

            conn.executemany(
                "INSERT INTO movimentacoes (pessoa_id, entrada, saida) VALUES (?, ?, ?)",
                [(pessoa_id, para_texto(e), para_texto(s)) for e, s in movimentos],
            )
    return True
