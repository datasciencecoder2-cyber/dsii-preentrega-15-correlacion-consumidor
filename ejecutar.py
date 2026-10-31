"""Ejecuta y guarda el notebook con resultados embebidos (no requiere Internet)."""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent
NB = ROOT / 'notebooks' / 'preentrega_15_correlacion_consumidor.ipynb'


def main():
    cuaderno = nbformat.read(NB, as_version=4)
    NotebookClient(cuaderno, timeout=240, kernel_name='python3',
                   resources={'metadata': {'path': str(ROOT)}}).execute()
    nbformat.write(cuaderno, NB)
    errores = [o for c in cuaderno.cells if c.cell_type == 'code'
               for o in c.get('outputs', []) if o.output_type == 'error']
    if errores:
        raise RuntimeError(f'Notebook presenta {len(errores)} errores')
    print(f'NOTEBOOK EJECUTADO: OK ({len(cuaderno.cells)} celdas)')
    print(f'Se guardaron resultados visibles en {NB}')
    print('Archivos exportados en graficos/ y resultados/')


if __name__ == '__main__':
    main()
