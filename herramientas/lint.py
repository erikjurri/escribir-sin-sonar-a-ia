# -*- coding: utf-8 -*-
"""Señala formas sospechosas de escritura de IA en un markdown en español.

Uso:
  py -3 lint.py archivo.md              prosa fuera de «» y de los bloques de código
  py -3 lint.py archivo.md --despues    solo la columna «Después» de las tablas Antes | Después (comillas incluidas)
  py -3 lint.py archivo.md --codigo     solo los bloques de código (las versiones para pegar), fuera de «»
  py -3 lint.py archivo.md --todo       todo, comillas incluidas

Cada aviso se revisa a mano. Muchos son falsos positivos (un «más que» comparativo, una lista de tres que
son tres cosas). El objetivo es no dejar pasar ninguna forma sin mirarla.
"""
import re
import sys

PATS = [
    # contraste por negación y su familia
    ("contraste", r"\bno es\b[^.;:\n]{0,90}?[,.;:]\s*(es|era|son|sino)\b"),
    ("contraste", r"\bno se trata de\b|\besto no va de\b|\bno va de\b"),
    ("contraste", r"\bno solo\b|\bno sólo\b|\bno solamente\b|\bno únicamente\b"),
    ("contraste", r"\bsino\b"),
    ("contraste", r"\bmás que\b"),
    ("contraste", r"\blejos de\b"),
    ("contraste", r"\ben (vez|lugar) de\b"),
    ("contraste", r"\bmenos\b[^.\n]{0,40}\by más\b"),
    ("contraste", r"\bolvídate de\b|\bdeja de ser\b|\bquedó atrás\b|\bqueda atrás\b"),
    ("contraste", r"\bno se limita a\b"),
    ("contraste mayúscula", r"\bno\.\s+[A-ZÁÉÍÓÚ]"),
    ("contraste", r",\s+(y\s+)?no\s+\w+(\s+\w+)?\.(\s|$)"),
    ("cuenta atrás", r"\b(Sin|Ni|No)\s+\w+\.\s+(Sin|Ni|No)\s+\w+\."),
    # sello de autenticidad y énfasis
    ("sello", r"\breal(es|mente)?\b|\bde verdad\b|\bverdader[oa]s?\b|\bgenuin[oa]s?\b|\bauténtic[oa]s?\b"),
    ("énfasis", r"\b(esto|eso) importa\b|\blo que importa\b|\bla respuesta corta\b|\bla respuesta honesta\b|\bpara ser (claro|honesto|sincero)\b"),
    ("énfasis", r"\bclave\b|\bcrucial(es)?\b|\bfundamental(es)?\b|\besencial(es)?\b|\bpoderos[oa]s?\b|\bpotentes?\b|\bmágic[oa]s?\b|\bmagia\b|\bbrutal(es)?\b|\bincreíbles?\b|\btransformador(a|es|as)?\b"),
    # vocabulario delator
    ("vocabulario", r"\bsumerg\w*|\badentr\w*|\bdesentrañ\w*|\bahond\w*|\bnaveg\w*|\bpanorama\b|\becosistema\b|\bpotenci(ar|a|an)\b|\bimpuls(ar|a|an)\b|\bfoment(ar|a|an)\b|\bempoder\w*|\bdesbloque\w*|\bholístic\w*|\bsinergia\w*|\brobust\w*|\btapiz\b|\babanico\b"),
    ("vocabulario", r"\bviaje\b|\bpalanca\b|\bmatiz\b|\bmatices\b"),
    ("muletilla", r"\bsin duda\b|\ben definitiva\b|\ben resumen\b|\ben conclusión\b|\ben última instancia\b|\bcabe destacar\b|\bes importante (señalar|destacar|tener en cuenta|recordar)\b|\bvale la pena (mencionar|destacar)\b|\bal final del día\b|\bdicho esto\b|\ben el mundo actual\b|\bla era digital\b"),
    ("muletilla", r"\bjuega un papel\b|\bdesempeña un papel\b|\bse erige\b|\bjugar un rol\b|\ba nivel de\b|\bhace sentido\b"),
    ("antesala", r"\b(aquí|ahí) (viene|está) (lo|la|el)\b|\bspoiler\b|\bojo:|\bdato:|\btraducción:|\bel giro\b|\bla trampa\b"),
    ("apertura", r"^\s*(¡claro|claro[,!]|¡por supuesto|por supuesto[,!]|¡excelente|¡gran pregunta|aquí tienes)"),
    ("cierre", r"\b¿quieres que\b|\bsi quieres,? (puedo|te)\b|\bespero que (te )?(sirva|ayude)\b"),
    # suspense
    ("pregunta respondida", r"¿[^?\n]{1,45}\?\s+[A-ZÁÉÍÓÚ0-9]"),
    ("dos puntos + mayúscula", r":\s+[A-ZÁÉÍÓÚ][a-záéíóú]"),
    # puntuación
    ("raya", r"—"),
    ("punto y coma", r";"),
    # sintaxis
    ("gerundio de cola", r",\s+\w+(ando|iendo|yendo)(se|lo|la|le|les|los|las)?\b[^.\n]{0,80}\.(\s|$)"),
    # tríada de palabras sueltas
    ("tríada", r"\b\w+,\s+\w+\s+y\s+\w+\b[.!]"),
]
QUOTES = re.compile(r"«[^»]*»")


def lineas_objetivo(txt, modo):
    """Devuelve (número de línea, texto a revisar) según el modo."""
    en_codigo = False
    en_tabla_antes = False
    for i, line in enumerate(txt.splitlines(), 1):
        s = line.strip()
        if s.startswith("```"):
            en_codigo = not en_codigo
            continue
        if modo == "todo":
            yield i, line
            continue
        if modo == "codigo":
            if en_codigo:
                yield i, QUOTES.sub(lambda m: " " * len(m.group(0)), line)
            continue
        if en_codigo:
            continue
        if s.startswith("|"):
            celdas = [c.strip() for c in s.strip("|").split("|")]
            if celdas and celdas[0].lower().startswith("antes"):
                en_tabla_antes = True
                continue
            if re.match(r"^\|[\s:\-|]+\|?$", s):
                continue
            if modo == "despues":
                if en_tabla_antes and len(celdas) > 1:
                    yield i, celdas[1]
                continue
            # prosa: en tablas Antes | Después no se revisa nada (se revisa con --despues)
            if en_tabla_antes:
                continue
            yield i, QUOTES.sub(lambda m: " " * len(m.group(0)), line)
            continue
        en_tabla_antes = False
        if modo == "despues":
            continue
        if s.startswith(">"):
            continue
        yield i, QUOTES.sub(lambda m: " " * len(m.group(0)), line)


def main():
    path = sys.argv[1]
    modo = "prosa"
    for flag, m in (("--despues", "despues"), ("--codigo", "codigo"), ("--todo", "todo")):
        if flag in sys.argv:
            modo = m
    txt = open(path, encoding="utf-8").read()
    n = 0
    cuenta = {}
    for i, scan in lineas_objetivo(txt, modo):
        for name, p in PATS:
            flags = 0 if name in ("dos puntos + mayúscula", "pregunta respondida", "contraste mayúscula", "cuenta atrás") else re.I
            for m in re.finditer(p, scan, flags=flags | re.M):
                a, b = max(0, m.start() - 70), min(len(scan), m.end() + 70)
                print(f"L{i} [{name}] …{scan[a:b].strip()}…")
                n += 1
                cuenta[name] = cuenta.get(name, 0) + 1
    # encabezados con mayúscula en cada palabra
    for i, line in enumerate(txt.splitlines(), 1):
        m = re.match(r"^#{1,4}\s+(.*)", line)
        if m and modo in ("prosa", "todo"):
            palabras = [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", m.group(1)) if len(w) > 3]
            mayus = [w for w in palabras[1:] if w[0].isupper()]
            if len(mayus) >= 2:
                print(f"L{i} [título en mayúsculas] {line.strip()}")
                n += 1
    negritas = len(re.findall(r"\*\*[^*]+\*\*", txt))
    emojis = len(re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", txt))
    palabras = len(txt.split())
    print(f"--- modo {modo} · {n} avisos · {palabras} palabras · {negritas} negritas · {emojis} emojis")
    print("--- por tipo: " + ", ".join(f"{k} {v}" for k, v in sorted(cuenta.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
