import os

file_path = "c:/Users/david/Desktop/Github VE Bistro/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Inject custom CSS
custom_css = """
        .hide-on-mobile { display: block; }
        @media (max-width: 639px) {
            .hide-on-mobile { display: none !important; }
        }
"""
if "hide-on-mobile" not in content:
    content = content.replace("</style>", custom_css + "\n    </style>")

# 2. Update JavaScript Modal parser to strip this new class
if "hide-on-mobile" not in content.split("openProductModal")[1]:
    content = content.replace(
        "htmlDesc = htmlDesc.replace(/hidden md:block/g, '').replace(/hidden sm:block/g, 'block').replace(/hidden sm:inline/g, 'inline');",
        "htmlDesc = htmlDesc.replace(/hide-on-mobile/g, '').replace(/hidden md:block/g, '').replace(/hidden sm:block/g, 'block').replace(/hidden sm:inline/g, 'inline');"
    )

# 3. Update the Translation Strings
content = content.replace("hidden sm:block", "hide-on-mobile")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Forced hide on mobile applied perfectly!")
