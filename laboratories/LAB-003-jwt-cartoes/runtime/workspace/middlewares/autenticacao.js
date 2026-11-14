// Middlewares de segurança: quem é o usuário (autenticar) e o que ele pode fazer (exigirPerfil).
const { lerToken } = require('../services/token.service');

function autenticar(req, res, next) {
  const cabecalho = req.get('Authorization') || '';
  const [tipo, token] = cabecalho.split(' ');
  if (tipo !== 'Bearer' || !token) {
    return res.status(401).json({ erro: 'Token ausente.' });
  }
  const dados = lerToken(token);
  if (!dados) {
    return res.status(401).json({ erro: 'Token inválido.' });
  }
  req.usuario = { id: dados.sub, nome: dados.nome, perfil: dados.perfil };
  return next();
}

function exigirPerfil(perfil) {
  return (req, res, next) => {
    if (req.usuario.perfil !== perfil) {
      return res.status(403).json({ erro: 'Acesso restrito.' });
    }
    return next();
  };
}

module.exports = { autenticar, exigirPerfil };
