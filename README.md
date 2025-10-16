# 🔑 Gerador de Chaveiros (.stl) a partir de nomes

Este projeto gera automaticamente **plaquinhas de chaveiro** em **formato STL** usando o **OpenSCAD**, a partir de um arquivo **JSON** com pares `[Nome, Sobrenome]`.

> 💡 Uso pessoal: organizar e imprimir chaveiros baseados em nomes (ex.: turmas, equipes, eventos).

---

## ✨ Visão geral

* **Entrada**: `nomes.json` contendo `{ "pares": [["Nome","Sobrenome"], ...] }`
* **Modelo**: arquivo `.scad` base (ex.: `chaveiros.scad`) com o módulo `arranjo_pareado_uniforme(...)`
* **Saída**: arquivos `.stl` (e opcionais `.scad` intermediários) na pasta `out/`
* **Renderização**: feita via **OpenSCAD (CLI)**

---

## 📦 Requisitos

* **Python 3.8+**
* **OpenSCAD** instalado e acessível no PATH

  * Linux/macOS: `openscad`
  * Windows: `"C:\Program Files\OpenSCAD\openscad.exe"`

---

## 🗂️ Estrutura sugerida

```
.
├── chaveiro_gen.py           # Script principal (Python)
├── chaveiros.scad            # Modelo base (OpenSCAD)
├── exemplos/
│   └── nomes_exemplo.json    # Exemplo de entrada
├── modelos/
│   └── chaveiro_base_v1.stl  # Modelo base STL
└── out/                      # (gerado) STL e SCAD intermediários
```

---

## 🧬 Exemplo de arquivo JSON

```json
{
  "pares": [
    ["Romulo", "Beninca"],
    ["Leonardo", "Leonardo"],
    ["GFIG", "GFIG"]
  ]
}
```

---

## ⚙️ Parâmetros disponíveis

| Parâmetro             | Padrão           | Descrição                                  |
| --------------------- | ---------------- | ------------------------------------------ |
| `json`                | *(obrigatório)*  | Arquivo com os pares de nomes.             |
| `--model`             | `chaveiros.scad` | Modelo SCAD base.                          |
| `--linhas-por-coluna` | `10`             | Linhas por coluna (deve ser **par**).      |
| `--colunas`           | `3`              | Número de colunas.                         |
| `--openscad`          | `openscad`       | Caminho do executável do OpenSCAD.         |
| `--outdir`            | `out`            | Pasta de saída.                            |
| `--keep-scad`         | *(desativado)*   | Mantém arquivos `.scad` intermediários.    |
| `--timeout`           | `600`            | Tempo limite (segundos) para renderização. |

---

## 🚀 Exemplos de uso

### 🧱 Gerar 3 colunas de 10 linhas (padrão)

```bash
python chaveiro_gen.py nomes.json
```

### 🔢 Gerar placas com 4 colunas e 12 linhas

```bash
python chaveiro_gen.py nomes.json --linhas-por-coluna 12 --colunas 4
```

### 🧩 Definir outro modelo SCAD

```bash
python chaveiro_gen.py nomes.json --model meus_chaveiros.scad
```

### 📁 Salvar saídas em outra pasta

```bash
python chaveiro_gen.py nomes.json --outdir resultados
```

---

## ▶️ Para rodar o script diretamente

```bash
python gerar_chaveiros.py
```

ou, com parâmetros específicos:

```bash
python chaveiro_gen.py servidores.json --model chaveiros.scad --linhas-por-coluna 10 --colunas 3
```

---

## 💡 Dicas úteis

* Certifique-se de que o **OpenSCAD** está instalado e acessível pelo terminal.
  Teste com:

  ```bash
  openscad --version
  ```

* Se o arquivo STL não for gerado, use:

  ```bash
  --keep-scad
  ```

  para inspecionar o `.scad` intermediário no OpenSCAD GUI.

* Cada **par [Nome, Sobrenome]** ocupa **duas linhas** (uma para o nome e outra para o sobrenome), por isso `--linhas-por-coluna` deve sempre ser **par**.

---




---

## 🧾 Licença

Projeto de uso pessoal — livre para adaptação e compartilhamento.
Se desejar, utilize uma licença aberta como **MIT** ou **CC-BY-SA**.

---

**Autor:** Romulo de Aguiar Beninca
Professor de Informática — Instituto Federal de Santa Catarina (IFSC)

