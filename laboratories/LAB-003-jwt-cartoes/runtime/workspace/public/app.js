// Interface do Portal Orbe: guarda o token após o login e chama a API com ele.
const reais = (v) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
const $ = (id) => document.getElementById(id);

async function api(caminho) {
  const token = sessionStorage.getItem('token');
  const resposta = await fetch(caminho, { headers: { Authorization: `Bearer ${token}` } });
  if (!resposta.ok) throw new Error(resposta.status);
  return resposta.json();
}

async function mostrarCartao() {
  const usuario = JSON.parse(sessionStorage.getItem('usuario'));
  $('tela-login').hidden = true;
  $('usuario').hidden = false;
  $('usuario').innerHTML = '';
  $('usuario').append(`${usuario.nome} · `);
  const sair = document.createElement('a');
  sair.href = '#';
  sair.textContent = 'Sair';
  sair.onclick = () => { sessionStorage.clear(); location.reload(); };
  $('usuario').append(sair);

  if (usuario.perfil === 'admin') {
    const resumo = await api('/api/admin/resumo');
    $('auditoria').textContent = resumo.codigoAuditoria;
    $('lista-cartoes').innerHTML = '';
    for (const c of resumo.cartoes) {
      const linha = document.createElement('tr');
      for (const texto of [c.titular, `${c.bandeira} final ${c.final}`, reais(c.limite)]) {
        const celula = document.createElement('td');
        celula.textContent = texto;
        linha.append(celula);
      }
      linha.lastChild.className = 'valor';
      $('lista-cartoes').append(linha);
    }
    $('tela-gerente').hidden = false;
    return;
  }
  const cartao = await api('/api/cartoes/meu');
  $('bandeira').textContent = cartao.bandeira;
  $('final').textContent = cartao.final;
  $('titular').textContent = cartao.titular.toUpperCase();
  $('limite').textContent = reais(cartao.limite);
  $('disponivel').textContent = reais(cartao.disponivel);
  $('tela-cartao').hidden = false;
}

$('form-login').addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const form = new FormData(evento.target);
  const resposta = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: form.get('email'), senha: form.get('senha') }),
  });
  const corpo = await resposta.json();
  if (!resposta.ok) {
    $('erro-login').textContent = corpo.erro;
    $('erro-login').hidden = false;
    return;
  }
  sessionStorage.setItem('token', corpo.token);
  sessionStorage.setItem('usuario', JSON.stringify(corpo.usuario));
  mostrarCartao().catch(() => { sessionStorage.clear(); location.reload(); });
});

if (sessionStorage.getItem('token')) {
  mostrarCartao().catch(() => { sessionStorage.clear(); location.reload(); });
}
