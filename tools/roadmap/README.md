# Module Vastleggen → Verbeterroadmap

Eén module voor alle frameworks. Per tabblad zet de module een kaart *Vastleggen* met punten die je beoordeelt als op orde, deels of niet op orde. Wat niet (helemaal) op orde is, wordt een actie in de verbeterroadmap. Per actie leg je periode, prioriteit, status en eigenaar vast. Export naar Excel (csv) of kopiëren.

- `items-core.js`: kernpunten (deel A), gelden voor elk framework.
- `items-<framework>.js`: branchepunten en de configuratie (`window.RM_CFG`) per framework: warmte, inwarmte, po (projectorganisaties, met `br` per branche).
- `rm_inject.py pagina.html items-<framework>.js [uit.html]`: zet de module in een framework-pagina.

Een punt toevoegen: voeg een regel toe in het juiste items-bestand (`id`, `tab`, `laag`, `groep`, `norm`, `actie`, `eig`, `fase`) en injecteer opnieuw.
