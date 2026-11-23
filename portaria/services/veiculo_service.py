from portaria.exceptions import DuplicadoError, NaoEncontradoError, ValidacaoError
from portaria.models.veiculo import Veiculo
from portaria.repositories.pessoa_repository import PessoaRepository
from portaria.repositories.veiculo_repository import VeiculoRepository
from portaria.utils.validators import campos_vazios, normalizar_placa, validar_placa


class VeiculoService:
    """Desafio extra: cadastro de veículos e placas."""

    def __init__(self, veiculos: VeiculoRepository, pessoas: PessoaRepository) -> None:
        self._veiculos = veiculos
        self._pessoas = pessoas

    def cadastrar(self, pessoa_id: int | None, placa: str, modelo: str, cor: str) -> Veiculo:
        vazios = campos_vazios({"Placa": placa, "Modelo": modelo, "Cor": cor})
        if pessoa_id is None:
            vazios.insert(0, "Proprietário")
        if vazios or pessoa_id is None:
            raise ValidacaoError("Preencha os campos obrigatórios:\n• " + "\n• ".join(vazios))
        if not validar_placa(placa):
            raise ValidacaoError("Placa inválida. Use ABC-1234 ou o padrão Mercosul ABC1D23.")
        if self._pessoas.buscar_por_id(pessoa_id) is None:
            raise NaoEncontradoError("Proprietário não encontrado.")

        normalizada = normalizar_placa(placa)
        if self._veiculos.buscar_por_placa(normalizada) is not None:
            raise DuplicadoError("Esta placa já está cadastrada.")
        return self._veiculos.inserir(
            Veiculo(pessoa_id=pessoa_id, placa=normalizada, modelo=modelo.strip(), cor=cor.strip())
        )

    def listar(self) -> list[Veiculo]:
        return self._veiculos.listar()

    def excluir(self, veiculo_id: int) -> None:
        if not self._veiculos.excluir(veiculo_id):
            raise NaoEncontradoError("Veículo não encontrado.")
