/* App mobile SIMULADO do laboratório (ADR-025). Fala com a API como um app Android/iOS faria. */
(function () {
  "use strict";
  var LAB = window.LAB || { recursos: [] };
  var tem = function (r) { return LAB.recursos.indexOf(r) >= 0; };
  var estado = { token: null, contaId: null, chave: null, aba: "inicio" };
  var raiz = document.getElementById("app");

  function el(tag, classe, texto) {
    var n = document.createElement(tag);
    if (classe) n.className = classe;
    if (texto !== undefined && texto !== null) n.textContent = String(texto);
    return n;
  }

  function api(metodo, caminho, corpo, extras) {
    var h = { "Content-Type": "application/json" };
    if (estado.token) h.Authorization = "Bearer " + estado.token;
    if (estado.chave) h["X-Api-Key"] = estado.chave;
    Object.keys(extras || {}).forEach(function (k) { h[k] = extras[k]; });
    return fetch(caminho, { method: metodo, headers: h, body: corpo ? JSON.stringify(corpo) : undefined })
      .then(function (r) {
        return r.text().then(function (t) {
          var d = {};
          try { d = t ? JSON.parse(t) : {}; } catch (e) { d = {}; }
          return { ok: r.ok, status: r.status, dados: d };
        });
      });
  }

  function barra(titulo, botao) {
    var b = el("header", "barra");
    var t = el("div");
    t.appendChild(el("div", "marca", LAB.marca));
    t.appendChild(el("h1", null, titulo));
    b.appendChild(t);
    if (botao) b.appendChild(botao);
    return b;
  }

  function telaLogin() {
    raiz.innerHTML = "";
    var corpo = el("section", "corpo");
    var m = el("div", "marca-login");
    m.appendChild(el("strong", null, LAB.marca));
    m.appendChild(el("span", null, "Entre na sua conta"));
    corpo.appendChild(m);
    if (tem("homologacao")) corpo.appendChild(el("span", "etiqueta", "Modo homologação"));
    var f = el("form");
    f.style.display = "flex"; f.style.flexDirection = "column"; f.style.gap = "10px";
    var lu = el("label", "campo", "Usuário"); var u = el("input"); u.name = "login"; u.autocomplete = "username"; lu.appendChild(u);
    var ls = el("label", "campo", "Senha"); var s = el("input"); s.type = "password"; s.name = "senha"; s.autocomplete = "current-password"; ls.appendChild(s);
    var erro = el("div", "erro");
    var b = el("button", "botao", "Entrar"); b.type = "submit";
    f.appendChild(lu); f.appendChild(ls); f.appendChild(erro); f.appendChild(b);
    f.addEventListener("submit", function (ev) {
      ev.preventDefault();
      api("POST", "/api/login", { login: u.value, senha: s.value }).then(function (r) {
        if (!r.ok) { erro.textContent = "Usuário ou senha inválidos."; return; }
        estado.token = r.dados.token; estado.contaId = r.dados.contaId; estado.aba = "inicio";
        telaApp();
      });
    });
    corpo.appendChild(f);
    raiz.appendChild(corpo);
  }

  function sair() {
    var fim = function () { estado.token = null; estado.contaId = null; telaLogin(); };
    if (tem("sair")) api("POST", "/api/sair").then(fim, fim); else fim();
  }

  function itemLinha(i) {
    var d = el("div", "item");
    var t = el("div");
    t.appendChild(el("b", null, i.titulo));
    t.appendChild(el("small", null, i.detalhe));
    d.appendChild(t);
    d.appendChild(el("div", "valor", i.valor));
    return d;
  }

  function folhaBiometria(corpo) {
    var fundo = el("div", "fundo");
    var folha = el("div", "folha");
    folha.appendChild(el("div", "digital", "◉"));
    folha.appendChild(el("strong", null, "Confirme com a digital"));
    folha.appendChild(el("small", null, LAB.acao));
    var tocar = el("button", "botao", "Tocar no sensor");
    var cancelar = el("button", "botao claro", "Cancelar");
    tocar.addEventListener("click", function () {
      // O sensor do aparelho confirmou a digital: o app pede a prova e envia junto com a operação.
      api("POST", "/api/biometria/prova").then(function (p) {
        return api("POST", "/api/acao", { acao: LAB.acao }, { "X-Prova-Biometria": (p.dados && p.dados.prova) || "" });
      }).then(function (r) {
        fundo.remove();
        corpo.appendChild(el("div", r.ok ? "ok" : "erro", r.ok ? "Operação concluída: " + LAB.acao : "Operação recusada."));
      });
    });
    cancelar.addEventListener("click", function () { fundo.remove(); });
    folha.appendChild(tocar); folha.appendChild(cancelar);
    fundo.appendChild(folha);
    document.body.appendChild(fundo);
  }

  function telaApp() {
    raiz.innerHTML = "";
    var botaoSair = el("button", null, "Sair");
    botaoSair.addEventListener("click", sair);
    var titulo = estado.aba === "perfil" ? "Meu perfil" : LAB.lista;
    raiz.appendChild(barra(titulo, botaoSair));
    var corpo = el("section", "corpo");
    raiz.appendChild(corpo);
    if (estado.aba === "perfil") {
      api("GET", "/api/perfil").then(function (r) {
        if (!r.ok) { corpo.appendChild(el("div", "erro", "Sessão expirada. Entre de novo.")); return; }
        // A tela mostra só o nome e o resumo.
        var c = el("div", "cartao"); c.appendChild(el("small", null, "Nome")); c.appendChild(el("strong", null, r.dados.nome));
        corpo.appendChild(c);
        corpo.appendChild(itemLinha({ titulo: "Resumo", detalhe: r.dados.resumo, valor: "" }));
      });
    } else {
      api("GET", "/api/conta").then(function (r) {
        if (!r.ok) { corpo.appendChild(el("div", "erro", "Sessão expirada. Entre de novo.")); return; }
        var c = el("div", "cartao");
        c.appendChild(el("small", null, "Olá, " + String(r.dados.nome).split(" ")[0]));
        c.appendChild(el("strong", null, r.dados.resumo));
        corpo.insertBefore(c, corpo.firstChild);
      });
      var lista = el("div");
      lista.style.display = "flex"; lista.style.flexDirection = "column"; lista.style.gap = "8px";
      corpo.appendChild(el("div", "secao", LAB.lista));
      corpo.appendChild(lista);
      var caminho = tem("chave") ? "/api/itens?conta=" + estado.contaId : "/api/itens";
      api("GET", caminho).then(function (r) {
        ((r.dados && r.dados.itens) || []).forEach(function (i) { lista.appendChild(itemLinha(i)); });
      });
      if (tem("biometria")) {
        var acao = el("button", "botao", LAB.acao);
        acao.addEventListener("click", function () { folhaBiometria(corpo); });
        corpo.appendChild(acao);
      }
    }
    var nav = el("nav", "nav");
    var abas = [["inicio", "Início"]];
    if (tem("perfil")) abas.push(["perfil", "Perfil"]);
    abas.forEach(function (a) {
      var b = el("button", estado.aba === a[0] ? "ativo" : "", a[1]);
      b.addEventListener("click", function () { estado.aba = a[0]; telaApp(); });
      nav.appendChild(b);
    });
    raiz.appendChild(nav);
  }

  if (tem("chave")) {
    // Como um app real, lê a configuração empacotada junto com ele (cliente/config.json).
    fetch("/cliente/config.json").then(function (r) { return r.json(); }).then(function (c) {
      estado.chave = c.api_key; telaLogin();
    }, telaLogin);
  } else {
    telaLogin();
  }
})();
