# Escribir sin sonar a IA

Erik Jurri · octubre de 2026

Este repositorio guarda un documento para que la IA (Claude, ChatGPT, Gemini) escriba sin sus estructuras típicas: el «no es X, es Y», las frases que anuncian algo y no lo dicen, las tres palabras en fila, las aperturas y cierres de plantilla y otros 100 patrones más, cada uno con su reescritura de antes y después.

## Qué hay

- `01-documento-maestro.md` y `Documento-Maestro-Escritura-sin-IA.pdf`. El documento completo, de unas 39.000 palabras. La parte 0 explica cómo usarlo, la parte 1 le dice a la IA cómo escribir, las partes 2 a 6 son el catálogo de patrones y la parte 7 trae las versiones para pegar. El anexo explica por qué la IA escribe así y de qué fuentes sale.
- `02-versiones-para-pegar.md` y `Versiones-para-pegar.pdf`. Las cuatro versiones de la parte 7, sueltas para copiarlas.
- `pagina/escribir-sin-sonar-a-ia.html`. El documento entero en una sola página, con índice y un botón para copiar cada versión. Se abre con doble clic en cualquier navegador.
- `herramientas/`. El revisor automático de patrones (`lint.py`), el generador de PDF (`md2pdf.py`) y el generador de la página (`gen_pagina.py`).

## Cómo usarlo con una IA

La IA no necesita el documento entero. Basta con esto:

1. Pega la versión **compacta** (1.677 palabras) en las instrucciones de un proyecto de Claude o de ChatGPT, de un Gem o del `CLAUDE.md` de Claude Code. Si el campo tiene límite de caracteres, como las instrucciones personalizadas de la cuenta de ChatGPT, usa la **mínima** (1.391 caracteres).
2. En conversaciones largas, pega de vez en cuando el **recordatorio de una línea**.
3. Antes de publicar o enviar un texto, abre un chat nuevo y pásalo por el **prompt de corrector**.

En cuatro rondas de pruebas a ciegas, la compacta dejó más o menos la mitad de los patrones que deja la IA sin instrucciones, y con la pasada del corrector se quedó en un tercio.

## El revisor automático

`lint.py` busca en un texto los patrones que se pueden detectar con reglas. Necesita Python 3 y nada más:

```
python herramientas/lint.py mi-texto.md
```

Avisa de lo que parece un patrón para que lo revise una persona; no corrige nada por sí solo.

Para regenerar los PDF hace falta `pip install reportlab`, y el script usa las fuentes de Windows (`C:\Windows\Fonts`). Para regenerar la página hace falta `pip install markdown`. En Git Bash, pon delante `PYTHONIOENCODING=utf-8` para que los acentos salgan bien en la consola.

## Compartir

Puedes compartir este documento y pasárselo a cualquier IA. Si lo cambias, cita la fuente.
