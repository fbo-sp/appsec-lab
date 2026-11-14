const express = require('express');
const { autenticar } = require('../middlewares/autenticacao');

function criarRotasCartoes(cartoesController) {
  const rotas = express.Router();
  rotas.get('/meu', autenticar, cartoesController.meu);
  return rotas;
}

module.exports = criarRotasCartoes;
