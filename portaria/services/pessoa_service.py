from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from portaria import config
from portaria.exceptions import DuplicadoError, ValidacaoError
from portaria.models.pessoa import Pessoa
from portaria.repositories.pessoa_repository import PessoaRepository
from portaria.utils.validators import (
    campos_vazios,
    somente_digitos,
    validar_cpf,
    validar_data,
    validar_horario,
    validar_telefone,
)

# Tolerância para relógios levemente diferentes ao informar a hora de entrada.
_TOLERANCIA_FUTURO = timedelta(minutes=5)


@dataclass(slots=True)
class DadosCadastro:
    """Valores brutos digitados na tela de cadastro."""

    nome: str
    cpf: str
    telefone: str
    empresa: str
    tipo_acesso: str
    data_entrada: str
    horario_entrada: str
    motivo: str


class PessoaService:
    def __init__(
        self,
        pessoas: PessoaRepository,
        relogio: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._pessoas = pessoas
        self._relogio = relogio

    def cadastrar(self, dados: DadosCadastro) -> Pessoa:
        """Valida os dados, grava a pessoa e registra sua primeira entrada."""
        entrada = self._validar(dados)
        cpf = somente_digitos(dados.cpf)
        if self._pessoas.buscar_por_cpf(cpf) is not None:
            raise DuplicadoError("Já existe uma pessoa cadastrada com este CPF.")

        pessoa = Pessoa(
            nome=" ".join(dados.nome.split()),
            cpf=cpf,
            telefone=somente_digitos(dados.telefone),
            empresa=dados.empresa.strip(),
            tipo_acesso=dados.tipo_acesso,
            motivo=dados.motivo.strip(),
            criado_em=self._relogio(),
        )
        return self._pessoas.inserir_com_entrada(pessoa, entrada)

    def listar(self) -> list[Pessoa]:
        return self._pessoas.listar()

    def _validar(self, dados: DadosCadastro) -> datetime:
        vazios = campos_vazios(
            {
                "Nome completo": dados.nome,
                "CPF": dados.cpf,
                "Telefone": dados.telefone,
                "Empresa": dados.empresa,
                "Tipo de acesso": dados.tipo_acesso,
                "Data de entrada": dados.data_entrada,
                "Horário de entrada": dados.horario_entrada,
                "Motivo da visita": dados.motivo,
            }
        )
        if vazios:
            raise ValidacaoError("Preencha os campos obrigatórios:\n• " + "\n• ".join(vazios))

        erros: list[str] = []
        if len(dados.nome.split()) < 2:
            erros.append("Informe o nome completo (nome e sobrenome).")
        if not validar_cpf(dados.cpf):
            erros.append("CPF inválido.")
        if not validar_telefone(dados.telefone):
            erros.append("Telefone inválido. Use (00) 00000-0000 ou (00) 0000-0000.")
        if dados.tipo_acesso not in config.TIPOS_ACESSO:
            erros.append("Selecione um tipo de acesso válido.")
        if not validar_data(dados.data_entrada):
            erros.append("Data de entrada inválida (use dd/mm/aaaa).")
        if not validar_horario(dados.horario_entrada):
            erros.append("Horário de entrada inválido (use HH:MM).")
        if erros:
            raise ValidacaoError("\n".join(erros))

        entrada = datetime.strptime(
            f"{dados.data_entrada.strip()} {dados.horario_entrada.strip()}",
            config.FORMATO_DATA_HORA,
        )
        if entrada > self._relogio() + _TOLERANCIA_FUTURO:
            raise ValidacaoError("A data/hora de entrada não pode estar no futuro.")
        return entrada
