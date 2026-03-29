import re
import os

file_path = "c:/Users/david/Desktop/Github VE Bistro/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# --- 1. HERO SECTION ---
content = content.replace('font-bold text-[10px] sm:text-sm mb-3', 'font-bold text-[9px] sm:text-xs mb-2') # Just in case it was applied
content = content.replace('font-bold text-sm mb-4', 'font-bold text-[10px] sm:text-xs mb-2')
content = content.replace('text-2xl sm:text-4xl md:text-6xl font-bold mb-3 sm:mb-4', 'text-xl sm:text-3xl md:text-5xl font-bold mb-2')
content = content.replace('text-base md:text-lg text-gray-200 mb-8', 'text-[11px] md:text-base text-gray-200 mb-4 sm:mb-6')
content = content.replace('py-3 px-8 rounded-full shadow-lg transform transition hover:scale-105 flex items-center justify-center gap-2 text-xs md:text-base w-full sm:w-auto mt-2', 'py-2 px-6 rounded-full shadow-lg transform transition hover:scale-105 flex items-center justify-center gap-2 text-[10px] md:text-sm w-full sm:w-auto mt-1')
content = content.replace('min-h-[60vh] md:min-h-[550px]', 'min-h-[40vh] md:min-h-[500px]')
content = content.replace('pt-28 pb-10 sm:pt-32', 'pt-20 pb-8 sm:pt-28')

# --- 2. HISTORY SECTION ---
content = content.replace('text-2xl sm:text-4xl md:text-6xl font-black text-gray-900 leading-tight', 'text-lg sm:text-3xl md:text-5xl font-black text-gray-900 leading-tight')
content = content.replace('text-4xl sm:text-6xl lg:text-8xl inline-block mt-2', 'text-2xl sm:text-5xl lg:text-6xl inline-block mt-1')
content = content.replace('h-48 sm:h-72 md:h-[450px]', 'h-32 sm:h-64 md:h-[400px]')
content = content.replace('p-4 sm:p-8 md:p-14', 'p-3 sm:p-6 md:p-10')
content = content.replace('p-6 sm:p-8 md:p-14', 'p-3 sm:p-6 md:p-10') # original before my script
content = content.replace('text-2xl sm:text-3xl md:text-4xl font-black text-gray-900 mb-4 tracking-tight', 'text-base sm:text-2xl md:text-3xl font-black text-gray-900 mb-2 sm:mb-3 tracking-tight')
content = content.replace('text-[11px] sm:text-base md:text-xl leading-relaxed font-medium', 'text-[9px] sm:text-xs md:text-lg leading-snug font-medium')
content = content.replace('text-[11px] sm:text-base md:text-xl leading-relaxed mb-8', 'text-[9px] sm:text-xs md:text-lg leading-snug mb-4 sm:mb-6')

# --- 3. COMBO ITEMS ---
# Make the ul hidden on mobile for Combo 1
if "Uma seleção especial para você conhecer os sabores mais tradicionais da Venezuela em um único pedido." in content:
    # Combo 1
    content = content.replace('Uma seleção especial para você conhecer os sabores mais tradicionais da Venezuela em um único pedido.<br><br>\n                                <ul', 'Uma seleção especial para você conhecer os sabores mais tradicionais da Venezuela em um único pedido.\n                                <ul')
    content = content.replace("<ul class='list-disc pl-4 space-y-1 text-left text-[11px] sm:text-xs'>", "<ul class='hidden sm:block list-disc pl-4 space-y-1 text-left text-[11px] sm:text-xs mt-2'>")
    # Combo 2
    content = content.replace("Duas empanadas venezuelanas douradas e crocantes, carne e queijo. Acompanhadas de um refrescante papelón", "Duas empanadas venezuelanas douradas e crocantes, carne e queijo. <span class='hidden sm:inline'>Acompanhadas de um refrescante papelón")
    content = content.replace("molho tradicional guasacaca).", "molho tradicional guasacaca).</span>")
    # Combo 3
    content = content.replace("A combinação perfeita para os amantes de queijo! 1 Cachapa tradicional com queijo", "A combinação perfeita para os amantes de queijo! <span class='hidden sm:inline'>1 Cachapa tradicional com queijo")
    content = content.replace("famosa Salsa Guasacaca.", "famosa Salsa Guasacaca.</span>")
    # Combo 4
    content = content.replace("A verdadeira perdição! Uma cachapa rústica e suculenta, de milho super fresco, transbordando de queijo derretido, acompanhada do nosso crocante", "A verdadeira perdição! Uma cachapa rústica e suculenta, transbordando de queijo derretido. <span class='hidden sm:inline'>Acompanhada do nosso crocante")
    content = content.replace("cada mordida!", "cada mordida!</span>")

# Update JS to strip 'hidden' class when opening modal so full desc shows
old_modal_js = "let htmlDesc = descEl ? descEl.innerHTML : '';"
new_modal_js = "let htmlDesc = descEl ? descEl.innerHTML : '';\n    if(htmlDesc) htmlDesc = htmlDesc.replace(/hidden sm:block/g, 'block').replace(/hidden sm:inline/g, 'inline');"
content = content.replace(old_modal_js, new_modal_js)

# --- 4. MENU CATEGORY TAB REORDERING ---
# Replace tabs completely with the new order + new tab
old_tabs_html = """<button class="category-tab active px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent" data-category="combos" data-i18n="cat_combos">Combos & Promo</button>
                <button class="category-tab whitespace-nowrap px-3 sm:px-6 py-2.5 sm:py-2 rounded-full font-bold text-xs sm:text-sm text-gray-400" data-category="arepas">Arepas</button>
                <button class="category-tab whitespace-nowrap px-3 sm:px-6 py-2.5 sm:py-2 rounded-full font-bold text-xs sm:text-sm text-gray-400" data-category="empanadas">Empanadas</button>
                <button class="category-tab whitespace-nowrap px-3 sm:px-6 py-2.5 sm:py-2 rounded-full font-bold text-xs sm:text-sm text-gray-400" data-category="tequenos" data-i18n="cat_tequenos">Tequeños</button>
                <button class="category-tab whitespace-nowrap px-3 sm:px-6 py-2.5 sm:py-2 rounded-full font-bold text-xs sm:text-sm text-gray-400" data-category="cachapas" data-i18n="cat_cachapas">Cachapas</button>
                <button class="category-tab whitespace-nowrap px-3 sm:px-6 py-2.5 sm:py-2 rounded-full font-bold text-xs sm:text-sm text-gray-400" data-category="bebidas" data-i18n="cat_drinks">Bebidas</button>"""

# My previous script might have converted all of them to just `px-2 pb-2 font-bold...`
# Let's just use regex to replace all tabs
tabsContainerRegex = re.compile(r'(<div class="flex justify-start sm:justify-center[^>]+>)(.*?)(</div>\s*<!-- Grid de Itens -->)', re.DOTALL)

new_tabs = """
                <button class="category-tab active px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent" data-category="combos" data-i18n="cat_combos">Combos & Promo</button>
                <button class="category-tab px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="arepas">Arepas</button>
                <button class="category-tab px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="cachapas" data-i18n="cat_cachapas">Cachapas</button>
                <button class="category-tab px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="empanadas">Empanadas</button>
                <button class="category-tab px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="tequenos" data-i18n="cat_tequenos">Tequeños</button>
                <button class="category-tab px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="sobremesas" data-i18n="cat_sobremesas">Sobremesas Venezuelanas</button>
                <button class="category-tab px-2 pb-2 font-bold text-sm sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="bebidas" data-i18n="cat_drinks">Bebidas</button>
            """

content = tabsContainerRegex.sub(r'\1' + new_tabs + r'\3', content)

# --- 5. MENU SECTIONS REORDERING ---
# We split by '<!-- SEÇÃO '
# First we find where '<!-- SEÇÃO COMBOS -->' starts.
menu_start_idx = content.find('<!-- SEÇÃO COMBOS -->')
if menu_start_idx != -1:
    before_menu = content[:menu_start_idx]
    menu_content_and_after = content[menu_start_idx:]
    
    # Split by '<!-- SEÇÃO '
    parts = menu_content_and_after.split('<!-- SEÇÃO ')
    
    # Extract the after_menu part which is after the last section's closing div
    # Actually, all sections end when the <script> or something else starts, but wait, they are all inside <div id="menu-container">
    # The last section is Bebidas. It closes with </div>.
    # Let's extract sections cleanly by regex matching `<div id="[a-z]+-section"`
    
    combos_re = re.search(r'<!-- SEÇÃO COMBOS -->\s*<div id="combos-section".*?(?=<!-- SEÇÃO AREPAS -->|<!-- SEÇÃO EMPANADAS -->|<!-- SEÇÃO CACHAPAS -->|<!-- SEÇÃO TEQUEÑOS -->|<!-- SEÇÃO BEBIDAS -->|<\/div>\s*<\/section>)', menu_content_and_after, re.DOTALL)
    arepas_re = re.search(r'<!-- SEÇÃO AREPAS -->\s*<div id="arepas-section".*?(?=<!-- SEÇÃO EMPANADAS -->|<!-- SEÇÃO CACHAPAS -->|<!-- SEÇÃO TEQUEÑOS -->|<!-- SEÇÃO BEBIDAS -->|<!-- SEÇÃO COMO -->|<\/div>\s*<\/section>)', menu_content_and_after, re.DOTALL)
    empanadas_re = re.search(r'<!-- SEÇÃO EMPANADAS -->\s*<div id="empanadas-section".*?(?=<!-- SEÇÃO AREPAS -->|<!-- SEÇÃO CACHAPAS -->|<!-- SEÇÃO TEQUEÑOS -->|<!-- SEÇÃO BEBIDAS -->|<!-- SEÇÃO COMO -->|<\/div>\s*<\/section>)', menu_content_and_after, re.DOTALL)
    cachapas_re = re.search(r'<!-- SEÇÃO CACHAPAS( (RÚSTICAS))? -->\s*<div id="cachapas-section".*?(?=<!-- SEÇÃO AREPAS -->|<!-- SEÇÃO EMPANADAS -->|<!-- SEÇÃO TEQUEÑOS -->|<!-- SEÇÃO BEBIDAS -->|<!-- SEÇÃO COMO -->|<\/div>\s*<\/section>)', menu_content_and_after, re.DOTALL)
    tequenos_re = re.search(r'<!-- SEÇÃO TEQUEÑOS -->\s*<div id="tequenos-section".*?(?=<!-- SEÇÃO AREPAS -->|<!-- SEÇÃO EMPANADAS -->|<!-- SEÇÃO CACHAPAS -->|<!-- SEÇÃO BEBIDAS -->|<!-- SEÇÃO COMO -->|<\/div>\s*<\/section>)', menu_content_and_after, re.DOTALL)
    bebidas_re = re.search(r'<!-- SEÇÃO BEBIDAS -->\s*<div id="bebidas-section".*?(?=<!-- SEÇÃO AREPAS -->|<!-- SEÇÃO EMPANADAS -->|<!-- SEÇÃO CACHAPAS -->|<!-- SEÇÃO TEQUEÑOS -->|<!-- SEÇÃO COMO -->|<\/div>\s*<!-- Final do Grid -->|<\/div>\s*<\/section>)', menu_content_and_after, re.DOTALL)
    
    if all([combos_re, arepas_re, empanadas_re, cachapas_re, tequenos_re, bebidas_re]):
        combos = combos_re.group(0)
        arepas = arepas_re.group(0)
        empanadas = empanadas_re.group(0)
        cachapas = cachapas_re.group(0)
        tequenos = tequenos_re.group(0)
        bebidas = bebidas_re.group(0)
        
        # We need to construct the new menu
        # Create a new Sobremesas section just empty for now
        sobremesas = """<!-- SEÇÃO SOBREMESAS -->
                <div id="sobremesas-section" class="menu-section hidden grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
                    <!-- Placeholder -->
                    <div class="w-full text-center text-gray-500 py-10 col-span-full">
                        Em breve deliciosas sobremesas venezuelanas!
                    </div>
                </div>
                """
        
        new_menu = "\n" + combos + "\n" + arepas + "\n" + cachapas + "\n" + empanadas + "\n" + tequenos + "\n" + sobremesas + "\n" + bebidas + "\n"
        
        # Before we substitute, replace the whole block in the file
        start = menu_content_and_after.find('<!-- SEÇÃO COMBOS -->')
        end = menu_content_and_after.find('</div>\n        </div>\n    </section>')
        if end == -1: end = menu_content_and_after.find('</section>') # fallback
        
        if start != -1 and end != -1:
            # We must just be careful to not cut too little or much
            # Let's reconstruct using regex sub:
            # Actually, easiest is to just write the new sections in the right order.
            # But the original sections might have the `hidden` class incorrectly set if we just move them.
            # Let's ensure combos doesn't have `hidden` and the rest do!
            
            def add_hidden(html):
                if 'class="menu-section grid' in html:
                    return html.replace('class="menu-section grid', 'class="menu-section hidden grid')
                return html
                
            def remove_hidden(html):
                return html.replace('class="menu-section hidden grid', 'class="menu-section grid')
                
            combos = remove_hidden(combos)
            arepas = add_hidden(arepas)
            empanadas = add_hidden(empanadas)
            cachapas = add_hidden(cachapas)
            tequenos = add_hidden(tequenos)
            bebidas = add_hidden(bebidas)
            
            new_menu = "\n" + combos + "\n" + arepas + "\n" + cachapas + "\n" + empanadas + "\n" + tequenos + "\n" + sobremesas + "\n" + bebidas + "\n"
            
            menu_html_regex = re.compile(r'<!-- SEÇÃO COMBOS -->.*?(?=</div>\s*<!-- Final do grid|\s*</section>\s*<!-- App Banner)', re.DOTALL)
            content = menu_html_regex.sub(lambda m: new_menu, content)
            
            # Since the structure is:
            # <div id="menu-container">
            #    <!-- SEÇÃO COMBOS -->...
            # </div>
            # </section>
            # Let's ensure we didn't wipe the closing div. The lookahead (?=<\/div>\s*<\/section>) helps.

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Menu reordered and UI fixed!")
