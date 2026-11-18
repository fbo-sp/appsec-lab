// Serviço de tokens: emite o JWT no login e lê o JWT que chega em cada requisição.
const jwt = require('jsonwebtoken');
const config = require('../config');

function emitirToken(usuario) {
  // Os "claims" (dados) do token: quem é o usuário e qual o perfil dele.
  const dados = { sub: usuario.id, nome: usuario.nome, perfil: usuario.perfil };
  return jwt.sign(dados, config.SEGREDO_JWT, { algorithm: 'HS256', expiresIn: config.EXPIRACAO_TOKEN });
}

function lerToken(token) {
  // Lê os dados (claims) do token recebido no cabeçalho Authorization.
  return jwt.decode(token);
}

module.exports = { emitirToken, lerToken };
