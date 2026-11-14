// Serviço de cartões: regras de negócio de consulta e de alteração de limite.
const config = require('../config');

class CartaoService {
  constructor(cartaoRepository, usuarioRepository, dados) {
    this.cartoes = cartaoRepository;
    this.usuarios = usuarioRepository;
    this.dados = dados;
  }

  meuCartao(usuarioId) {
    const cartao = this.cartoes.buscarPorUsuario(usuarioId);
    return cartao ? this.formatar(cartao) : null;
  }

  resumoGerencial() {
    return {
      codigoAuditoria: this.dados.codigoAuditoria,
      cartoes: this.cartoes.listarTodos().map((c) => this.formatar(c)),
    };
  }

  alterarLimite(cartaoId, novoLimite) {
    const valor = Number(novoLimite);
    if (!Number.isFinite(valor) || valor <= 0 || valor > config.LIMITE_MAXIMO) {
      return { erro: `O limite deve estar entre 1 e ${config.LIMITE_MAXIMO}.` };
    }
    const anterior = this.cartoes.buscarPorId(cartaoId);
    if (!anterior) return { erro: 'Cartão não encontrado.' };
    const limiteAnterior = anterior.limite;
    const cartao = this.cartoes.atualizarLimite(cartaoId, valor);
    return {
      cartao: this.formatar(cartao),
      limiteAnterior,
      protocolo: `ORB-LIM-${cartao.final}-${valor}`,
    };
  }

  formatar(cartao) {
    const titular = this.usuarios.buscarPorId(cartao.usuarioId);
    return {
      id: cartao.id,
      titular: titular ? titular.nome : '',
      bandeira: cartao.bandeira,
      final: cartao.final,
      limite: cartao.limite,
      disponivel: Math.round((cartao.limite - cartao.gasto) * 100) / 100,
    };
  }
}

module.exports = CartaoService;
