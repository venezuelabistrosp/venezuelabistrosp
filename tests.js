(function() {
    console.log('[Test Suite] Initializing Venezuela Bistro SP test runner...');

    // 1. Back up original global objects and mocks
    // Access cart and currentLang directly as they are declared with 'let' in the script block
    const originalCart = typeof cart !== 'undefined' ? [...cart] : [];
    const originalLang = typeof currentLang !== 'undefined' ? currentLang : 'pt';
    const originalWindowOpen = window.open;
    const originalAlert = window.alert;
    const originalFetch = window.fetch;

    let lastOpenedUrl = null;
    let lastAlertMessage = null;
    let lastFetchCall = null;

    // Apply Mocks
    window.open = function(url, target) {
        lastOpenedUrl = url;
        return { close: () => {} };
    };
    window.alert = function(msg) {
        lastAlertMessage = msg;
        console.log('[Mock Alert]', msg);
    };
    window.fetch = function(url, options) {
        lastFetchCall = { url, options };
        return Promise.resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve({ status: 'success' })
        });
    };

    // 2. Inject Test Panel Styles
    const styleId = 'test-suite-styles';
    if (!document.getElementById(styleId)) {
        const style = document.createElement('style');
        style.id = styleId;
        style.innerHTML = `
            #test-runner-panel {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 360px;
                max-height: 480px;
                background: rgba(28, 25, 23, 0.95);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                color: #f3f4f6;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
                z-index: 99999;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                transition: transform 0.3s ease, opacity 0.3s ease;
            }
            #test-runner-header {
                padding: 12px 16px;
                background: rgba(255, 204, 0, 0.1);
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            #test-runner-header h3 {
                margin: 0;
                font-size: 14px;
                font-weight: 700;
                color: #ffcc00;
                letter-spacing: 0.5px;
            }
            #test-runner-summary {
                font-size: 11px;
                color: #9ca3af;
                margin-top: 2px;
            }
            #test-runner-close {
                background: none;
                border: none;
                color: #9ca3af;
                cursor: pointer;
                font-size: 16px;
                padding: 4px;
            }
            #test-runner-close:hover {
                color: #f3f4f6;
            }
            #test-runner-body {
                padding: 12px 16px;
                overflow-y: auto;
                flex-grow: 1;
            }
            .test-row {
                display: flex;
                align-items: flex-start;
                gap: 10px;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.03);
                font-size: 12px;
            }
            .test-row:last-child {
                border-bottom: none;
            }
            .test-status {
                font-weight: bold;
                flex-shrink: 0;
            }
            .test-status.pass {
                color: #10b981;
            }
            .test-status.fail {
                color: #ef4444;
            }
            .test-name {
                flex-grow: 1;
                line-height: 1.4;
            }
            .test-error {
                color: #fca5a5;
                font-size: 10px;
                margin-top: 4px;
                font-family: monospace;
                white-space: pre-wrap;
            }
            #test-runner-footer {
                padding: 10px 16px;
                background: rgba(0, 0, 0, 0.2);
                border-top: 1px solid rgba(255, 255, 255, 0.05);
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 11px;
            }
            .btn-test {
                background: #ffcc00;
                color: #1c1917;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 700;
                cursor: pointer;
            }
            .btn-test:hover {
                background: #e6b800;
            }
        `;
        document.head.appendChild(style);
    }

    // 3. Create UI Panel
    const panel = document.createElement('div');
    panel.id = 'test-runner-panel';
    panel.innerHTML = `
        <div id="test-runner-header">
            <div>
                <h3>🧪 VeneBistro Test Suite</h3>
                <div id="test-runner-summary">Executando testes...</div>
            </div>
            <button id="test-runner-close" onclick="document.getElementById('test-runner-panel').remove()">×</button>
        </div>
        <div id="test-runner-body"></div>
        <div id="test-runner-footer">
            <span id="test-time">Tempo: 0ms</span>
            <button class="btn-test" id="btn-re-run">Recarregar</button>
        </div>
    `;
    document.body.appendChild(panel);

    document.getElementById('btn-re-run').addEventListener('click', () => {
        window.location.reload();
    });

    const testBody = document.getElementById('test-runner-body');
    const summary = document.getElementById('test-runner-summary');
    const timeDisplay = document.getElementById('test-time');

    let passed = 0;
    let failed = 0;
    const startTime = performance.now();

    function addTestResult(name, success, errorMsg = '') {
        const row = document.createElement('div');
        row.className = 'test-row';
        row.innerHTML = `
            <span class="test-status ${success ? 'pass' : 'fail'}">${success ? '✔' : '✘'}</span>
            <div class="test-name">
                <div>${name}</div>
                ${errorMsg ? `<div class="test-error">${errorMsg}</div>` : ''}
            </div>
        `;
        testBody.appendChild(row);
        if (success) passed++;
        else failed++;
        
        summary.textContent = `Aprovados: ${passed} | Falhas: ${failed}`;
    }

    // 4. Run Test Cases
    try {
        if (typeof cart === 'undefined') {
            addTestResult("Acesso a Variável Global 'cart'", false, "A variável global 'cart' não está definida.");
            return;
        }

        // Clear cart for test isolation
        cart = [];
        if (typeof window.saveCartToStorage === 'function') window.saveCartToStorage();
        if (typeof window.updateCartUI === 'function') window.updateCartUI();

        // --- TEST 1: Cart starts empty ---
        const t1_cartEmpty = cart.length === 0;
        addTestResult("Cart Inicial Vazio", t1_cartEmpty, t1_cartEmpty ? '' : 'O carrinho não iniciou vazio.');

        // --- TEST 2: Add single product ---
        if (typeof window.addToCart === 'function') {
            window.addToCart("Arepa de Pabellón", 45.00);
            const t2_added = cart.length === 1 && cart[0].name === "Arepa de Pabellón" && cart[0].qty === 1;
            const t2_total = window.calculateSubtotal() === 45.00;
            addTestResult("Adicionar Item Único (Arepa de Pabellón)", t2_added && t2_total, 
                `Esperado: qty=1, total=45.00. Obtido: len=${cart.length}, qty=${cart[0]?.qty}, total=${window.calculateSubtotal()}`);
        } else {
            addTestResult("Adicionar Item Único", false, "Função addToCart no encontrada.");
        }

        // --- TEST 3: Add duplicate product (should increment quantity) ---
        if (typeof window.addToCart === 'function') {
            window.addToCart("Arepa de Pabellón", 45.00);
            const t3_added = cart.length === 1 && cart[0].qty === 2;
            const t3_total = window.calculateSubtotal() === 90.00;
            addTestResult("Acúmulo de Quantidade (Duplicados)", t3_added && t3_total, 
                `Esperado: len=1, qty=2, total=90.00. Obtido: len=${cart.length}, qty=${cart[0]?.qty}, total=${window.calculateSubtotal()}`);
        } else {
            addTestResult("Acúmulo de Quantidade", false, "Função addToCart no encontrada.");
        }

        // --- TEST 4: Modify Quantity and Remove Item ---
        if (typeof window.updateCartItemQuantity === 'function') {
            const itemId = cart[0].id;
            // increase to 3
            window.updateCartItemQuantity(itemId, 3);
            const t4_inc = cart[0].qty === 3 && window.calculateSubtotal() === 135.00;
            // decrease to 0 (remove)
            window.updateCartItemQuantity(itemId, 0);
            const t4_dec = cart.length === 0 && window.calculateSubtotal() === 0;
            
            addTestResult("Modificar Quantidade e Remoção (updateCartItemQuantity)", t4_inc && t4_dec, 
                `Erro na modificação. Incremento: ${t4_inc} (qty=${cart[0]?.qty}, total=${window.calculateSubtotal()}), Remoção: ${t4_dec} (len=${cart.length})`);
        } else {
            addTestResult("Modificar Quantidade e Remoção", false, "Função updateCartItemQuantity no encontrada.");
        }

        // --- TEST 5: Cart Calculation for Multiple Items ---
        if (typeof window.addToCart === 'function') {
            window.addToCart("Combo Llanero", 35.00);
            window.addToCart("Coca-Cola Lata Zero", 6.00);
            const t5_len = cart.length === 2;
            const t5_total = window.calculateSubtotal() === 41.00;
            addTestResult("Cálculo de Carrinho com Varios Items", t5_len && t5_total, 
                `Esperado: len=2, total=41.00. Obtido: len=${cart.length}, total=${window.calculateSubtotal()}`);
        } else {
            addTestResult("Cálculo com Varios Items", false, "addToCart no encontrada.");
        }

        // --- TEST 6: Form Validation on Checkout ---
        if (typeof window.submitCheckout === 'function') {
            // Backup form values
            const nameField = document.getElementById('chk-name');
            const phoneField = document.getElementById('chk-phone');
            const origName = nameField ? nameField.value : '';
            const origPhone = phoneField ? phoneField.value : '';

            // Force empty fields
            if (nameField) nameField.value = '';
            if (phoneField) phoneField.value = '';

            lastAlertMessage = null;
            window.submitCheckout();
            
            const t6_valName = lastAlertMessage !== null; // validation should trigger alert
            
            // Restore fields
            if (nameField) nameField.value = origName;
            if (phoneField) phoneField.value = origPhone;

            addTestResult("Validação de Campos del Formulario", t6_valName, "El checkout envió con campos vacíos o no validó correctamente el nombre.");
        } else {
            addTestResult("Validação de Campos del Formulario", false, "Função submitCheckout no encontrada.");
        }

        // --- TEST 7: WhatsApp Message Parsing and Delivery ---
        if (typeof window.submitCheckout === 'function') {
            // Set fields values
            const nameField = document.getElementById('chk-name');
            const phoneField = document.getElementById('chk-phone');
            const addressField = document.getElementById('chk-address');
            
            if (nameField) nameField.value = "David Test";
            if (phoneField) phoneField.value = "11999999999";
            if (addressField) addressField.value = "Rua Teste, 123";

            // Set orderType radio to Takeout (Balcão) to simplify
            const takeoutRadio = document.querySelector('input[name="orderType"][value="Balcão"]');
            if (takeoutRadio) {
                takeoutRadio.checked = true;
                if (typeof window.toggleDeliveryFields === 'function') window.toggleDeliveryFields();
            }

            lastOpenedUrl = null;
            window.submitCheckout();

            let t7_passed = false;
            let errorDetails = '';
            if (lastOpenedUrl) {
                const decodedUrl = decodeURIComponent(lastOpenedUrl);
                const hasCombo = decodedUrl.includes("1x Combo Llanero");
                const hasCoke = decodedUrl.includes("1x Coca-Cola Lata Zero");
                const hasTotal = decodedUrl.includes("Subtotal (Comida): R$ 41,00") || decodedUrl.includes("R$ 41,00");
                const hasClient = decodedUrl.includes("David Test");
                
                t7_passed = hasCombo && hasCoke && hasTotal && hasClient;
                if (!t7_passed) {
                    errorDetails = `URL generated incorrect: ${decodedUrl}\nMatch: Combo=${hasCombo}, Coke=${hasCoke}, Total=${hasTotal}, Client=${hasClient}`;
                }
            } else {
                errorDetails = "window.open no fue llamado durante el checkout.";
            }

            addTestResult("Generación y Formato de Mensaje de WhatsApp", t7_passed, errorDetails);
        } else {
            addTestResult("Generación y Formato de Mensaje de WhatsApp", false, "Função submitCheckout no encontrada.");
        }

    } catch (err) {
        console.error(err);
        addTestResult("Falha Fatal Execução de Teste", false, err.stack);
    } finally {
        // 5. Restore original objects so user's cart is unaffected
        if (typeof cart !== 'undefined') {
            cart = originalCart;
            if (typeof window.saveCartToStorage === 'function') window.saveCartToStorage();
            if (typeof window.updateCartUI === 'function') window.updateCartUI();
        }
        if (typeof currentLang !== 'undefined') {
            currentLang = originalLang;
        }
        window.open = originalWindowOpen;
        window.alert = originalAlert;
        window.fetch = originalFetch;

        const duration = Math.round(performance.now() - startTime);
        timeDisplay.textContent = `Tempo: ${duration}ms`;
        console.log(`[Test Suite] Completed in ${duration}ms. Passed: ${passed}, Failed: ${failed}`);
    }
})();
