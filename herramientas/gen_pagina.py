# -*- coding: utf-8 -*-
"""Genera la página para compartir a partir de 01-documento-maestro.md.
Uso: python herramientas/gen_pagina.py   (desde la carpeta raíz del repositorio)
Salida: pagina/escribir-sin-sonar-a-ia.html
"""
import html
import os
import re

import markdown

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(BASE, '01-documento-maestro.md'), encoding='utf-8').read().replace('\r\n', '\n')

# quitar título y línea de autor: van en la cabecera de la página
src = re.sub(r'\A# [^\n]*\n\n[^\n]*\n\n', '', src)


def slug(value, separator='-'):
    v = value.lower()
    for a, b in (('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ü', 'u'), ('ñ', 'n')):
        v = v.replace(a, b)
    v = re.sub(r'[^a-z0-9]+', separator, v).strip(separator)
    return v


md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'],
                       extension_configs={'toc': {'slugify': slug, 'toc_depth': '2-3'}})
body = md.convert(src)
toc_tokens = md.toc_tokens

# bloques para copiar
n = [0]


def bloque(m):
    n[0] += 1
    code = m.group(1)
    return (f'<div class="pegar"><div class="pegar-barra"><span class="pegar-etq">Texto para pegar</span>'
            f'<button type="button" class="copiar" data-objetivo="b{n[0]}">Copiar</button></div>'
            f'<pre id="b{n[0]}" tabindex="0">{code}</pre></div>')


body = re.sub(r'<pre><code>(.*?)</code></pre>', bloque, body, flags=re.S)
# tablas: envoltorio con scroll y clase para las de antes y después
body = re.sub(r'<table>\s*<thead>\s*<tr>\s*<th>Antes</th>', '<table class="ab"><thead><tr><th>Antes</th>', body)
body = re.sub(r'(<table.*?</table>)', r'<div class="tabla">\1</div>', body, flags=re.S)
# marca de párrafo para enlazar cada encabezado
body = re.sub(r'<(h[23]) id="([^"]+)">(.*?)</\1>',
              lambda m: f'<{m.group(1)} id="{m.group(2)}">{m.group(3)} <a class="ancla" href="#{m.group(2)}" aria-label="Enlace a esta sección">¶</a></{m.group(1)}>',
              body)


def indice(tokens):
    out = ['<ol class="indice-partes">']
    for t in tokens:
        out.append(f'<li><a href="#{t["id"]}">{html.escape(t["name"])}</a>')
        if t.get('children'):
            out.append('<ol>')
            for c in t['children']:
                out.append(f'<li><a href="#{c["id"]}">{html.escape(c["name"])}</a></li>')
            out.append('</ol>')
        out.append('</li>')
    out.append('</ol>')
    return '\n'.join(out)


toc_html = indice(toc_tokens)
ids = {t['name']: t['id'] for t in toc_tokens}
for t in toc_tokens:
    for c in t.get('children', []):
        ids[c['name']] = c['id']
id_compacta = next((v for k, v in ids.items() if k.startswith('7.1')), 'parte-7')
id_corrector = next((v for k, v in ids.items() if k.startswith('7.4')), 'parte-7')
id_minima = next((v for k, v in ids.items() if k.startswith('7.2')), 'parte-7')
id_catalogo = next((v for k, v in ids.items() if k.startswith('Parte 2')), 'parte-2')
id_probo = next((v for k, v in ids.items() if k.startswith('Cómo se probó')), 'anexo')
palabras = len(src.split())

CSS = r"""
/* Layout: columna de lectura de unas 68 letras con el índice fijo a la izquierda en pantallas anchas; en el móvil el índice se pliega encima del texto */
:root{
  --papel:#f5f6f8; --tinta:#1b212a; --suave:#3a4350; --linea:#d7dbe1; --panel:#ffffff;
  --lapiz:#b2332b; --antes:#fbefed; --despues:#edf4f0; --codigo:#eef0f3;
  --f-texto:"Literata", Georgia, "Times New Roman", serif;
  --f-ui:"Work Sans", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --f-mono:"IBM Plex Mono", Consolas, "Courier New", monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --papel:#121419; --tinta:#e8eaee; --suave:#c6ccd5; --linea:#2c3139; --panel:#1a1d23;
  --lapiz:#f0837a; --antes:#2b1e1e; --despues:#17251f; --codigo:#1f232a; color-scheme:dark } }
:root[data-theme="dark"]{
  --papel:#121419; --tinta:#e8eaee; --suave:#c6ccd5; --linea:#2c3139; --panel:#1a1d23;
  --lapiz:#f0837a; --antes:#2b1e1e; --despues:#17251f; --codigo:#1f232a; color-scheme:dark }
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
body{background:var(--papel);color:var(--tinta);font-family:var(--f-texto);font-size:17px;line-height:1.62;padding-inline:16px;padding-block:0 48px}
a{color:var(--lapiz)}
a:focus-visible,button:focus-visible,pre:focus-visible,summary:focus-visible{outline:2px solid var(--lapiz);outline-offset:2px}
.cabecera{max-width:1180px;margin:0 auto;padding-block:40px 28px;border-bottom:1px solid var(--linea)}
.cabecera .sobre{font-family:var(--f-ui);font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--suave);margin:0 0 12px}
.cabecera h1{font-size:clamp(30px,5vw,48px);line-height:1.12;margin:0 0 14px;text-wrap:balance;max-width:22ch}
.cabecera .autor{font-family:var(--f-ui);font-size:15px;color:var(--suave);margin:0 0 22px}
.uso{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;max-width:1180px}
.uso div{background:var(--panel);border:1px solid var(--linea);border-radius:6px;padding:16px 18px;min-width:0}
.uso h2{font-family:var(--f-ui);font-size:15px;font-weight:600;margin:0 0 6px}
.uso p{margin:0;font-size:15.5px;line-height:1.55}
.marco{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:270px minmax(0,1fr);gap:48px;padding-top:32px}
nav.indice{position:sticky;top:env(safe-area-inset-top,0px);align-self:start;max-height:100vh;overflow:auto;padding:8px 4px 24px 0;font-family:var(--f-ui);font-size:14px;line-height:1.4}
nav.indice summary{font-weight:600;cursor:pointer;margin-bottom:10px;list-style:none}
nav.indice ol{list-style:none;margin:0;padding:0}
.indice-partes>li{margin:0 0 10px}
.indice-partes>li>a{font-weight:600;color:var(--tinta);text-decoration:none}
.indice-partes ol{margin:4px 0 0 0;padding-left:10px;border-left:1px solid var(--linea)}
.indice-partes ol a{color:var(--suave);text-decoration:none;display:block;padding:2px 0 2px 8px}
nav.indice a:hover{color:var(--lapiz)}
main{min-width:0;max-width:72ch}
main h2{font-size:30px;line-height:1.2;margin:56px 0 16px;padding-top:18px;border-top:2px solid var(--tinta);text-wrap:balance}
main h2:first-child{margin-top:0}
main h3{font-size:21px;line-height:1.3;margin:38px 0 10px;text-wrap:balance}
main h4{font-family:var(--f-ui);font-size:13px;letter-spacing:.07em;text-transform:uppercase;color:var(--lapiz);margin:26px 0 8px}
main p,main li{hyphens:auto}
main ul,main ol{padding-left:1.3em}
main li{margin:0 0 6px}
.ancla{font-family:var(--f-ui);font-weight:400;font-size:.7em;color:var(--suave);text-decoration:none;opacity:0;margin-left:4px}
h2:hover .ancla,h3:hover .ancla,.ancla:focus{opacity:1}
blockquote{margin:18px 0;padding:10px 16px;background:var(--panel);border-left:3px solid var(--linea)}
.tabla{overflow-x:auto;margin:18px 0 22px;border:1px solid var(--linea);border-radius:6px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:15.5px;line-height:1.5}
th,td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid var(--linea)}
th{font-family:var(--f-ui);font-size:13px;letter-spacing:.05em;text-transform:uppercase;background:var(--codigo)}
tr:last-child td{border-bottom:0}
table.ab td:first-child{background:var(--antes);text-decoration:underline wavy var(--lapiz);text-decoration-thickness:1px;text-underline-offset:4px;width:42%}
table.ab td:nth-child(2){background:var(--despues)}
code{font-family:var(--f-mono);font-size:.88em;background:var(--codigo);padding:1px 4px;border-radius:3px}
.pegar{margin:16px 0 26px;border:1px solid var(--linea);border-radius:6px;background:var(--panel);min-width:0}
.pegar-barra{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 10px 8px 14px;border-bottom:1px solid var(--linea);font-family:var(--f-ui);font-size:13px}
.pegar-etq{color:var(--suave);letter-spacing:.05em;text-transform:uppercase}
button.copiar{font-family:var(--f-ui);font-size:14px;font-weight:600;color:var(--panel);background:var(--lapiz);border:0;border-radius:4px;padding:7px 14px;cursor:pointer}
button.copiar:hover{filter:brightness(1.08)}
.pegar pre{margin:0;padding:14px 16px;max-height:420px;overflow:auto;white-space:pre-wrap;word-break:break-word;font-family:var(--f-texto);font-size:15px;line-height:1.55;background:var(--codigo)}
.pie{max-width:1180px;margin:56px auto 0;padding-top:18px;border-top:1px solid var(--linea);font-family:var(--f-ui);font-size:14px;color:var(--suave)}
@media (max-width: 900px){
  .marco{grid-template-columns:minmax(0,1fr);gap:8px;padding-top:20px}
  nav.indice{position:static;max-height:none;padding:0;border:1px solid var(--linea);border-radius:6px;background:var(--panel)}
  nav.indice details{padding:12px 14px}
  nav.indice summary{margin:0}
  nav.indice details[open] summary{margin-bottom:12px}
  main h2{font-size:25px}
  body{font-size:16.5px}
}
"""

JS = r"""
(function(){
  var ancho = window.matchMedia('(min-width: 901px)');
  var det = document.getElementById('indice-det');
  function ajustar(){ if (det) det.open = ancho.matches; }
  ajustar();
  if (ancho.addEventListener) ancho.addEventListener('change', ajustar);
  document.querySelectorAll('button.copiar').forEach(function(b){
    b.addEventListener('click', function(){
      var pre = document.getElementById(b.getAttribute('data-objetivo'));
      var texto = pre.innerText;
      function hecho(msg){ var t = b.textContent; b.textContent = msg; setTimeout(function(){ b.textContent = 'Copiar'; }, 1800); }
      function seleccionar(){ var r = document.createRange(); r.selectNodeContents(pre); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); hecho('Seleccionado: pulsa Ctrl+C'); }
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(texto).then(function(){ hecho('Copiado'); }, seleccionar);
        } else { seleccionar(); }
      } catch (e) { seleccionar(); }
    });
  });
})();
"""

pagina = f"""<title>Escribir sin sonar a IA</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,600;7..72,700&family=Work+Sans:wght@400;600&family=IBM+Plex+Mono&display=swap">
<style>{CSS}</style>
<header class="cabecera">
  <p class="sobre">Documento maestro · {palabras:,} palabras</p>
  <h1>Documento maestro para eliminar las estructuras de comunicación de la IA</h1>
  <p class="autor">Erik Jurri · octubre de 2026</p>
  <div class="uso">
    <div><h2>Para tu IA</h2><p>Copia la <a href="#{id_compacta}">versión compacta</a> en las instrucciones de un proyecto de Claude o de ChatGPT, de un Gem o del CLAUDE.md. Donde haya poco espacio, usa la <a href="#{id_minima}">mínima</a>.</p></div>
    <div><h2>Antes de publicar</h2><p>Abre un chat nuevo y pasa el texto por el <a href="#{id_corrector}">prompt de corrector</a>. Lee la nota que deja debajo antes de copiar el texto.</p></div>
    <div><h2>Para ti</h2><p>El <a href="#{id_catalogo}">catálogo</a> explica cada patrón con ejemplos de antes y después, y el anexo cuenta <a href="#{id_probo}">cómo se probó</a> el documento.</p></div>
  </div>
</header>
<div class="marco">
  <nav class="indice" aria-label="Índice"><details id="indice-det" open><summary>Índice</summary>
{toc_html}
  </details></nav>
  <main>
{body}
  </main>
</div>
<footer class="pie">Erik Jurri · octubre de 2026. Puedes compartir este documento y pasárselo a cualquier IA.</footer>
<script>{JS}</script>
""".replace(f'{palabras:,}', f'{palabras:,}'.replace(',', '.'))

out = os.path.join(BASE, 'pagina', 'escribir-sin-sonar-a-ia.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w', encoding='utf-8').write(pagina)
print('página:', out, len(pagina), 'caracteres;', n[0], 'bloques para copiar;', palabras, 'palabras')
