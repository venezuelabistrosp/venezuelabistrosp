import re

file_path = "c:/Users/david/Desktop/Github VE Bistro/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    orig = f.read()

content = orig

# Menu Tabs literal replacement
tab_start = content.find('<div class="flex justify-start sm:justify-center')
tab_end = content.find('<!-- Grid de Itens -->')

if tab_start != -1 and tab_end != -1:
    before_tab = content[:tab_start]
    after_tab = content[tab_end:]
    
    # recreate the tab container
    # find the end of the opening div tag
    div_end_idx = content.find('>', tab_start) + 1
    opener = content[tab_start:div_end_idx]
    
    new_tabs = opener + """
                <button class="category-tab active px-2 pb-2 font-bold text-[13px] sm:text-base whitespace-nowrap bg-transparent" data-category="combos" data-i18n="cat_combos">Combos & Promo</button>
                <button class="category-tab px-2 pb-2 font-bold text-[13px] sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="arepas">Arepas</button>
                <button class="category-tab px-2 pb-2 font-bold text-[13px] sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="cachapas" data-i18n="cat_cachapas">Cachapas</button>
                <button class="category-tab px-2 pb-2 font-bold text-[13px] sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="empanadas">Empanadas</button>
                <button class="category-tab px-2 pb-2 font-bold text-[13px] sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="tequenos" data-i18n="cat_tequenos">Tequeños</button>
                <button class="category-tab px-2 pb-2 font-bold text-[13px] sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="sobremesas" data-i18n="cat_sobremesas">Sobremesas</button>
                <button class="category-tab px-2 pb-2 font-bold text-[13px] sm:text-base whitespace-nowrap bg-transparent text-gray-400" data-category="bebidas" data-i18n="cat_drinks">Bebidas</button>
            </div>
            """
    content = before_tab + new_tabs + after_tab

# Menu Sections Reordering
# Manually split it up
menu_container_id = '<div id="menu-container">'
mc_idx = content.find(menu_container_id)
end_menu_section = content.find('</section>', mc_idx)

if mc_idx != -1 and end_menu_section != -1:
    pre_menu = content[:mc_idx + len(menu_container_id)]
    post_menu = content[end_menu_section:]
    
    # Current Sections extraction:
    # 1. Combos
    combos_start = content.find('<!-- SEÇÃO COMBOS -->', mc_idx)
    arepas_start = content.find('<!-- SEÇÃO AREPAS -->', mc_idx)
    empanadas_start = content.find('<!-- SEÇÃO EMPANADAS -->', mc_idx)
    cachapas_start = content.find('<!-- SEÇÃO CACHAPAS', mc_idx)
    tequenos_start = content.find('<!-- SEÇÃO TEQUEÑOS -->', mc_idx)
    bebidas_start = content.find('<!-- SEÇÃO BEBIDAS -->', mc_idx)
    
    # For bounds, assume the above order or use their indices
    starts = [(combos_start, "combos"), (arepas_start, "arepas"), (empanadas_start, "empanadas"), (cachapas_start, "cachapas"), (tequenos_start, "tequenos"), (bebidas_start, "bebidas")]
    starts.sort() # sorted by occurrence in file
    
    sections_map = {}
    for i in range(len(starts)):
        start_pos, name = starts[i]
        end_pos = starts[i+1][0] if i < len(starts)-1 else content.find('</div>', bebidas_start)
        
        # Grab exactly up to the end of the section
        if name == "bebidas":
            # Just go from bebidas to the end of the container div
            # The menu-container div has a closing </div> before </section>
            # Let's find the closing div of "bebidas-section"
            closing_div = content.find('</div>\n                </div>', bebidas_start) # nested grid
            if closing_div == -1: closing_div = content.find('</div>\n            </div>', bebidas_start)
            end_pos = closing_div + 6 # plus </div> 
            
        sections_map[name] = content[start_pos:end_pos]

    # Reassemble in order: Combos, Arepas, Cachapas, Empanadas, Tequeños, Sobremesas, Bebidas
    if len(sections_map) == 6:
        def set_hide(html, is_visible):
            # First clean any existing grid states
            if 'class="menu-section hidden grid ' in html:
                html = html.replace('class="menu-section hidden grid ', 'class="menu-section grid ')
            
            patt = re.compile(r'class="menu-section grid')
            if is_visible:
                # Should not have hidden
                return html
            else:
                return patt.sub('class="menu-section hidden grid', html)
            
        new_combos = set_hide(sections_map["combos"], True)
        new_arepas = set_hide(sections_map["arepas"], False)
        new_cachapas = set_hide(sections_map["cachapas"], False)
        new_empanadas = set_hide(sections_map["empanadas"], False)
        new_tequenos = set_hide(sections_map["tequenos"], False)
        new_bebidas = set_hide(sections_map["bebidas"], False)
        
        new_sobremesas = """\n                <!-- SEÇÃO SOBREMESAS -->
                <div id="sobremesas-section" class="menu-section hidden grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
                    <!-- Placeholder -->
                    <div class="w-full text-center text-gray-500 py-10 col-span-full">
                        Em breve deliciosas sobremesas venezuelanas!
                    </div>
                </div>\n                """
                
        # Ensure we don't duplicate closing tags and insert neatly
        assembled_menu = "\n" + new_combos + "\n" + new_arepas + "\n" + new_cachapas + "\n" + new_empanadas + "\n" + new_tequenos + new_sobremesas + new_bebidas + "\n            </div>\n        </div>\n    "
        
        content = pre_menu + assembled_menu + post_menu

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("UI successfully fixed and reordered.")
