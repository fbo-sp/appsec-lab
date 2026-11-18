// Camada de controle: painel do gerente de crédito.
function criarAdminController(cartaoService) {
  return {
    resumo(req, res) {
      return res.json(cartaoService.resumoGerencial());
    },

    alterarLimite(req, res) {
      const resultado = cartaoService.alterarLimite(Number(req.params.id), req.body.novoLimite);
      if (resultado.erro) return res.status(400).json(resultado);
      console.log(`Limite alterado por ${req.usuario.nome} (perfil ${req.usuario.perfil}): ${resultado.protocolo}`);
      return res.json(resultado);
    },
  };
}

module.exports = criarAdminController;
