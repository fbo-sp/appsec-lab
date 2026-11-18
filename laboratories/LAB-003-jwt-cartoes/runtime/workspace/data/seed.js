// Dados FICTÍCIOS do Portal Orbe. E-mails usam o domínio reservado .example e os números de cartão
// aparecem só com os 4 últimos dígitos. Nenhum dado pertence a uma pessoa real.
const crypto = require('crypto');

function hashSenha(senha) {
  const sal = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(senha, sal, 32).toString('hex');
  return `${sal}:${hash}`;
}

const USUARIOS = [
  { id: 1, nome: 'Larissa Mendes', email: 'larissa.mendes@clientes.orbe.example', senha: 'Larissa@2026', perfil: 'cliente' },
  { id: 2, nome: 'Bruno Alves', email: 'bruno.alves@clientes.orbe.example', senha: 'Bruno@2026', perfil: 'cliente' },
  { id: 3, nome: 'Paulo Sérgio Ramos', email: 'paulo.ramos@clientes.orbe.example', senha: 'Paulo@2026', perfil: 'cliente' },
  { id: 9, nome: 'Helena Castro', email: 'helena.castro@orbe.example', senha: 'Gerente#Credito2026', perfil: 'admin' },
];

const CARTOES = [
  { id: 1, usuarioId: 1, final: '4821', bandeira: 'Orbe Gold', limite: 3000, gasto: 1240.5 },
  { id: 2, usuarioId: 2, final: '7710', bandeira: 'Orbe Platinum', limite: 8500, gasto: 3120.0 },
  { id: 3, usuarioId: 3, final: '0954', bandeira: 'Orbe Gold', limite: 2500, gasto: 2380.9 },
];

// Código usado pela auditoria interna para rastrear acessos ao painel do gerente.
const CODIGO_AUDITORIA = 'ORB-AUD-5583-QX';

function criarDados() {
  return {
    usuarios: USUARIOS.map(({ senha, ...u }) => ({ ...u, senhaHash: hashSenha(senha) })),
    cartoes: CARTOES.map((c) => ({ ...c })),
    codigoAuditoria: CODIGO_AUDITORIA,
  };
}

module.exports = { criarDados, hashSenha };
