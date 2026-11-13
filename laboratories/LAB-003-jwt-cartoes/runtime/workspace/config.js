// Configurações da API do Portal Orbe.
//
// ATENÇÃO: o segredo abaixo é FICTÍCIO e existe só neste laboratório. Em produção ele viria de um
// cofre de segredos (variável de ambiente injetada no deploy), nunca do código-fonte.
module.exports = {
  PORTA: 8080,
  SEGREDO_JWT: 'orbe-segredo-ficticio-lab003-hs256',
  EXPIRACAO_TOKEN: '30m',
  LIMITE_MAXIMO: 100000,
};
