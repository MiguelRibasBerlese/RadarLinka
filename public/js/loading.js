(function() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.getElementById('loading-screen').style.display = 'none';
        return;
    }

    const scene    = new THREE.Scene();
    const camera   = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    document.getElementById('canvas-container').appendChild(renderer.domElement);
    camera.position.z = 4;

    const loader   = new THREE.TextureLoader();
    const nightmap = loader.load('assets/textures/nightmap.jpg');
    const specular = loader.load('assets/textures/specular.png');

    const planetMat = new THREE.MeshPhongMaterial({
        color:    new THREE.Color(0x050505),
        specular: new THREE.Color(0x000000),
        shininess: 0,
    });
    const planet = new THREE.Mesh(new THREE.SphereGeometry(1.5, 64, 64), planetMat);
    scene.add(planet);

    const countriesMat = new THREE.MeshPhongMaterial({
        color:             new THREE.Color(0x000000),
        emissive:          new THREE.Color(0x8547e4),
        emissiveIntensity: 0.9,
        specular:          new THREE.Color(0x000000),
        shininess:         0,
        transparent:       true,
        depthWrite:        false,
    });
    const countriesMesh = new THREE.Mesh(new THREE.SphereGeometry(1.501, 64, 64), countriesMat);
    planet.add(countriesMesh);

    loader.load('assets/textures/specular.png', (specTex) => {
        const img = specTex.image;
        const c = document.createElement('canvas');
        c.width = img.width; c.height = img.height;
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

    const cityMat = new THREE.MeshBasicMaterial({
        map:         nightmap,
        blending:    THREE.AdditiveBlending,
        transparent: true,
        depthWrite:  false,
    });
    planet.add(new THREE.Mesh(new THREE.SphereGeometry(1.502, 64, 64), cityMat));

    scene.add(new THREE.AmbientLight(0xffffff, 0.6));

    const ui = document.getElementById('loading-ui');
    setTimeout(() => ui.style.opacity = '1', 1000);

    let zoomAtivo = false, zoomInicio = 0;
    setTimeout(() => {
        zoomAtivo = true;
        zoomInicio = Date.now();
        ui.style.opacity = '0';
    }, 3000);

    setTimeout(() => {
        const ls = document.getElementById('loading-screen');
        ls.style.transition = 'opacity 0.8s ease';
        ls.style.opacity = '0';
        setTimeout(() => {
            ls.style.display = 'none';
            const toggle = document.getElementById('theme-toggle-wrap');
            toggle.style.opacity = '1';
            toggle.style.pointerEvents = 'auto';
            document.getElementById('chat-bubble').classList.add('visivel');
        }, 800);
    }, 5500);

    (function animate() {
        requestAnimationFrame(animate);
        planet.rotation.y += 0.002;
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
