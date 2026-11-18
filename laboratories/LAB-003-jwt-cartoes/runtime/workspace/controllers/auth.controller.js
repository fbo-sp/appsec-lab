// Camada de controle: login.
function criarAuthController(authService) {
  return {
    entrar(req, res) {
      const resultado = authService.entrar(req.body.email, req.body.senha);
      if (!resultado) return res.status(401).json({ erro: 'E-mail ou senha inválidos.' });
      return res.json(resultado);
    },
  };
}

module.exports = criarAuthController;
