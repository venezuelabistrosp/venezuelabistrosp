import re
import os

file_path = "c:/Users/david/Desktop/Github VE Bistro/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Hero Section Shrinking
# Badge
content = content.replace('font-bold text-sm mb-4', 'font-bold text-[10px] sm:text-sm mb-3')
# O Verdadeiro Sabor
content = content.replace('text-2xl sm:text-4xl md:text-6xl font-bold mb-3 sm:mb-4', 'text-xl sm:text-3xl md:text-6xl font-bold mb-2 sm:mb-4')
# Venezuelano (was taking space? Actually just the whole H2)
# Subtitle
content = content.replace('text-base md:text-lg text-gray-200 mb-8', 'text-[11px] md:text-lg text-gray-200 mb-4 sm:mb-8')
# Button Ver Cardapio
content = content.replace('py-3 px-8 rounded-full shadow-lg transform transition hover:scale-105 flex items-center justify-center gap-2 text-xs md:text-base w-full sm:w-auto mt-2', 'py-2 px-5 rounded-full shadow-lg transform transition hover:scale-105 flex items-center justify-center gap-2 text-[10px] md:text-base w-full sm:w-auto mt-1')

# Background height
content = content.replace('min-h-[60vh] md:min-h-[550px]', 'min-h-[40vh] md:min-h-[550px]')
content = content.replace('pt-28 pb-10 sm:pt-32', 'pt-20 pb-8 sm:pt-32')

# 2. History Section 
# Mais que comida
content = content.replace('text-2xl sm:text-4xl md:text-6xl font-black text-gray-900 leading-tight', 'text-lg sm:text-3xl md:text-6xl font-black text-gray-900 leading-tight')
# é cultura
content = content.replace('text-4xl sm:text-6xl lg:text-8xl inline-block mt-2', 'text-2xl sm:text-5xl lg:text-8xl inline-block mt-1 sm:mt-2')

# Carousel Slides padding and image height
content = content.replace('h-48 sm:h-72 md:h-[450px]', 'h-32 sm:h-72 md:h-[450px]')
content = content.replace('p-4 sm:p-8 md:p-14', 'p-3 sm:p-8 md:p-14')

# Slide Text headings
content = content.replace('text-2xl sm:text-3xl md:text-4xl font-black text-gray-900 mb-4 tracking-tight', 'text-sm sm:text-2xl md:text-4xl font-black text-gray-900 mb-2 sm:mb-4 tracking-tight')

# Slide text
content = content.replace('text-[11px] sm:text-base md:text-xl leading-relaxed font-medium', 'text-[9px] sm:text-base md:text-xl leading-normal font-medium')
content = content.replace('text-[11px] sm:text-base md:text-xl leading-relaxed mb-8', 'text-[9px] sm:text-base md:text-xl leading-normal mb-4 sm:mb-8')
content = content.replace('w-8 h-8 sm:w-10 sm:h-10 text-gray-100 rotate-180', 'w-4 h-4 sm:w-10 sm:h-10 text-gray-100 rotate-180')

# 3. Combo Cards lists
# Hide everything after the first sentence on mobile inside description
# Instead of complex HTML hiding, let's wrap the ul and the extra text in a span that is hidden on mobile: `hidden md:block`.
# But since the modal script copies HTML directly, we modify the modal JS to ALWAYS show it even if hidden class is there.
# Let's fix JS first:
old_modal_js = "let htmlDesc = descEl ? descEl.innerHTML : '';\n    document.getElementById('modal-desc').innerHTML = htmlDesc;"
new_modal_js = "let htmlDesc = descEl ? descEl.innerHTML : '';\n    // Remove Tailwind hidden classes so it shows in modal\n    htmlDesc = htmlDesc.replace(/hidden md:block/g, 'block').replace(/sm:hidden/g, 'hidden');\n    document.getElementById('modal-desc').innerHTML = htmlDesc;"
content = content.replace(old_modal_js, new_modal_js)

# Now wrap the extra text for Combo 1
combo1_search = "Uma seleção especial para você conhecer os sabores mais tradicionais da Venezuela em um único pedido.<br><br>\n                                <ul class='list-disc pl-4 space-y-1 text-left text-[11px] sm:text-xs'>"
combo1_replace = "Uma seleção especial para você conhecer os sabores mais tradicionais da Venezuela em um único pedido.\n                                <div class='hidden md:block mt-2'>\n                                <ul class='list-disc pl-4 space-y-1 text-left text-[11px] sm:text-xs'>"
content = content.replace(combo1_search, combo1_replace)
# Close the div at the end of ul
content = content.replace('<li><strong>1 Suco de rapadura com limão.</strong></li>\n                                </ul>\n                            </div>', '<li><strong>1 Suco de rapadura com limão.</strong></li>\n                                </ul></div>\n                            </div>')

# Combo 3
combo3_search = "A combinação perfeita para os amantes de queijo! 1 Cachapa tradicional com queijo derretido, 4 Tequeños douradinhos, 1 Suco de papelón com limão refrescante e nossa famosa Salsa Guasacaca."
combo3_replace = "A combinação perfeita para os amantes de queijo! <span class='hidden md:inline'>1 Cachapa tradicional com queijo derretido, 4 Tequeños douradinhos, 1 Suco de papelón com limão refrescante e nossa famosa Salsa Guasacaca.</span>"
content = content.replace(combo3_search, combo3_replace)

# Combo 4
combo4_search = "A verdadeira perdição! Uma cachapa rústica e suculenta, de milho super fresco, transbordando de queijo derretido, acompanhada do nosso crocante e irresistível cochino frito (porco frito). Tudo isso com um refrescante papelón com limão bem gelado e a nossa famosa salsa guasacaca. Prepare-se para uma explosão de sabores a cada mordida!"
combo4_replace = "A verdadeira perdição! Uma cachapa rústica e suculenta, de milho super fresco transbordando de queijo derretido.<span class='hidden md:inline'> Acompanhada do nosso crocante e irresistível cochino frito (porco frito). Tudo isso com um refrescante papelón com limão bem gelado e a nossa famosa salsa guasacaca. Prepare-se para uma explosão de sabores a cada mordida!</span>"
content = content.replace(combo4_search, combo4_replace)

# Combo 2
combo2_search = "Duas empanadas venezuelanas douradas e crocantes, carne e queijo. Acompanhadas de um refrescante papelón com limão 300 ml grátis. Uma combinação perfeita para conhecer os sabores tradicionais da Venezuela em um combo prático, saboroso e ideal para qualquer hora do dia. (Acompanha nosso molho tradicional guasacaca)."
combo2_replace = "Duas empanadas venezuelanas douradas e crocantes, carne e queijo. <span class='hidden md:inline'>Acompanhadas de um refrescante papelón com limão 300 ml grátis. Uma combinação perfeita para conhecer os sabores tradicionais da Venezuela em um combo prático, saboroso e ideal para qualquer hora do dia. (Acompanha nosso molho tradicional guasacaca).</span>"
content = content.replace(combo2_search, combo2_replace)

# Finally, ensure descriptions on regular cards are strictly 2 lines if possible
content = content.replace('line-clamp-2 h-[30px] sm:h-auto overflow-hidden', 'line-clamp-2 h-auto overflow-hidden')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Second UI pass applied successfully!")
