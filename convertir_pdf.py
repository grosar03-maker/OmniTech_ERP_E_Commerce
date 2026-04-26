"""
Script para convertir la documentación de Stripe a PDF
"""

import markdown
from pathlib import Path

# Leer el markdown
md_file = Path("DOCUMENTACION_STRIPE.md")
html_file = Path("DOCUMENTACION_STRIPE.html")

contenido = md_file.read_text(encoding='utf-8')

# Convertir a HTML con extensiones para tablas y código
html_content = markdown.markdown(
    contenido,
    extensions=['tables', 'fenced_code', 'codehilite']
)

# HTML completo con estilos para impresión
html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Documentación Stripe - OmniTech</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
            color: #333;
        }}
        h1 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #764ba2;
            margin-top: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
        }}
        pre {{
            background: #1a1a2e;
            color: #fff;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }}
        pre code {{
            background: transparent;
            color: #fff;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .note {{
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 10px 15px;
            margin: 15px 0;
        }}
        @media print {{
            body {{
                padding: 20px;
            }}
            pre {{
                background: #f4f4f4;
                color: #333;
            }}
            pre code {{
                color: #333;
            }}
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

# Guardar HTML
html_file.write_text(html_completo, encoding='utf-8')
print(f"HTML guardado en: {html_file.absolute()}")

# Instrucciones para convertir a PDF
print("\n" + "="*60)
print("INSTRUCCIONES PARA CONVERTIR A PDF:")
print("="*60)
print("1. Abre el archivo HTML generado:")
print(f"   {html_file.absolute()}")
print("\n2. Presiona Ctrl+P (o Cmd+P en Mac)")
print("\n3. Selecciona 'Guardar como PDF'")
print("\n4. Ajusta los márgenes a 'Ninguno' o 'Mínimo'")
print("="*60)
