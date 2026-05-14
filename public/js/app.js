// Data da edição
(function() {
    const meses = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
    const hoje = new Date();
    const el = document.getElementById('data-edicao');
    if (el) el.textContent = hoje.getDate() + ' de ' + meses[hoje.getMonth()] + ' de ' + hoje.getFullYear();
})();

const BADGE_CORES = {
    'Show':        '#C0392B',
    'Festa':       '#6C3483',
    'Feira':       '#1E8449',
    'Festival':    '#B7770D',
    'Teatro':      '#1A5276',
    'Esporte':     '#0E6655',
    'Corporativo': '#7F8C8D',
    'Curso':       '#1A6B8A',
    'Exposição':   '#884EA0',
    'Religioso':   '#A04000',
    'Turismo':     '#1D8348',
    'Infantil':    '#CB4335',
    'Outro':       '#95A5A6',
};

let _todosEventos = [];

function formatarData(iso) {
    if (!iso) return 'Data a confirmar';
    try {
        const [a, m, d] = iso.split('-');
        return d + '/' + m + '/' + a;
    } catch(e) { return iso; }
}

// ── helpers de data ──────────────────────────────────────────────────────────
function _hoje() {
    const d = new Date(); d.setHours(0,0,0,0); return d;
}
function _isoParaDate(iso) {
    if (!iso) return null;
    const [a, m, d] = iso.split('-').map(Number);
    const dt = new Date(a, m - 1, d);
    return isNaN(dt) ? null : dt;
}
function _dataOkParaFiltro(iso, filtro) {
    if (filtro === 'todos') return true;
    const dt = _isoParaDate(iso);
    if (!dt) return filtro === 'todos';
    const hoje = _hoje();
    const diff = Math.round((dt - hoje) / 86400000);
    const diaSemana = dt.getDay();
    if (filtro === 'hoje')   return diff === 0;
    if (filtro === 'fds')    return diff >= 0 && diff <= 7 && (diaSemana === 5 || diaSemana === 6 || diaSemana === 0);
    if (filtro === 'semana') return diff >= 0 && diff <= 7;
    if (filtro === 'mes')    return diff >= 0 && diff <= 31;
    return true;
}

function gerarCard(ev) {
    const cat    = ev.categoria || 'Outro';
    const cor    = BADGE_CORES[cat] || '#95A5A6';
    const titulo = (ev.titulo || '').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    const local  = (ev.local  || 'Ribeirão Preto').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    const data   = formatarData(ev.data_iso);
    const narr   = (ev.narrativa_ia || '').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    const url    = ev.url || '#';
    const cidade = ev.cidade || 'Ribeirão Preto';
    const art = document.createElement('article');
    art.className = 'card';
    art.dataset.cat    = cat;
    art.dataset.cidade = cidade;
    art.onclick = () => window.open(url, '_blank');
    art.innerHTML =
        '<span class="badge" style="background:' + cor + '">' + cat + '</span>' +
        '<h2>' + titulo + '</h2>' +
        '<p class="meta">' + data + ' &nbsp;·&nbsp; ' + local + '</p>' +
        (narr ? '<p class="narrativa">' + narr + '</p>' : '');
    return art;
}

const observadorCards = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
            setTimeout(() => entry.target.classList.add('visivel'), i * 60);
            observadorCards.unobserve(entry.target);
        }
    });
}, { threshold: 0.08 });

function renderizarGrid(eventos) {
    const grid = document.getElementById('grid-eventos');
    if (!grid) return;
    grid.innerHTML = '';
    if (!eventos.length) {
        grid.innerHTML = '<p class="vazio">Nenhum evento encontrado.</p>';
        const label = document.getElementById('count-label');
        if (label) label.textContent = '0 eventos';
        return;
    }
    eventos.forEach(ev => {
        const card = gerarCard(ev);
        grid.appendChild(card);
        observadorCards.observe(card);
    });
    const label = document.getElementById('count-label');
    if (label) label.textContent = eventos.length + ' evento' + (eventos.length !== 1 ? 's' : '');
}

function popularDropdowns(eventos) {
    const cats    = {};
    const cidades = {};
    eventos.forEach(ev => {
        const c  = ev.categoria || 'Outro';
        const ci = ev.cidade    || 'Ribeirão Preto';
        cats[c]   = (cats[c]   || 0) + 1;
        cidades[ci] = (cidades[ci] || 0) + 1;
    });

    const csCat    = document.getElementById('cs-cat');
    const csCidade = document.getElementById('cs-cidade');
    const listCat    = csCat    ? csCat.querySelector('.cs-list')    : null;
    const listCidade = csCidade ? csCidade.querySelector('.cs-list') : null;

    const catAtual    = csCat    ? (csCat.dataset.value    || 'todos')  : 'todos';
    const cidadeAtual = csCidade ? (csCidade.dataset.value || 'todas') : 'todas';

    if (listCat) {
        const atoC = catAtual === 'todos' ? ' ativo' : '';
        let h = '<li class="cs-item' + atoC + '" data-value="todos">Todos os tipos</li>';
        Object.keys(cats).sort().forEach(c => {
            const ativo = catAtual === c ? ' ativo' : '';
            h += '<li class="cs-item' + ativo + '" data-value="' + c.replace(/"/g,'&quot;') + '">' + c + ' (' + cats[c] + ')</li>';
        });
        listCat.innerHTML = h;
    }

    if (listCidade) {
        const atoD = cidadeAtual === 'todas' ? ' ativo' : '';
        let h = '<li class="cs-item' + atoD + '" data-value="todas">Todas as regiões</li>';
        Object.keys(cidades).sort().forEach(ci => {
            const ativo = cidadeAtual === ci ? ' ativo' : '';
            h += '<li class="cs-item' + ativo + '" data-value="' + ci.replace(/"/g,'&quot;') + '">' + ci + ' (' + cidades[ci] + ')</li>';
        });
        listCidade.innerHTML = h;
    }

    // Popula contagem nos chips de data
    _atualizarContagemChips();
}

function _atualizarContagemChips() {
    const chips = document.querySelectorAll('#chips-data .pf-chip');
    const LABELS = { hoje: 'Hoje', fds: 'Fim de semana', semana: 'Esta semana', mes: 'Este mês', todos: 'Todos' };
    chips.forEach(chip => {
        const v = chip.dataset.value;
        if (v === 'todos') { chip.textContent = 'Todos'; return; }
        const n = _todosEventos.filter(ev => _dataOkParaFiltro(ev.data_iso, v)).length;
        chip.textContent = LABELS[v] + (n ? ' · ' + n : '');
    });
}

// ── Filtros ativos ───────────────────────────────────────────────────────────
function _atualizarAtivos() {
    const cat    = document.getElementById('cs-cat')?.dataset.value    || 'todos';
    const cidade = document.getElementById('cs-cidade')?.dataset.value || 'todas';
    const data   = document.querySelector('#chips-data .pf-chip.ativo')?.dataset.value || 'todos';
    const busca  = document.getElementById('busca-input')?.value?.trim() || '';
    const LABELS_DATA = { hoje: 'Hoje', fds: 'Fim de semana', semana: 'Esta semana', mes: 'Este mês' };

    const ativos = [];
    if (cat    !== 'todos')  ativos.push({ label: cat,                       tipo: 'cat' });
    if (cidade !== 'todas')  ativos.push({ label: cidade,                    tipo: 'cidade' });
    if (data   !== 'todos')  ativos.push({ label: LABELS_DATA[data] || data, tipo: 'data' });
    if (busca)               ativos.push({ label: '"' + busca + '"',         tipo: 'busca' });

    // Painel interno
    const pAtivos  = document.getElementById('pf-ativos');
    const chipsEl  = document.getElementById('pf-ativos-chips');
    if (pAtivos && chipsEl) {
        if (!ativos.length) { pAtivos.style.display = 'none'; }
        else {
            pAtivos.style.display = 'flex';
            chipsEl.innerHTML = ativos.map(a =>
                '<button class="pf-ativo-chip" data-tipo="' + a.tipo + '" onclick="_removerFiltro(this)">' +
                a.label +
                '<svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 2l6 6M8 2l-6 6"/></svg>' +
                '</button>'
            ).join('');
        }
    }

    // Badge e chips inline na barra superior
    const badge       = document.getElementById('filtros-badge');
    const inlineEl    = document.getElementById('pf-ativos-inline');
    if (badge) {
        if (ativos.length) { badge.textContent = ativos.length; badge.style.display = 'inline-flex'; }
        else               { badge.style.display = 'none'; }
    }
    if (inlineEl) {
        inlineEl.innerHTML = ativos.map(a =>
            '<button class="pf-ativo-chip" data-tipo="' + a.tipo + '" onclick="_removerFiltro(this)">' +
            a.label +
            '<svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 2l6 6M8 2l-6 6"/></svg>' +
            '</button>'
        ).join('');
    }
}

function _removerFiltro(btn) {
    const tipo = btn.dataset.tipo;
    if (tipo === 'cat') {
        const cs = document.getElementById('cs-cat');
        cs.dataset.value = 'todos';
        cs.querySelector('.cs-value').textContent = 'Todos os tipos';
        cs.querySelectorAll('.cs-item').forEach(i => i.classList.toggle('ativo', i.dataset.value === 'todos'));
    } else if (tipo === 'cidade') {
        const cs = document.getElementById('cs-cidade');
        cs.dataset.value = 'todas';
        cs.querySelector('.cs-value').textContent = 'Todas as regiões';
        cs.querySelectorAll('.cs-item').forEach(i => i.classList.toggle('ativo', i.dataset.value === 'todas'));
    } else if (tipo === 'data') {
        document.querySelectorAll('#chips-data .pf-chip').forEach(c => c.classList.toggle('ativo', c.dataset.value === 'todos'));
    } else if (tipo === 'busca') {
        const input = document.getElementById('busca-input');
        if (input) input.value = '';
        document.getElementById('busca-clear')?.classList.remove('visible');
    }
    aplicarFiltros();
}

function limparTodosFiltros() {
    const csCat = document.getElementById('cs-cat');
    csCat.dataset.value = 'todos';
    csCat.querySelector('.cs-value').textContent = 'Todos os tipos';
    csCat.querySelectorAll('.cs-item').forEach(i => i.classList.toggle('ativo', i.dataset.value === 'todos'));

    const csCidade = document.getElementById('cs-cidade');
    csCidade.dataset.value = 'todas';
    csCidade.querySelector('.cs-value').textContent = 'Todas as regiões';
    csCidade.querySelectorAll('.cs-item').forEach(i => i.classList.toggle('ativo', i.dataset.value === 'todas'));

    document.querySelectorAll('#chips-data .pf-chip').forEach(c => c.classList.toggle('ativo', c.dataset.value === 'todos'));

    const input = document.getElementById('busca-input');
    if (input) input.value = '';
    document.getElementById('busca-clear')?.classList.remove('visible');

    aplicarFiltros();
}

function aplicarFiltros() {
    const cat    = document.getElementById('cs-cat')?.dataset.value    || 'todos';
    const cidade = document.getElementById('cs-cidade')?.dataset.value || 'todas';
    const data   = document.querySelector('#chips-data .pf-chip.ativo')?.dataset.value || 'todos';
    const busca  = (document.getElementById('busca-input')?.value || '')
                    .toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

    document.getElementById('busca-clear')?.classList.toggle('visible', busca.length > 0);

    const filtrados = _todosEventos.filter(ev => {
        const catOk    = cat    === 'todos' || (ev.categoria || 'Outro') === cat;
        const cidadeOk = cidade === 'todas' || (ev.cidade    || 'Ribeirão Preto') === cidade;
        const dataOk   = _dataOkParaFiltro(ev.data_iso, data);
        let buscaOk = true;
        if (busca) {
            const texto = ((ev.titulo || '') + ' ' + (ev.local || '') + ' ' + (ev.narrativa_ia || ''))
                .toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
            buscaOk = texto.includes(busca);
        }
        return catOk && cidadeOk && dataOk && buscaOk;
    });

    renderizarGrid(filtrados);
    _atualizarAtivos();
}

function togglePainelFiltros() {
    const painel = document.getElementById('painel-filtros');
    const btn    = document.getElementById('btn-filtros');
    const aberto = painel.classList.toggle('aberto');
    btn.setAttribute('aria-expanded', aberto);
}

function limparBusca() {
    const input = document.getElementById('busca-input');
    if (input) { input.value = ''; input.focus(); }
    aplicarFiltros();
}

async function carregarEventos() {
    try {
        const resp = await fetch('data/events.json?v=' + Date.now());
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        _todosEventos = await resp.json();
        popularDropdowns(_todosEventos);
        aplicarFiltros();
    } catch(e) {
        const grid = document.getElementById('grid-eventos');
        if (grid) grid.innerHTML = '<p class="vazio">Erro ao carregar eventos. Tente recarregar a página.</p>';
        const label = document.getElementById('count-label');
        if (label) label.textContent = '0 eventos';
    }
}

// ── Chips de data ────────────────────────────────────────────────────────────
document.querySelectorAll('#chips-data .pf-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        document.querySelectorAll('#chips-data .pf-chip').forEach(c => c.classList.remove('ativo'));
        chip.classList.add('ativo');
        aplicarFiltros();
    });
});

// ── Dropdowns customizados ───────────────────────────────────────────────────
document.querySelectorAll('.custom-select').forEach(cs => {
    const trigger = cs.querySelector('.cs-trigger');
    const valueEl = cs.querySelector('.cs-value');
    const list    = cs.querySelector('.cs-list');

    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        document.querySelectorAll('.custom-select.open').forEach(o => { if (o !== cs) o.classList.remove('open'); });
        cs.classList.toggle('open');
    });

    list.addEventListener('click', (e) => {
        const item = e.target.closest('.cs-item');
        if (!item) return;
        list.querySelectorAll('.cs-item').forEach(i => i.classList.remove('ativo'));
        item.classList.add('ativo');
        valueEl.textContent = item.textContent;
        cs.dataset.value = item.dataset.value;
        cs.classList.remove('open');
        aplicarFiltros();
    });
});

document.addEventListener('click', () => {
    document.querySelectorAll('.custom-select.open').forEach(o => o.classList.remove('open'));
});

carregarEventos();
