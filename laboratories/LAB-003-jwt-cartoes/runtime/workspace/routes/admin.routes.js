const express = require('express');
const { autenticar, exigirPerfil } = require('../middlewares/autenticacao');

function criarRotasAdmin(adminController) {
  const rotas = express.Router();
  // Toda rota daqui exige token válido E perfil de gerente (admin).
  rotas.use(autenticar, exigirPerfil('admin'));
  rotas.get('/resumo', adminController.resumo);
  rotas.patch('/cartoes/:id/limite', adminController.alterarLimite);
  return rotas;
}

module.exports = criarRotasAdmin;
