import re
import os

file_path = "c:/Users/david/Desktop/Github VE Bistro/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Hero Section Fixes
content = content.replace('text-4xl md:text-6xl font-bold mb-4', 'text-2xl sm:text-4xl md:text-6xl font-bold mb-3 sm:mb-4')
content = content.replace('text-5xl sm:text-7xl lg:text-8xl', 'text-4xl sm:text-6xl lg:text-8xl')
content = content.replace('text-sm md:text-base w-full sm:w-auto', 'text-xs md:text-base w-full sm:w-auto mt-2')
content = content.replace('bg-white/10 p-1.5 rounded-full', 'bg-white/10 p-1 rounded-full')

# 2. History Section Fixes
content = content.replace('py-12 sm:py-16 bg-white', 'py-6 sm:py-16 bg-white')
content = content.replace('text-4xl sm:text-5xl md:text-6xl font-black', 'text-2xl sm:text-4xl md:text-6xl font-black')
content = content.replace('h-56 sm:h-72 md:h-[450px]', 'h-48 sm:h-72 md:h-[450px]')
content = content.replace('p-6 sm:p-8 md:p-14', 'p-4 sm:p-8 md:p-14')
content = content.replace('text-base sm:text-lg md:text-xl', 'text-[11px] sm:text-base md:text-xl')
content = content.replace('pt-8 mt-10 border-t', 'pt-4 mt-6 border-t')
content = content.replace('w-12 h-12', 'w-10 h-10')
content = content.replace('text-base sm:text-xl font-black', 'text-sm sm:text-xl font-black')

# 3. Category Tabs (Visual + Sticky)
sticky_container = '<div class="flex justify-start sm:justify-center gap-4 sm:gap-6 mb-8 sm:mb-10 overflow-x-auto py-3 px-4 scrollbar-hide sticky top-[3rem] z-40 bg-[#fcfcfc]/95 backdrop-blur-md border-b border-gray-200">'
content = content.replace('<div class="flex justify-start sm:justify-center gap-2 sm:gap-3 mb-8 sm:mb-10 overflow-x-auto py-2 px-1 sm:px-4 scrollbar-hide">', sticky_container)

old_tab_css = """.category-tab.active {
            background-color: var(--venezuela-red);
            color: white;
            box-shadow: 0 4px 6px -1px rgba(207, 20, 43, 0.4);
            transform: scale(1.05);
        }"""
new_tab_css = """.category-tab.active {
            color: var(--venezuela-red);
            border-bottom: 3px solid var(--venezuela-red);
        }"""
content = content.replace(old_tab_css, new_tab_css)

old_tab_hover = ".category-tab:not(.active):hover { background-color: #e5e7eb; }"
new_tab_hover = ".category-tab { border-bottom: 3px solid transparent; border-radius: 0; padding-bottom: 0.5rem; transition: none; }\n        .category-tab:not(.active):hover { color: #333; }"
content = content.replace(old_tab_hover, new_tab_hover)

content = content.replace('px-3 sm:px-6 py-2.5 sm:py-2 rounded-full font-bold text-xs sm:text-sm shadow-sm', 'px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent')
content = content.replace('bg-gray-200 text-gray-700 shadow-sm', 'text-gray-400')
content = content.replace('class="category-tab active whitespace-nowrap px-3 sm:px-6 py-2.5 sm:py-2 rounded-full font-bold text-xs sm:text-sm shadow-sm"', 'class="category-tab active px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent"')

# 4. Product Cards
content = content.replace('class="bg-white rounded-2xl overflow-hidden shadow-md card-hover group flex flex-col', 'class="bg-white rounded-xl sm:rounded-2xl overflow-hidden shadow-sm sm:shadow-md card-hover group flex flex-row sm:flex-col border border-gray-100 sm:border-transparent p-2 sm:p-0 gap-3 sm:gap-0')

# Card image container
content = content.replace('h-56 sm:h-64 bg-gray-100 flex items-center justify-center relative overflow-hidden flex-shrink-0', 'w-[100px] sm:w-full h-auto sm:h-64 bg-gray-100 flex items-center justify-center relative overflow-hidden flex-shrink-0 rounded-lg sm:rounded-none object-cover min-h-[100px]')
content = content.replace('class="product-img-container"', 'class="product-img-container w-full h-full"')
content = content.replace('class="product-img"', 'class="product-img w-full h-full object-cover"')

# For Combos that have slightly different classes:
content = content.replace('class="bg-white rounded-2xl overflow-hidden shadow-md card-hover group flex flex-col border-2 border-ven-red"', 'class="bg-white rounded-xl sm:rounded-2xl overflow-hidden shadow-sm sm:shadow-md card-hover group flex flex-row sm:flex-col border border-ven-red sm:border-2 border-ven-red p-2 sm:p-0 gap-3 sm:gap-0 relative"')
content = content.replace('class="bg-white rounded-2xl overflow-hidden shadow-md card-hover group flex flex-col border-2 border-ven-blue"', 'class="bg-white rounded-xl sm:rounded-2xl overflow-hidden shadow-sm sm:shadow-md card-hover group flex flex-row sm:flex-col border border-ven-blue sm:border-2 border-ven-blue p-2 sm:p-0 gap-3 sm:gap-0 relative"')
content = content.replace('class="bg-white rounded-2xl overflow-hidden shadow-md card-hover group flex flex-col border-2 border-ven-yellow"', 'class="bg-white rounded-xl sm:rounded-2xl overflow-hidden shadow-sm sm:shadow-md card-hover group flex flex-row sm:flex-col border border-ven-yellow sm:border-2 border-ven-yellow p-2 sm:p-0 gap-3 sm:gap-0 relative"')


# Card info container
content = content.replace('class="p-5 sm:p-6 flex flex-col flex-grow"', 'class="py-1 pr-1 sm:p-6 flex flex-col flex-grow w-[calc(100%-110px)] sm:w-full"')
content = content.replace('class="flex justify-between items-start mb-2 gap-2"', 'class="flex justify-between items-start mb-1 sm:mb-2 gap-2 flex-col sm:flex-row"')
content = content.replace('class="flex justify-between items-start mb-2 gap-2 sm:gap-0"', 'class="flex justify-between items-start mb-1 sm:mb-2 gap-2 flex-col sm:flex-row sm:gap-0"')
content = content.replace('font-bold text-lg sm:text-xl text-gray-800 pr-1', 'font-bold text-[13px] leading-tight sm:text-xl text-gray-800 pr-1')

# Price
content = content.replace('text-ven-red font-bold text-base sm:text-lg', 'text-ven-red font-bold text-sm sm:text-lg')

# Line-clamp for descriptions
content = content.replace('class="text-gray-500 text-xs sm:text-sm mb-3 sm:mb-4 flex-grow"', 'class="text-gray-500 text-[10px] sm:text-sm mb-2 sm:mb-4 flex-grow line-clamp-2 h-[30px] sm:h-auto overflow-hidden"')

# Rewrite buttons to redirect to modal on mobile
old_btn = '<button class="add-to-cart w-full bg-gray-900 text-white py-2.5 sm:py-3 rounded-lg sm:rounded-xl font-bold hover:bg-ven-red transition-colors flex justify-center items-center gap-2 mt-auto text-xs sm:text-sm"'
new_btn = '<button class="hidden sm:flex add-to-cart w-full bg-gray-900 text-white py-2.5 sm:py-3 rounded-lg sm:rounded-xl font-bold hover:bg-ven-red transition-colors justify-center items-center gap-2 mt-auto text-xs sm:text-sm"'
content = content.replace(old_btn, new_btn)
old_btn2 = '<button class="add-to-cart w-full bg-ven-red text-white py-2.5 sm:py-3 rounded-lg sm:rounded-xl font-bold hover:bg-gray-900 transition-colors flex justify-center items-center gap-2 mt-auto text-xs sm:text-sm"'
new_btn2 = '<button class="hidden sm:flex add-to-cart w-full bg-ven-red text-white py-2.5 sm:py-3 rounded-lg sm:rounded-xl font-bold hover:bg-gray-900 transition-colors justify-center items-center gap-2 mt-auto text-xs sm:text-sm"'
content = content.replace(old_btn2, new_btn2)

old_btn3 = '<button class="add-to-cart w-full bg-ven-blue text-white py-2.5 sm:py-3 rounded-lg sm:rounded-xl font-bold hover:bg-gray-900 transition-colors flex justify-center items-center gap-2 mt-auto text-xs sm:text-sm"'
new_btn3 = '<button class="hidden sm:flex add-to-cart w-full bg-ven-blue text-white py-2.5 sm:py-3 rounded-lg sm:rounded-xl font-bold hover:bg-gray-900 transition-colors justify-center items-center gap-2 mt-auto text-xs sm:text-sm"'
content = content.replace(old_btn3, new_btn3)

end_tag = '</i> <span data-i18n="btn_add">Adicionar</span>\n                            </button>'
# Ensure we do a re sub just in case of spaces
content = content.replace(end_tag, '</i> <span data-i18n="btn_add">Adicionar</span>\n                            </button>\n                            <button class="sm:hidden text-ven-red text-[11px] font-bold mt-auto uppercase tracking-wide flex justify-end items-center gap-1 active:opacity-70 mt-2" onclick="openProductModal(this)">Ver detalhes <i data-lucide="chevron-right" class="w-3 h-3"></i></button>')

# For combos it might be slightly different layout if it includes info
content = content.replace('R$ 35,90</span>\n                                </div>\n                            </div>', 'R$ 35,90</span>\n                                </div>\n                            </div>\n                                <div class="sm:hidden w-full text-right mt-1"><span class="text-gray-400 font-medium text-[10px]">De: R$ 75,00</span></div>')

# Hide portions on mobile since they take space
content = content.replace('class="portion-tag mb-3 sm:mb-4 w-max"', 'class="portion-tag hidden sm:inline-block mb-3 sm:mb-4 w-max"')


# Modal Addition
modal_html = """
    <!-- Modal do Produto -->
    <div id="product-detail-modal" class="fixed inset-0 z-[120] flex items-end sm:items-center justify-center hidden" style="opacity:0; transition: opacity 0.3s ease;">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm modal-bg" onclick="closeProductModal()"></div>
        <div class="bg-white rounded-t-3xl sm:rounded-2xl w-full sm:max-w-md mx-0 sm:mx-4 relative z-10 shadow-2xl flex flex-col h-[85vh] sm:max-h-[85vh] transform translate-y-full sm:translate-y-0 transition-transform duration-300 ease-out" id="modal-content-panel">
            
            <button onclick="closeProductModal()" class="absolute top-4 right-4 bg-white/80 backdrop-blur-md text-gray-800 hover:text-red-500 rounded-full p-2 z-20 shadow-sm">
                <i data-lucide="x" class="w-5 h-5"></i>
            </button>

            <!-- Detalhes Scrolláveis -->
            <div class="overflow-y-auto flex-grow rounded-t-3xl">
                <!-- Imagem -->
                <div class="w-full h-64 sm:h-64 relative bg-gray-100">
                    <img id="modal-img" src="" class="w-full h-full object-cover">
                    <!-- Sombra gradiente -->
                    <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                </div>

                <div class="p-5 sm:p-6 bg-white relative z-10 rounded-t-3xl -mt-6">
                    <h3 id="modal-title" class="text-2xl font-black text-ven-blue mb-1 leading-tight">Produto</h3>
                    <span id="modal-portion" class="inline-block bg-yellow-50 text-gray-600 text-[10px] font-bold px-3 py-1 rounded-full w-max mb-6">Rende: 1 pessoa</span>
                    
                    <div class="flex justify-between items-center bg-gray-50 border border-gray-100 p-3 rounded-xl mb-6">
                        <span class="text-gray-500 text-xs font-bold uppercase tracking-widest">Valor</span>
                        <span id="modal-price" class="text-ven-red font-black text-xl whitespace-nowrap">R$ 0,00</span>
                    </div>

                    <h4 class="text-gray-400 font-bold text-[10px] uppercase tracking-widest mb-3">Ingredientes & Detalhes</h4>
                    <div id="modal-desc" class="text-gray-600 text-sm leading-relaxed mb-6 font-medium">Descrição...</div>
                </div>
            </div>

            <!-- Rodapé / Ações -->
            <div class="border-t border-gray-100 p-4 sm:p-5 bg-white flex flex-col gap-4 flex-shrink-0 shadow-[0_-10px_20px_rgba(0,0,0,0.05)]">
                <div class="flex flex-row items-center justify-between">
                    <div class="flex items-center gap-3">
                        <button onclick="updateModalQuantity(-1)" class="w-12 h-12 flex items-center justify-center bg-gray-100 text-gray-600 hover:text-black rounded-full active:scale-95 text-2xl font-normal transition">-</button>
                        <span id="modal-qty" class="w-6 text-center font-black text-xl text-gray-900">1</span>
                        <button onclick="updateModalQuantity(1)" class="w-12 h-12 flex items-center justify-center bg-gray-100 text-gray-600 hover:text-black rounded-full active:scale-95 text-2xl font-normal transition">+</button>
                    </div>
                    
                    <button id="modal-add-btn" class="bg-ven-red text-white h-12 px-6 rounded-full font-black text-sm shadow-xl hover:bg-[#b01020] active:scale-95 transition-transform flex items-center gap-2">
                        <span>Adicionar Pedido</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
"""

modal_js = """
// Modal Logic Setup
let pModalActive = null;
let pModalQty = 1;

window.openProductModal = function(btn) {
    const card = btn.closest('.bg-white');
    const title = card.querySelector('h4').innerText;
    
    // Find price text
    let priceText = "R$ 0,00";
    const priceNodesEl = card.querySelectorAll('.text-ven-red.font-bold, .text-ven-blue.font-bold');
    if(priceNodesEl.length > 0) {
        priceText = priceNodesEl[priceNodesEl.length - 1].innerText;
    }
    const rawPrice = parseFloat(priceText.replace('R$', '').replace(',', '.').trim());

    // Image, Description, Portion
    const imgEl = card.querySelector('img');
    const descEl = card.querySelector('p, div.text-gray-500'); // the description block
    const portionEl = card.querySelector('.portion-tag');

    document.getElementById('modal-img').src = imgEl.src;
    document.getElementById('modal-title').innerText = title;
    document.getElementById('modal-price').innerText = 'R$ ' + rawPrice.toFixed(2).replace('.', ',');
    
    // Some logic to extract pure HTML text, but removing line-clamp dynamically
    let htmlDesc = descEl ? descEl.innerHTML : '';
    document.getElementById('modal-desc').innerHTML = htmlDesc;
    
    if(portionEl) {
        document.getElementById('modal-portion').innerText = portionEl.innerText;
        document.getElementById('modal-portion').style.display = 'inline-block';
    } else {
        document.getElementById('modal-portion').style.display = 'none';
    }

    pModalActive = { title: title, basePrice: rawPrice };
    pModalQty = 1;
    document.getElementById('modal-qty').innerText = '1';

    // Open Modal
    const modal = document.getElementById('product-detail-modal');
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.style.opacity = '1';
        document.getElementById('modal-content-panel').classList.remove('translate-y-full');
    }, 10);
};

window.closeProductModal = function() {
    const modal = document.getElementById('product-detail-modal');
    modal.style.opacity = '0';
    document.getElementById('modal-content-panel').classList.add('translate-y-full');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
};

window.updateModalQuantity = function(change) {
    if (pModalQty + change >= 1) {
        pModalQty += change;
        document.getElementById('modal-qty').innerText = pModalQty;
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const addBtn = document.getElementById('modal-add-btn');
    if(addBtn) {
        addBtn.addEventListener('click', function() {
            if(pModalActive && window.addToCart) {
                for(let i=0; i<pModalQty; i++) {
                    window.addToCart(pModalActive.title, pModalActive.basePrice);
                }
                closeProductModal();
                // We add a toast inside addToCart to be visible ideally.
            }
        });
    }
});
"""

# Inject before script
content = content.replace('<script>', modal_html + '<script>\n' + modal_js + '\n')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("UI successfully refactored!")
