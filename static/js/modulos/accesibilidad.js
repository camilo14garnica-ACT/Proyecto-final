/**
 * ==========================================================================
 * MÓDULO DE ACCESIBILIDAD - VETERINARIA MASCOTT
 * Implementación de Historias de Usuario:
 * 1. Color de fuente y contraste
 * 2. Cambio de fuente y tipografía
 * 3. Herramientas transversales (Lector TTS, regla de lectura, cursor, etc.)
 * 4. Configuración y persistencia (localStorage, atajos de teclado, aria-live)
 * ==========================================================================
 */

(function () {
    'use strict';

    const STORAGE_KEY = 'mascott_accesibilidad_config';

    // Estado inicial por defecto
    const DEFAULT_CONFIG = {
        contraste: 'normal',           // 'normal', 'alto-contraste-oscuro', 'alto-contraste-claro', 'modo-oscuro', 'escala-grises', 'sepia', 'invertir'
        fuenteTamano: 100,             // 90, 100, 115, 130, 150
        tipografia: 'default',         // 'default', 'dislexia', 'serif', 'mono'
        interlineado: false,           // boolean
        interletreado: false,          // boolean
        textoIzquierda: false,         // boolean
        resaltarEnlaces: false,        // boolean
        resaltarTitulos: false,        // boolean
        sinAnimaciones: false,         // boolean
        cursorGrande: false,           // boolean
        focusVisible: false,           // boolean
        guiaLectura: false,            // boolean
        lectorVoz: false               // boolean
    };

    let config = Object.assign({}, DEFAULT_CONFIG);
    let speechSynth = window.speechSynthesis || null;
    let currentUtterance = null;
    let elementReading = null;

    /**
     * Carga configuración guardada desde localStorage
     */
    function cargarConfiguracion() {
        try {
            const guardado = localStorage.getItem(STORAGE_KEY);
            if (guardado) {
                config = Object.assign({}, DEFAULT_CONFIG, JSON.parse(guardado));
            }
        } catch (e) {
            console.warn('Accesibilidad Mascott: no se pudo leer localStorage', e);
        }
    }

    /**
     * Guarda la configuración actual en localStorage
     */
    function guardarConfiguracion() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
        } catch (e) {
            console.warn('Accesibilidad Mascott: no se pudo guardar en localStorage', e);
        }
        actualizarBadgeContador();
    }

    /**
     * Anuncio para lectores de pantalla mediante aria-live
     */
    function anunciarAccesibilidad(mensaje) {
        const liveRegion = document.getElementById('ac-live-announcer');
        if (liveRegion) {
            liveRegion.textContent = '';
            setTimeout(() => {
                liveRegion.textContent = mensaje;
            }, 50);
        }
    }

    /**
     * Aplica todas las clases y estilos en el elemento <html>
     */
    function aplicarConfiguracion() {
        const html = document.documentElement;

        // 1. Contraste y Colores
        html.classList.remove(
            'ac-alto-contraste-oscuro',
            'ac-alto-contraste-claro',
            'ac-modo-oscuro',
            'ac-escala-grises',
            'ac-sepia',
            'ac-invertir'
        );
        if (config.contraste !== 'normal') {
            html.classList.add(`ac-${config.contraste}`);
        }

        // 2. Tamaño de fuente
        html.classList.remove(
            'ac-fuente-90',
            'ac-fuente-100',
            'ac-fuente-115',
            'ac-fuente-130',
            'ac-fuente-150'
        );
        html.classList.add(`ac-fuente-${config.fuenteTamano}`);

        // 3. Tipografía
        html.classList.remove('ac-tipografia-dislexia', 'ac-tipografia-serif', 'ac-tipografia-mono');
        if (config.tipografia !== 'default') {
            html.classList.add(`ac-tipografia-${config.tipografia}`);
        }

        // 4. Espaciados
        html.classList.toggle('ac-interlineado-amplio', !!config.interlineado);
        html.classList.toggle('ac-interletreado-amplio', !!config.interletreado);
        html.classList.toggle('ac-texto-izquierda', !!config.textoIzquierda);

        // 5. Herramientas transversales
        html.classList.toggle('ac-resaltar-enlaces', !!config.resaltarEnlaces);
        html.classList.toggle('ac-resaltar-titulos', !!config.resaltarTitulos);
        html.classList.toggle('ac-sin-animaciones', !!config.sinAnimaciones);
        html.classList.toggle('ac-cursor-grande', !!config.cursorGrande);
        html.classList.toggle('ac-focus-visible', !!config.focusVisible);
        html.classList.toggle('ac-guia-lectura-activa', !!config.guiaLectura);

        // Barra de lector de voz
        const speechBar = document.getElementById('ac-speech-bar');
        if (speechBar) {
            if (config.lectorVoz) {
                speechBar.classList.add('activo');
            } else {
                speechBar.classList.remove('activo');
                detenerVoz();
            }
        }

        sincronizarControlesUI();
        guardarConfiguracion();
    }

    /**
     * Sincroniza el estado de los botones y switches en el panel HTML
     */
    function sincronizarControlesUI() {
        // Botones de contraste
        document.querySelectorAll('[data-ac-contraste]').forEach(btn => {
            const valor = btn.getAttribute('data-ac-contraste');
            btn.classList.toggle('active', valor === config.contraste);
            btn.setAttribute('aria-pressed', valor === config.contraste ? 'true' : 'false');
        });

        // Indicador de tamaño de fuente
        const indicadorFuente = document.getElementById('ac-font-size-indicator');
        if (indicadorFuente) {
            indicadorFuente.textContent = `${config.fuenteTamano}%`;
        }

        // Botones de tipografía
        document.querySelectorAll('[data-ac-tipografia]').forEach(btn => {
            const valor = btn.getAttribute('data-ac-tipografia');
            btn.classList.toggle('active', valor === config.tipografia);
            btn.setAttribute('aria-pressed', valor === config.tipografia ? 'true' : 'false');
        });

        // Switches booleanos
        const switches = [
            { id: 'ac-sw-interlineado', prop: 'interlineado' },
            { id: 'ac-sw-interletreado', prop: 'interletreado' },
            { id: 'ac-sw-texto-izq', prop: 'textoIzquierda' },
            { id: 'ac-sw-enlaces', prop: 'resaltarEnlaces' },
            { id: 'ac-sw-titulos', prop: 'resaltarTitulos' },
            { id: 'ac-sw-animaciones', prop: 'sinAnimaciones' },
            { id: 'ac-sw-cursor', prop: 'cursorGrande' },
            { id: 'ac-sw-focus', prop: 'focusVisible' },
            { id: 'ac-sw-guia', prop: 'guiaLectura' },
            { id: 'ac-sw-lector', prop: 'lectorVoz' }
        ];

        switches.forEach(sw => {
            const el = document.getElementById(sw.id);
            if (el) {
                el.checked = !!config[sw.prop];
            }
        });

        actualizarBadgeContador();
    }

    /**
     * Muestra la cantidad de ajustes activos en el botón flotante
     */
    function actualizarBadgeContador() {
        const badge = document.getElementById('ac-badge-count');
        if (!badge) return;

        let activos = 0;
        if (config.contraste !== 'normal') activos++;
        if (config.fuenteTamano !== 100) activos++;
        if (config.tipografia !== 'default') activos++;
        if (config.interlineado) activos++;
        if (config.interletreado) activos++;
        if (config.textoIzquierda) activos++;
        if (config.resaltarEnlaces) activos++;
        if (config.resaltarTitulos) activos++;
        if (config.sinAnimaciones) activos++;
        if (config.cursorGrande) activos++;
        if (config.focusVisible) activos++;
        if (config.guiaLectura) activos++;
        if (config.lectorVoz) activos++;

        if (activos > 0) {
            badge.textContent = activos;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }

    /**
     * HISTORIA 1: Control de Contraste y Colores
     */
    function setContraste(modo) {
        config.contraste = modo;
        aplicarConfiguracion();
        anunciarAccesibilidad(`Contraste cambiado a modo ${modo}`);
    }

    /**
     * HISTORIA 2: Control de Tamaño de Fuente y Tipografía
     */
    const ESCALA_FUENTE = [90, 100, 115, 130, 150];

    function aumentarFuente() {
        const idx = ESCALA_FUENTE.indexOf(config.fuenteTamano);
        if (idx < ESCALA_FUENTE.length - 1) {
            config.fuenteTamano = ESCALA_FUENTE[idx + 1];
            aplicarConfiguracion();
            anunciarAccesibilidad(`Tamaño de fuente aumentado a ${config.fuenteTamano} por ciento`);
        }
    }

    function disminuirFuente() {
        const idx = ESCALA_FUENTE.indexOf(config.fuenteTamano);
        if (idx > 0) {
            config.fuenteTamano = ESCALA_FUENTE[idx - 1];
            aplicarConfiguracion();
            anunciarAccesibilidad(`Tamaño de fuente reducido a ${config.fuenteTamano} por ciento`);
        }
    }

    function setTipografia(tipo) {
        config.tipografia = tipo;
        aplicarConfiguracion();
        anunciarAccesibilidad(`Tipografía cambiada a ${tipo}`);
    }

    /**
     * HISTORIA 3: Herramientas Transversales - Lector Text-to-Speech
     */
    function leerTexto(texto, elemento) {
        if (!speechSynth) {
            alert('Tu navegador no soporta síntesis de voz.');
            return;
        }

        detenerVoz();

        if (!texto || texto.trim() === '') return;

        currentUtterance = new SpeechSynthesisUtterance(texto.trim());
        currentUtterance.lang = 'es-CO';
        currentUtterance.rate = 1.0;

        // Intentar voz en español disponible
        const voces = speechSynth.getVoices();
        const vozEs = voces.find(v => v.lang.startsWith('es'));
        if (vozEs) currentUtterance.voice = vozEs;

        if (elemento) {
            if (elementReading) elementReading.classList.remove('ac-speaking-now');
            elementReading = elemento;
            elementReading.classList.add('ac-speaking-now');
        }

        currentUtterance.onend = function () {
            if (elementReading) {
                elementReading.classList.remove('ac-speaking-now');
                elementReading = null;
            }
        };

        currentUtterance.onerror = function () {
            if (elementReading) {
                elementReading.classList.remove('ac-speaking-now');
                elementReading = null;
            }
        };

        speechSynth.speak(currentUtterance);
    }

    function pausarReanudarVoz() {
        if (!speechSynth) return;
        if (speechSynth.speaking) {
            if (speechSynth.paused) {
                speechSynth.resume();
            } else {
                speechSynth.pause();
            }
        }
    }

    function detenerVoz() {
        if (!speechSynth) return;
        speechSynth.cancel();
        if (elementReading) {
            elementReading.classList.remove('ac-speaking-now');
            elementReading = null;
        }
    }

    /**
     * HISTORIA 3: Guía de lectura interactiva (sigue el cursor)
     */
    function inicializarGuiaLectura() {
        const guia = document.getElementById('ac-reading-guide');
        if (!guia) return;

        window.addEventListener('mousemove', function (e) {
            if (config.guiaLectura) {
                guia.style.top = `${e.clientY}px`;
            }
        }, { passive: true });

        window.addEventListener('touchmove', function (e) {
            if (config.guiaLectura && e.touches.length > 0) {
                guia.style.top = `${e.touches[0].clientY}px`;
            }
        }, { passive: true });
    }

    /**
     * HISTORIA 4: Abrir y Cerrar Panel Modal / Drawer
     */
    function abrirModal() {
        const overlay = document.getElementById('ac-modal-overlay');
        const trigger = document.getElementById('ac-trigger-btn');
        if (overlay) {
            overlay.classList.add('open');
            overlay.setAttribute('aria-hidden', 'false');
            if (trigger) trigger.setAttribute('aria-expanded', 'true');

            // Enfocar el primer botón interactivo del panel
            const closeBtn = overlay.querySelector('.ac-close-btn');
            if (closeBtn) closeBtn.focus();
        }
        anunciarAccesibilidad('Panel de accesibilidad abierto');
    }

    function cerrarModal() {
        const overlay = document.getElementById('ac-modal-overlay');
        const trigger = document.getElementById('ac-trigger-btn');
        if (overlay) {
            overlay.classList.remove('open');
            overlay.setAttribute('aria-hidden', 'true');
            if (trigger) {
                trigger.setAttribute('aria-expanded', 'false');
                trigger.focus();
            }
        }
        anunciarAccesibilidad('Panel de accesibilidad cerrado');
    }

    /**
     * Restablecer todos los ajustes por defecto
     */
    function restablecerTodo() {
        detenerVoz();
        config = Object.assign({}, DEFAULT_CONFIG);
        aplicarConfiguracion();
        anunciarAccesibilidad('Se han restablecido todas las opciones de accesibilidad a sus valores originales.');
    }

    /**
     * Event Listeners e Inicialización
     */
    function inicializarEventos() {
        // Botón flotante para abrir panel
        const trigger = document.getElementById('ac-trigger-btn');
        if (trigger) {
            trigger.addEventListener('click', abrirModal);
        }

        // Botón cerrar y clic fuera
        const closeBtn = document.getElementById('ac-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', cerrarModal);
        }

        const overlay = document.getElementById('ac-modal-overlay');
        if (overlay) {
            overlay.addEventListener('click', function (e) {
                if (e.target === overlay) {
                    cerrarModal();
                }
            });
        }

        // Atajo de teclado: Escape para cerrar, Alt + A para abrir/cerrar
        window.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && overlay && overlay.classList.contains('open')) {
                cerrarModal();
            }
            // Alt + A (o Option + A)
            if (e.altKey && (e.key === 'a' || e.key === 'A')) {
                e.preventDefault();
                if (overlay && overlay.classList.contains('open')) {
                    cerrarModal();
                } else {
                    abrirModal();
                }
            }
        });

        // Controles de contraste
        document.querySelectorAll('[data-ac-contraste]').forEach(btn => {
            btn.addEventListener('click', function () {
                const modo = this.getAttribute('data-ac-contraste');
                setContraste(modo);
            });
        });

        // Controles de tamaño de fuente
        const btnFontPlus = document.getElementById('ac-font-increase');
        if (btnFontPlus) btnFontPlus.addEventListener('click', aumentarFuente);

        const btnFontMinus = document.getElementById('ac-font-decrease');
        if (btnFontMinus) btnFontMinus.addEventListener('click', disminuirFuente);

        // Controles de tipografía
        document.querySelectorAll('[data-ac-tipografia]').forEach(btn => {
            btn.addEventListener('click', function () {
                const tipo = this.getAttribute('data-ac-tipografia');
                setTipografia(tipo);
            });
        });

        // Switches de opciones transversales y espaciado
        const bindSwitch = (id, prop, nombreLegible) => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', function () {
                    config[prop] = this.checked;
                    aplicarConfiguracion();
                    anunciarAccesibilidad(`${nombreLegible} ${this.checked ? 'activado' : 'desactivado'}`);
                });
            }
        };

        bindSwitch('ac-sw-interlineado', 'interlineado', 'Interlineado amplio');
        bindSwitch('ac-sw-interletreado', 'interletreado', 'Espaciado entre letras');
        bindSwitch('ac-sw-texto-izq', 'textoIzquierda', 'Alineación a la izquierda');
        bindSwitch('ac-sw-enlaces', 'resaltarEnlaces', 'Resaltado de enlaces');
        bindSwitch('ac-sw-titulos', 'resaltarTitulos', 'Resaltado de encabezados');
        bindSwitch('ac-sw-animaciones', 'sinAnimaciones', 'Detener animaciones');
        bindSwitch('ac-sw-cursor', 'cursorGrande', 'Cursor de alta visibilidad');
        bindSwitch('ac-sw-focus', 'focusVisible', 'Enfoque visual resaltado');
        bindSwitch('ac-sw-guia', 'guiaLectura', 'Guía de lectura');
        bindSwitch('ac-sw-lector', 'lectorVoz', 'Lector de texto a voz');

        // Botón Restablecer
        const resetBtn = document.getElementById('ac-reset-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', restablecerTodo);
        }

        // Lector de voz interactivo al hacer click en el documento
        document.addEventListener('click', function (e) {
            if (!config.lectorVoz) return;

            // Ignorar clics dentro del panel de accesibilidad o la barra de voz
            if (e.target.closest('#ac-modal-overlay') || e.target.closest('#ac-trigger-btn') || e.target.closest('#ac-speech-bar')) {
                return;
            }

            // Detectar elemento de texto
            const textElement = e.target.closest('p, h1, h2, h3, h4, h5, h6, li, label, .card-text, .alert, blockquote, span, a');
            if (textElement) {
                const text = textElement.innerText || textElement.textContent;
                leerTexto(text, textElement);
            }
        });

        // Botones de la barra de control de voz flotante
        const btnVozPausa = document.getElementById('ac-speech-pause');
        if (btnVozPausa) {
            btnVozPausa.addEventListener('click', pausarReanudarVoz);
        }

        const btnVozStop = document.getElementById('ac-speech-stop');
        if (btnVozStop) {
            btnVozStop.addEventListener('click', detenerVoz);
        }

        const btnVozClose = document.getElementById('ac-speech-close');
        if (btnVozClose) {
            btnVozClose.addEventListener('click', function () {
                config.lectorVoz = false;
                aplicarConfiguracion();
            });
        }

        inicializarGuiaLectura();
    }

    // Inicializar al cargar el DOM
    cargarConfiguracion();
    aplicarConfiguracion();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializarEventos);
    } else {
        inicializarEventos();
    }

    // Exponer API global opcional
    window.MascottAccesibilidad = {
        config: config,
        abrir: abrirModal,
        cerrar: cerrarModal,
        restablecer: restablecerTodo,
        leerTexto: leerTexto,
        detenerVoz: detenerVoz
    };
})();
