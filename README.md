# Gerador de Chaveiros (.stl) a partir de nomes

Este projeto gera automaticamente **plaquinhas de chaveiro** em **STL** usando o **OpenSCAD**, a partir de um arquivo **JSON** com pares `[Nome, Sobrenome]`.

> Uso pessoal: organizar e imprimir chaveiros baseados em nomes (ex.: turmas, equipes, eventos).

---

## ✨ Visão geral

- **Entrada**: `nomes.json` com `{"pares": [["Nome","Sobrenome"], ...]}`
- **Modelo**: arquivo `.scad` base (ex.: `chaveiros.scad`) com o módulo `arranjo_pareado_uniforme(...)`
- **Saída**: arquivos `.stl` (e opcionais `.scad` intermediários) na pasta `out/`
- **Render**: feito via `openscad` (CLI)

---

## 📦 Requisitos

- **Python 3.8+**
- **OpenSCAD** instalado e acessível no PATH  
  - Linux/macOS: `openscad`  
  - Windows: `"C:\Program Files\OpenSCAD\openscad.exe"`

---

## 🗂️ Estrutura sugerida
├── chaveiro_gen.py # script principal (Python)
├── chaveiros.scad # modelo base (OpenSCAD)
├── exemplos/
│ └── nomes_exemplo.json # exemplo de entrada
├── modelos/
│ └── chaveiro_base_v1.stl
└── out/ # (gerado) STLs e SCADs intermediários


```json
{
  "pares": [
    ["Romulo", "Beninca"],
    ["Leonardo", "Leonardo"],
    ["GFIG", "GFIG"]
  ]
}


## Para rodar o script:
```bash
python gerar_chaveiros.py
```
   python chaveiro_gen.py servidores.json --model chaveiros.scad --linhas-por-coluna 10 --colunas 3 
