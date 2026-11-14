// API do Portal Orbe, da emissora de cartões Orbe.
//
// Aplicação de TREINAMENTO do CECyber AppSec Labs: todos os dados são fictícios e ela contém, de
// propósito, uma falha na validação de tokens JWT para você encontrar e corrigir.
//
// Como ela está organizada (veja também o README.md):
//
//     navegador ou curl -> routes/ -> middlewares/ -> controllers/ -> services/ -> repositories/
const path = require('path');
const express = require('express');

const config = require('./config');
const { criarDados } = require('./data/seed');
const UsuarioRepository = require('./repositories/usuario.repository');
const CartaoRepository = require('./repositories/cartao.repository');
const AuthService = require('./services/auth.service');
const CartaoService = require('./services/cartao.service');
const criarAuthController = require('./controllers/auth.controller');
const criarCartoesController = require('./controllers/cartoes.controller');
const criarAdminController = require('./controllers/admin.controller');
const criarRotasAuth = require('./routes/auth.routes');
const criarRotasCartoes = require('./routes/cartoes.routes');
const criarRotasAdmin = require('./routes/admin.routes');

function criarApp() {
  const dados = criarDados();
  const usuarios = new UsuarioRepository(dados);
  const cartoes = new CartaoRepository(dados);
  const cartaoService = new CartaoService(cartoes, usuarios, dados);

  const app = express();
  app.disable('x-powered-by');
  app.use(express.json());
  app.use((req, res, next) => {
    res.on('finish', () => console.log(`${req.method} ${req.originalUrl} ${res.statusCode}`));
    next();
  });
  app.use(express.static(path.join(__dirname, 'public')));
  app.use('/api', criarRotasAuth(criarAuthController(new AuthService(usuarios))));
  app.use('/api/cartoes', criarRotasCartoes(criarCartoesController(cartaoService)));
  app.use('/api/admin', criarRotasAdmin(criarAdminController(cartaoService)));
  app.use('/api', (req, res) => res.status(404).json({ erro: 'Rota não encontrada.' }));
  // Erro inesperado: detalhe só no log, resposta genérica para o usuário.
  app.use((erro, req, res, next) => {
    console.error(erro);
    res.status(500).json({ erro: 'Erro interno.' });
  });
  return app;
}

criarApp().listen(config.PORTA, '0.0.0.0', () => {
  console.log(`Portal Orbe ouvindo na porta ${config.PORTA}`);
});
