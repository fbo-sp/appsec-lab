/* Regras do app (vão empacotadas no APK/IPA, junto com o resto do código do app). */
window.REGRAS = {
  // Plano que o app considera para a conta: o que veio do cadastro, na resposta de /api/conta.
  plano: function (conta) {
    return conta.plano;
  },
  // "Verificação de integridade" feita pelo próprio app: ele mesmo diz que está íntegro.
  integridade: function () {
    return "ok";
  }
};
