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
        let h = '<li class="cs-item' + atoD + '" data-value="todas">Todas as cidades</li>';
        Object.keys(cidades).sort().forEach(ci => {
            const ativo = cidadeAtual === ci ? ' ativo' : '';
            h += '<li class="cs-item' + ativo + '" data-value="' + ci.replace(/"/g,'&quot;') + '">' + ci + ' (' + cidades[ci] + ')</li>';
        });
        listCidade.innerHTML = h;
    }
}

function aplicarFiltros() {
    const cat    = document.getElementById('cs-cat')?.dataset.value    || 'todos';
    const cidade = document.getElementById('cs-cidade')?.dataset.value || 'todas';
    const busca  = (document.getElementById('busca-input')?.value || '')
                    .toLowerCase()
                    .normalize('NFD')
                    .replace(/[̀-ͯ]/g, '');
    const btnClear = document.getElementById('busca-clear');
    if (btnClear) btnClear.classList.toggle('visible', busca.length > 0);

    const filtrados = _todosEventos.filter(ev => {
        const catOk    = cat    === 'todos' || (ev.categoria || 'Outro') === cat;
        const cidadeOk = cidade === 'todas' || (ev.cidade    || 'Ribeirão Preto') === cidade;
        let buscaOk = true;
        if (busca.length > 0) {
            const texto = ((ev.titulo || '') + ' ' + (ev.local || '') + ' ' + (ev.narrativa_ia || ''))
                .toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
            buscaOk = texto.includes(busca);
        }
        return catOk && cidadeOk && buscaOk;
    });

    renderizarGrid(filtrados);
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

// Dropdowns customizados — event delegation
(function() {
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
})();

carregarEventos();
