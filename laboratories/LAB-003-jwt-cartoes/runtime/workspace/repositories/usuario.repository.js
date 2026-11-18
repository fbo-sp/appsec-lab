// Camada de acesso a dados dos usuários (em memória, recriada a cada início da aplicação).
class UsuarioRepository {
  constructor(dados) {
    this.dados = dados;
  }

  buscarPorEmail(email) {
    return this.dados.usuarios.find((u) => u.email === email) || null;
  }

  buscarPorId(id) {
    return this.dados.usuarios.find((u) => u.id === id) || null;
  }
}

module.exports = UsuarioRepository;
