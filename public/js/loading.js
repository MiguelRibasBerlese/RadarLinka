(function() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.getElementById('loading-screen').style.display = 'none';
        return;
    }

    const scene    = new THREE.Scene();
    const camera   = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    document.getElementById('canvas-container').appendChild(renderer.domElement);
    camera.position.z = 4;

    const loader = new THREE.TextureLoader();

    // ── FUNDO ESTRELADO ──────────────────────────────────────────────────────────
    const starsTexture = loader.load('assets/textures/stars.jpg');
    const bgMat = new THREE.MeshBasicMaterial({ map: starsTexture, side: THREE.BackSide });
    scene.add(new THREE.Mesh(new THREE.SphereGeometry(500, 32, 32), bgMat));

    // ── PLANETA BASE ─────────────────────────────────────────────────────────────
    const planetMat = new THREE.MeshPhongMaterial({
        color:             new THREE.Color(0x0d1b3e),
        emissive:          new THREE.Color(0x6030cc),
        emissiveIntensity: 0.85,
        shininess:         12,
        specular:          new THREE.Color(0x334488),
    });
    const planet = new THREE.Mesh(new THREE.SphereGeometry(1.5, 64, 64), planetMat);
    planet.rotation.y = Math.PI * 0.15;
    scene.add(planet);

    // ── OVERLAY PAÍSES (emissiveMap invertido) ───────────────────────────────────
    const countriesMat = new THREE.MeshPhongMaterial({
        color:             new THREE.Color(0x000000),
        emissive:          new THREE.Color(0x9060f0),
        emissiveIntensity: 1.0,
        transparent:       true,
        depthWrite:        false,
        shininess:         0,
        specular:          new THREE.Color(0x000000),
    });
    planet.add(new THREE.Mesh(new THREE.SphereGeometry(1.501, 64, 64), countriesMat));

    loader.load('assets/textures/specular.png', (specTex) => {
        const img = specTex.image;
        const c   = document.createElement('canvas');
        c.width   = img.width;
        c.height  = img.height;
        const ctx = c.getContext('2d');
        ctx.drawImage(img, 0, 0);
        const d = ctx.getImageData(0, 0, c.width, c.height);
        for (let i = 0; i < d.data.length; i += 4) {
            d.data[i]   = 255 - d.data[i];
            d.data[i+1] = 255 - d.data[i+1];
            d.data[i+2] = 255 - d.data[i+2];
        }
        ctx.putImageData(d, 0, 0);
        countriesMat.emissiveMap = new THREE.CanvasTexture(c);
        countriesMat.needsUpdate = true;
    });

    // ── LUZES DAS CIDADES (nightmap aditivo) ─────────────────────────────────────
    const nightmap = loader.load('assets/textures/nightmap.jpg');
    const cityMat  = new THREE.MeshBasicMaterial({
        map:         nightmap,
        blending:    THREE.AdditiveBlending,
        transparent: true,
        opacity:     0.85,
        depthWrite:  false,
    });
    planet.add(new THREE.Mesh(new THREE.SphereGeometry(1.502, 64, 64), cityMat));

    // ── ATMOSFERA (glow roxo) ──────────────────────────────────────────────────
    const atmMat = new THREE.MeshPhongMaterial({
        color:       new THREE.Color(0x7040cc),
        emissive:    new THREE.Color(0x3020aa),
        transparent: true,
        opacity:     0.12,
        depthWrite:  false,
        side:        THREE.FrontSide,
    });
    scene.add(new THREE.Mesh(new THREE.SphereGeometry(1.62, 64, 64), atmMat));

    // ── ILUMINAÇÃO ────────────────────────────────────────────────────────────────
    scene.add(new THREE.AmbientLight(0x1a2255, 0.5));
    const sun = new THREE.DirectionalLight(0xffffff, 1.1);
    sun.position.set(5, 2, 4);
    scene.add(sun);
    const fillLight = new THREE.DirectionalLight(0x4420aa, 0.3);
    fillLight.position.set(-4, -1, -2);
    scene.add(fillLight);

    // ── ANIMAÇÕES DE TEXTO ────────────────────────────────────────────────────────
    const ui = document.getElementById('loading-ui');
    setTimeout(() => ui.classList.add('loading-visible'), 800);

    // ── TIMING ───────────────────────────────────────────────────────────────────
    let zoomAtivo = false, zoomInicio = 0;
    setTimeout(() => {
        zoomAtivo  = true;
        zoomInicio = Date.now();
        ui.style.transition = 'opacity 0.8s ease';
        ui.style.opacity    = '0';
    }, 3200);

    setTimeout(() => {
        const ls = document.getElementById('loading-screen');
        ls.style.transition = 'opacity 0.9s ease';
        ls.style.opacity    = '0';
        setTimeout(() => {
            ls.style.display = 'none';
            const toggle = document.getElementById('theme-toggle-wrap');
            toggle.style.opacity      = '1';
            toggle.style.pointerEvents = 'auto';
            document.getElementById('chat-bubble').classList.add('visivel');
        }, 900);
    }, 5600);

    // ── LOOP ─────────────────────────────────────────────────────────────────────
    (function animate() {
        requestAnimationFrame(animate);
        planet.rotation.y -= 0.0018;
        if (zoomAtivo) {
            const t = Math.min((Date.now() - zoomInicio) / 2500, 1);
            const e = t * t * (3 - 2 * t);
            camera.position.z = 4 - (3.92 * e);
        }
        renderer.render(scene, camera);
    })();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
})();
