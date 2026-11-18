// Serviço de autenticação: confere e-mail e senha e emite o token de acesso.
const crypto = require('crypto');
const { emitirToken } = require('./token.service');

class AuthService {
  constructor(usuarioRepository) {
    this.usuarios = usuarioRepository;
  }

  entrar(email, senha) {
    const usuario = this.usuarios.buscarPorEmail(String(email || '').trim().toLowerCase());
    if (!usuario || !this.senhaConfere(String(senha || ''), usuario.senhaHash)) return null;
    return { token: emitirToken(usuario), usuario: { nome: usuario.nome, perfil: usuario.perfil } };
  }

  senhaConfere(senha, senhaHash) {
    const [sal, hash] = senhaHash.split(':');
    const calculado = crypto.scryptSync(senha, sal, 32);
    return crypto.timingSafeEqual(calculado, Buffer.from(hash, 'hex'));
  }
}

module.exports = AuthService;
