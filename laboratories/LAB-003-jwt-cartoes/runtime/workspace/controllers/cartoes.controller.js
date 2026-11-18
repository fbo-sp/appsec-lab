// Camada de controle: cartão do cliente logado.
function criarCartoesController(cartaoService) {
  return {
    meu(req, res) {
      const cartao = cartaoService.meuCartao(req.usuario.id);
      if (!cartao) return res.status(404).json({ erro: 'Nenhum cartão encontrado.' });
      return res.json(cartao);
    },
  };
}

module.exports = criarCartoesController;
