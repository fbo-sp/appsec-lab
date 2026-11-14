// Camada de acesso a dados dos cartões (em memória, recriada a cada início da aplicação).
class CartaoRepository {
  constructor(dados) {
    this.dados = dados;
  }

  buscarPorUsuario(usuarioId) {
    return this.dados.cartoes.find((c) => c.usuarioId === usuarioId) || null;
  }

  buscarPorId(id) {
    return this.dados.cartoes.find((c) => c.id === id) || null;
  }

  listarTodos() {
    return this.dados.cartoes;
  }

  atualizarLimite(id, novoLimite) {
    const cartao = this.buscarPorId(id);
    if (cartao) cartao.limite = novoLimite;
    return cartao;
  }
}

module.exports = CartaoRepository;
