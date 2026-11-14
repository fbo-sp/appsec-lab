const express = require('express');

function criarRotasAuth(authController) {
  const rotas = express.Router();
  rotas.post('/login', authController.entrar);
  return rotas;
}

module.exports = criarRotasAuth;
