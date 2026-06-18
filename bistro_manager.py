import re
import os
from bs4 import BeautifulSoup

def toggle_product_stock(file_path, product_name, make_out_of_stock):
    """Toggles stock status of a product (grayscale overlay, button disabled/enabled)."""
    if not os.path.exists(file_path):
        print(f"[-] File not found: {file_path}")
        return False
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    found = False

    # Find h4 tags which contain product names
    h4s = soup.find_all('h4')
    for h4 in h4s:
        h4_text = h4.get_text().strip().lower()
        target_normalized = product_name.strip().lower()
        
        # Locate the card wrapper (div with classes 'bg-white' and 'rounded-xl')
        wrapper = h4.parent
        while wrapper and not (wrapper.name == 'div' and wrapper.get('class') and 'bg-white' in wrapper.get('class') and any('rounded-xl' in c or 'rounded-2xl' in c for c in wrapper.get('class'))):
            wrapper = wrapper.parent
            
        if not wrapper:
            continue
            
        # Check if card matches by h4 text or img alt
        matches = False
        if h4_text == target_normalized:
            matches = True
        else:
            img = wrapper.find('img')
            if img and img.get('alt', '').strip().lower() == target_normalized:
                matches = True
                
        if matches:
            found = True
            classes = wrapper.get('class', [])
            
            if make_out_of_stock:
                # 1. Update card classes
                if 'card-hover' in classes:
                    classes.remove('card-hover')
                for c in ['opacity-60', 'grayscale', 'pointer-events-none']:
                    if c not in classes:
                        classes.append(c)
                wrapper['class'] = classes
                
                # 2. Add Esgotado badge inside product-img-container
                img_container = wrapper.find(class_='product-img-container')
                if img_container:
                    badge = img_container.find('span', attrs={"data-i18n": "out_of_stock_tag"})
                    if not badge:
                        badge_html = (
                            '<div class="absolute inset-0 bg-black/50 z-20 flex items-center justify-center backdrop-blur-[2px]">'
                            '<span class="text-white font-black px-3 py-1 bg-red-600 border border-red-800 rounded shadow-lg transform -rotate-12 text-[10px] sm:text-xs" data-i18n="out_of_stock_tag">'
                            'Esgotado / Agotado'
                            '</span>'
                            '</div>'
                        )
                        badge_soup = BeautifulSoup(badge_html, 'html.parser')
                        img_container.append(badge_soup)
                
                # 3. Disable button
                btn = wrapper.find('button', class_='add-to-cart')
                if btn:
                    btn_classes = btn.get('class', [])
                    if 'bg-gray-900' in btn_classes:
                        btn_classes.remove('bg-gray-900')
                    btn_classes = [c for c in btn_classes if not c.startswith('hover:')]
                    if 'bg-gray-400' not in btn_classes:
                        btn_classes.append('bg-gray-400')
                    btn['class'] = btn_classes
                    btn['onclick'] = 'return false;'
                    
                    span = btn.find('span', attrs={"data-i18n": "btn_add"})
                    if span:
                        span.string = 'Indisponível'
            else:
                # Make IN stock
                # 1. Update card classes
                if 'card-hover' not in classes:
                    classes.append('card-hover')
                for c in ['opacity-60', 'grayscale', 'pointer-events-none']:
                    if c in classes:
                        classes.remove(c)
                wrapper['class'] = classes
                
                # 2. Remove Esgotado badge
                img_container = wrapper.find(class_='product-img-container')
                if img_container:
                    badge_span = img_container.find('span', attrs={"data-i18n": "out_of_stock_tag"})
                    if badge_span:
                        badge_parent = badge_span.parent
                        badge_parent.decompose()
                
                # 3. Enable button
                btn = wrapper.find('button', class_='add-to-cart')
                if btn:
                    btn_classes = btn.get('class', [])
                    if 'bg-gray-400' in btn_classes:
                        btn_classes.remove('bg-gray-400')
                    if 'bg-gray-900' not in btn_classes:
                        btn_classes.append('bg-gray-900')
                    if 'hover:bg-ven-red' not in btn_classes:
                        btn_classes.append('hover:bg-ven-red')
                    btn['class'] = btn_classes
                    
                    # Extract price from span
                    price = 0
                    price_span = wrapper.find('span', class_='text-ven-red')
                    if price_span:
                        price_text = price_span.get_text()
                        digits = re.findall(r'\d+', price_text)
                        if digits:
                            price = int(digits[0])
                            
                    btn['onclick'] = f"addToCart('{h4.get_text().strip()}', {price})"
                    
                    span = btn.find('span', attrs={"data-i18n": "btn_add"})
                    if span:
                        span.string = 'Adicionar'
            break

    if found:
        # Write back without changing HTML structure/entities
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
    return found


def update_schedule_hours(file_path, new_hours_pt, new_hours_es, new_hours_html):
    """Updates operating hours in HTML elements and translations script."""
    if not os.path.exists(file_path):
        print(f"[-] File not found: {file_path}")
        return False
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    
    # 1. Update raw HTML info_hours_val
    hours_els = soup.find_all(attrs={"data-i18n": "info_hours_val"})
    for el in hours_els:
        el.string = new_hours_html
        
    content_updated = str(soup)

    # 2. Update JS translations block
    # Structure has two matches: first is Spanish, second is Portuguese
    matches = list(re.finditer(r'(info_hours_val\s*:\s*["\'])(.*?)(["\'])', content_updated))
    if len(matches) >= 2:
        # Process from back to front to preserve indices
        # Match 1 (pt)
        start1, end1 = matches[1].span(2)
        content_updated = content_updated[:start1] + new_hours_pt + content_updated[end1:]
        
        # Re-evaluate match 0 since string changed but only after it, so indices of match 0 are still correct
        start0, end0 = matches[0].span(2)
        content_updated = content_updated[:start0] + new_hours_es + content_updated[end0:]
    else:
        print("[-] Could not find two info_hours_val instances in Javascript translations.")
        return False

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content_updated)
        
    return True


def add_new_product(file_path, slug, name_pt, name_es, desc_pt, desc_es, price, category, image_filename):
    """Appends a new product card to the specified section grid and registers its translations."""
    if not os.path.exists(file_path):
        print(f"[-] File not found: {file_path}")
        return False
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 1: Update JS translations dictionary
    # We will search for: pwa_install_btn: "Descargar Aplicación" (es)
    # and: pwa_install_btn: "Baixar Aplicativo" (pt)
    # and append our new translations right after them.
    
    name_key = f"name_{slug}"
    desc_key = f"desc_{slug}"
    
    es_replacement = (
        f'pwa_install_btn: "Descargar Aplicación",\n'
        f'                {name_key}: "{name_es}",\n'
        f'                {desc_key}: "{desc_es}"'
    )
    
    pt_replacement = (
        f'pwa_install_btn: "Baixar Aplicativo",\n'
        f'                {name_key}: "{name_pt}",\n'
        f'                {desc_key}: "{desc_pt}"'
    )
    
    # Apply translations replacement
    content_updated = re.sub(r'pwa_install_btn\s*:\s*"Descargar Aplicación",?', es_replacement, content)
    content_updated = re.sub(r'pwa_install_btn\s*:\s*"Baixar Aplicativo",?', pt_replacement, content_updated)
    
    # Step 2: Inject card into HTML section using BeautifulSoup
    soup = BeautifulSoup(content_updated, 'html.parser')
    
    section_id = f"{category}-section"
    section = soup.find(id=section_id)
    if not section:
        print(f"[-] Could not find section with ID: {section_id}")
        return False
        
    price_formatted = f"{price:.2f}".replace('.', ',')
    price_int = int(price)
    
    card_html = f"""
<!-- Item: {name_pt} -->
<div class="bg-white rounded-xl sm:rounded-2xl overflow-hidden shadow-sm sm:shadow-md card-hover group flex flex-row sm:flex-col border border-gray-100 sm:border-transparent p-2 sm:p-0 gap-3 sm:gap-0">
<div class="w-[100px] sm:w-full h-auto sm:h-64 bg-gray-100 flex items-center justify-center relative overflow-hidden flex-shrink-0 rounded-lg sm:rounded-none object-cover min-h-[100px]">
<div class="product-img-container w-full h-full">
<img loading="lazy" alt="{name_pt}" class="product-img w-full h-full object-cover" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1615719413546-198b25453f85?ixlib=rb-1.2.1&amp;auto=format&amp;fit=crop&amp;w=800&amp;q=80';" src="{image_filename}"/>
</div>
</div>
<div class="py-1 pr-1 sm:p-6 flex flex-col flex-grow w-[calc(100%-110px)] sm:w-full">
<div class="flex justify-between items-start mb-1 sm:mb-2 gap-2 flex-col sm:flex-row">
<h4 class="font-bold text-[13px] leading-tight sm:text-xl text-gray-800 pr-1" data-i18n="{name_key}">{name_pt}</h4>
<span class="text-ven-red font-bold text-sm sm:text-lg whitespace-nowrap flex-shrink-0 ml-1">R$ {price_formatted}</span>
</div>
<p class="text-gray-500 text-[10px] sm:text-sm mb-2 sm:mb-4 flex-grow line-clamp-2 h-[30px] sm:h-auto overflow-hidden" data-i18n="{desc_key}">{desc_pt}</p>
<span class="portion-tag hidden sm:inline-block mb-3 sm:mb-4 w-max" data-i18n="rend_300">Rende: 1 pessoa (300g)</span>
<button class="hidden sm:flex add-to-cart w-full bg-gray-900 text-white py-2.5 sm:py-3 rounded-lg sm:rounded-xl font-bold hover:bg-ven-red transition-colors justify-center items-center gap-2 mt-auto text-xs sm:text-sm" onclick="addToCart('{name_pt}', {price_int})">
<i class="w-4 h-4" data-lucide="plus-circle"></i> <span data-i18n="btn_add">Adicionar</span>
</button>
<button class="sm:hidden text-ven-red text-[11px] font-bold mt-auto uppercase tracking-wide flex justify-end items-center gap-1 active:opacity-70 mt-2 pointer-events-none">Ver detalhes <i class="w-3 h-3" data-lucide="chevron-right"></i></button>
</div>
</div>
"""
    
    card_soup = BeautifulSoup(card_html, 'html.parser')
    section.append(card_soup)
    
    # Save back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
        
    return True


def get_all_product_names(file_path):
    """Parses index.html to dynamically fetch all product names in the menu."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'html.parser')
    h4s = soup.find_all('h4')
    product_names = []
    for h4 in h4s:
        # Verify it resides inside a card wrapper
        wrapper = h4.parent
        while wrapper and not (wrapper.name == 'div' and wrapper.get('class') and 'bg-white' in wrapper.get('class') and any('rounded-xl' in c or 'rounded-2xl' in c for c in wrapper.get('class'))):
            wrapper = wrapper.parent
        if wrapper:
            product_names.append(h4.get_text().strip())
    return sorted(list(set(product_names)))
