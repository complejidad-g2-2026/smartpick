# Reglas de trabajo

Lo que acordamos como equipo. Si algo cambia, se actualiza aquí.

## Reglas generales

1. **Los commits no llevan coautores ni ninguna referencia a IA.** Los únicos
   autores son los integrantes del equipo.
2. **Todo en español**: informe, comentarios del código y documentación. La
   excepción son los mensajes de commit, que van en inglés.
3. **Cada integrante debe poder explicar el código.** El profesor puede pedírselo a
   cualquiera en la sustentación y penaliza si no lo sabe explicar.
4. **Solo técnicas del curso**: fuerza bruta, backtracking, divide y vencerás,
   BFS/DFS, ordenamiento topológico, SCC, UFDS, MST (Kruskal o Prim), flujo máximo
   (Ford-Fulkerson), programación dinámica, voraces, Bellman-Ford y Floyd-Warshall.
5. **Fuentes y datos se citan en APA**, con su licencia.
6. **Primero se discute, después se implementa.** Nada de cambios grandes sin avisar
   al grupo.
7. **El informe va en Google Docs**, sobre la plantilla oficial, y se exporta a
   `.docx` para entregarlo. Este repositorio es solo para el código, los datos y
   las figuras.

## Commits

Los mensajes van **en inglés** y siguen
[Conventional Commits](https://www.conventionalcommits.org): un tipo, dos puntos y
qué hace el cambio.

```
feat: build warehouse graph
fix: correct aisle distances
docs: update project context
```

| Tipo | Para qué |
| --- | --- |
| `feat` | Funcionalidad o contenido nuevo |
| `fix` | Corrección de un error |
| `docs` | Documentación del repositorio |
| `refactor` | Reorganizar código sin cambiar lo que hace |
| `chore` | Configuración, dependencias, archivos auxiliares |

El hook `.githooks/commit-msg` revisa los dos puntos anteriores en tu máquina:
rechaza el commit si la primera línea no sigue el formato o si el mensaje incluye un
coautor (`Co-authored-by`) o una referencia a IA (`Generated with`, etc.). Se activa
una vez por equipo con:

```
git config core.hooksPath .githooks
```

Si un commit sale rechazado, corrige el mensaje y vuelve a intentarlo. Si ya lo
hiciste y aún no lo subiste, `git commit --amend` lo arregla.

## Ramas

| Rama | Para qué |
| --- | --- |
| `main` | Estado estable. De aquí salen las entregas. |
| `feature/<tema>` | Un cambio concreto, p. ej. `feature/held-karp`. Vive pocos días. |

Se trabaja en una rama, se sube y se abre una Pull Request hacia `main` para que
otro integrante la revise.

## Código

- Los parámetros del almacén (pasillos, distancias, zonas) viven en `src/config.py`.
  Nada de números sueltos en los demás scripts.
- Cada función lleva un docstring corto que diga qué hace.
- Los algoritmos del curso se implementan a mano; `networkx` solo se usa para
  guardar y dibujar el grafo, no para resolverlo.
- Las figuras se generan con código, nunca se editan a mano, para que se puedan
  regenerar si cambia el modelo.
