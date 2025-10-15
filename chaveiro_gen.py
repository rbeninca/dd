#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#git ignore: chaveiro_gen.py out/ *.stl *.scad  *.png  .gitignore --- IGNORE ---
"""
Gerador automático de plaquinhas de chaveiro (.stl) a partir de um arquivo JSON.

Exemplo de uso básico:
    python chaveiro_gen.py nomes.json

Exemplo com parâmetros adicionais:
    python chaveiro_gen.py nomes.json \
        --model chaveiros.scad \
        --linhas-por-coluna 10 \
        --colunas 3 \
        --outdir saidas

Exemplo com caminho completo do OpenSCAD:
    python chaveiro_gen.py nomes.json --openscad /usr/bin/openscad

O JSON deve conter um vetor de pares como:
{
  "pares": [
    ["Yuri", "Salomao"],
    ["Leonardo", "Leonardo"],
    ["GFIG", "GFIG"]
  ]
}
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Função auxiliar para exibir mensagem personalizada quando o usuário erra
# ---------------------------------------------------------------------------
def mostrar_exemplos():
    print("""
Exemplos de uso válidos:
  1️⃣  Geração básica (usa chaveiros.scad por padrão)
      python chaveiro_gen.py nomes.json

  2️⃣  Definindo outro modelo e alterando o layout
      python chaveiro_gen.py nomes.json --model chaveiros.scad --linhas-por-coluna 12 --colunas 4

  3️⃣  Salvando saídas em outra pasta
      python chaveiro_gen.py nomes.json --outdir resultados

  4️⃣  Informando caminho completo do OpenSCAD
      python chaveiro_gen.py nomes.json --openscad "C:\\Program Files\\OpenSCAD\\openscad.exe"
""")

# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Gera arquivos STL de plaquinhas de chaveiro a partir de um JSON.",
    formatter_class=argparse.RawTextHelpFormatter,
    epilog="""
Exemplo mínimo:
  python chaveiro_gen.py servidores.json

Mais opções:
  python chaveiro_gen.py servidores.json --linhas-por-coluna 10 --colunas 3 --outdir out
"""
)
parser.add_argument("json", nargs="?", help="Caminho do arquivo JSON com os nomes e sobrenomes.")
parser.add_argument("--model", default="chaveiros.scad", help="Modelo SCAD base (padrão: chaveiros.scad)")
parser.add_argument("--linhas-por-coluna", type=int, default=10, help="Número de linhas por coluna (deve ser par).")
parser.add_argument("--colunas", type=int, default=3, help="Número de colunas (padrão: 3).")
parser.add_argument("--openscad", default="openscad", help="Comando ou caminho do executável do OpenSCAD.")
parser.add_argument("--outdir", default="out", help="Diretório onde serão salvos os arquivos gerados.")
parser.add_argument("--keep-scad", action="store_true", help="Mantém os arquivos .scad intermediários.")
parser.add_argument("--timeout", type=int, default=600, help="Timeout em segundos para renderização (padrão: 300s)")

args = parser.parse_args()

# ---------------------------------------------------------------------------
# Verificação inicial de parâmetros obrigatórios
# ---------------------------------------------------------------------------
if not args.json:
    print("\n⚠️  Erro: você deve informar o caminho de um arquivo JSON com os nomes.")
    print("\nUso correto:")
    parser.print_usage()
    mostrar_exemplos()
    sys.exit(1)

# ---------------------------------------------------------------------------
# Validações adicionais
# ---------------------------------------------------------------------------
if args.linhas_por_coluna % 2 != 0:
    print(f"\n⚠️  Erro: --linhas-por-coluna deve ser par (você passou {args.linhas_por_coluna}).")
    sys.exit(1)

if not os.path.isfile(args.json):
    print(f"\n⚠️  Erro: arquivo JSON não encontrado: {args.json}")
    sys.exit(1)

if not os.path.isfile(args.model):
    print(f"\n⚠️  Erro: modelo SCAD não encontrado: {args.model}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Leitura do JSON
# ---------------------------------------------------------------------------
print(f"📂 Lendo arquivo: {args.json}")
try:
    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    print(f"\n⚠️  Erro ao ler JSON: {e}")
    sys.exit(1)

# Debug: mostrar o que foi lido
print(f"🔍 DEBUG: Chaves encontradas no JSON: {list(data.keys())}")
print(f"🔍 DEBUG: Tipo do objeto: {type(data)}")

if "pares" not in data or not isinstance(data["pares"], list):
    print("\n⚠️  Erro: o JSON deve conter uma chave 'pares' com uma lista de pares [nome, sobrenome].")
    print(f"    Conteúdo recebido: {data}")
    sys.exit(1)

pares = data["pares"]
total_pares = len(pares)
print(f"✅ {total_pares} pares encontrados.")

if total_pares == 0:
    print("\n⚠️  Nenhum par para processar. Saindo...")
    sys.exit(0)

# ---------------------------------------------------------------------------
# Criar diretório de saída
# ---------------------------------------------------------------------------
Path(args.outdir).mkdir(parents=True, exist_ok=True)
print(f"📁 Diretório de saída: {args.outdir}")

# ---------------------------------------------------------------------------
# Calcular quantas placas serão necessárias
# CORREÇÃO: cada par ocupa 2 linhas (frente e verso)
# ---------------------------------------------------------------------------
chaveiros_por_coluna = args.linhas_por_coluna // 2
pares_por_placa = chaveiros_por_coluna * args.colunas
num_placas = math.ceil(total_pares / pares_por_placa)

print(f"📊 Layout: {args.linhas_por_coluna} linhas ÷ 2 = {chaveiros_por_coluna} chaveiros por coluna")
print(f"📊 Total: {chaveiros_por_coluna} chaveiros × {args.colunas} colunas = {pares_por_placa} chaveiros por placa")
print(f"📋 Serão geradas {num_placas} placa(s)")

# ---------------------------------------------------------------------------
# Processar cada placa
# ---------------------------------------------------------------------------
for placa_idx in range(num_placas):
    inicio = placa_idx * pares_por_placa
    fim = min(inicio + pares_por_placa, total_pares)
    pares_desta_placa = pares[inicio:fim]
    
    print(f"\n🔨 Processando placa {placa_idx + 1}/{num_placas} (pares {inicio + 1} a {fim})")
    
    # Gerar arquivo SCAD intermediário
    scad_file = os.path.join(args.outdir, f"placa_{placa_idx + 1}.scad")
    stl_file = os.path.join(args.outdir, f"placa_{placa_idx + 1}.stl")
    
    # Ler o modelo base
    with open(args.model, 'r', encoding='utf-8') as f:
        modelo_base = f.read()
    
    # Gerar o vetor de nomes no formato OpenSCAD
    nomes_scad = "nomes = [\n"
    for nome, sobrenome in pares_desta_placa:
        # Escapar aspas dentro dos nomes se necessário
        nome_esc = nome.replace('"', '\\"')
        sobrenome_esc = sobrenome.replace('"', '\\"')
        nomes_scad += f'  ["{nome_esc}", "{sobrenome_esc}"],\n'
    nomes_scad += "];"
    
    # Substituir o vetor 'nomes' no modelo base
    # Procura pelo padrão: nomes = [ ... ];
    padrao = r'nomes\s*=\s*\[.*?\];'
    
    if re.search(padrao, modelo_base, re.DOTALL):
        modelo_modificado = re.sub(padrao, nomes_scad, modelo_base, flags=re.DOTALL)
    else:
        # Se não encontrar o padrão, adiciona no final antes do render
        # Procura pela linha que chama arranjo_pareado_uniforme
        padrao_render = r'(arranjo_pareado_uniforme\s*\([^)]*\)\s*;)'
        if re.search(padrao_render, modelo_base):
            modelo_modificado = re.sub(
                padrao_render,
                nomes_scad + '\n\n\\1',
                modelo_base
            )
        else:
            print("  ⚠️  Aviso: não foi possível localizar o vetor 'nomes' ou a chamada do módulo.")
            print("     Adicionando o vetor no final do arquivo...")
            modelo_modificado = modelo_base + "\n\n" + nomes_scad
    
    # Salvar o arquivo SCAD modificado
    with open(scad_file, 'w', encoding='utf-8') as f:
        f.write(modelo_modificado)
    
    print(f"  ✏️  Arquivo SCAD gerado: {scad_file}")
    
    # Verificar tamanho do arquivo SCAD
    scad_size = os.path.getsize(scad_file)
    print(f"  📏 Tamanho do SCAD: {scad_size} bytes ({len(pares_desta_placa)} chaveiros)")
    
    # Renderizar com OpenSCAD
    print(f"  ⚙️  Renderizando STL (timeout: {args.timeout}s)...")
    print(f"  📝 Comando: {args.openscad} -o {stl_file} {scad_file}")
    
    # Adicionar flags para melhorar renderização em background
    openscad_args = [
        args.openscad,
        "-o", stl_file,
        "--export-format", "binstl",  # STL binário (mais rápido)
        scad_file
    ]
    
    print(f"  ⏱️  Iniciando renderização...")
    import time
    start_time = time.time()
    
    # Renderizar com OpenSCAD
    print(f"  ⚙️  Renderizando STL...")
    print(f"  📝 Comando: {args.openscad} -o {stl_file} {scad_file}")
    
    erro_renderizacao = False
    try:
        resultado = subprocess.run(
            openscad_args,
            capture_output=True,
            text=True,
            timeout=args.timeout
        )
        
        elapsed = time.time() - start_time
        print(f"  ⏱️  Renderização levou {elapsed:.1f} segundos")
        
        # Mostrar saída completa para debug
        if resultado.stdout:
            print(f"  📄 STDOUT:\n{resultado.stdout}")
        
        if resultado.returncode == 0:
            # Verificar se o arquivo STL foi realmente criado
            if os.path.exists(stl_file) and os.path.getsize(stl_file) > 0:
                stl_size = os.path.getsize(stl_file)
                print(f"  ✅ STL gerado com sucesso: {stl_file}")
                print(f"  📏 Tamanho: {stl_size:,} bytes ({stl_size/1024/1024:.2f} MB)")
            else:
                print(f"  ⚠️  OpenSCAD retornou sucesso, mas o arquivo STL não foi criado ou está vazio!")
                erro_renderizacao = True
        else:
            print(f"  ❌ Erro ao renderizar (código: {resultado.returncode})")
            erro_renderizacao = True
        
        # Sempre mostrar stderr se houver conteúdo
        if resultado.stderr:
            print(f"  ⚠️  STDERR:\n{resultado.stderr}")
            
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"  ⏱️  Timeout ao renderizar após {elapsed:.1f}s (limite: {args.timeout}s)")
        print(f"  💡 Dica: Use --timeout com um valor maior, ex: --timeout 600")
        erro_renderizacao = True
    except FileNotFoundError:
        print(f"  ❌ OpenSCAD não encontrado!")
        print(f"     Comando tentado: {args.openscad}")
        print(f"     Verifique se o OpenSCAD está instalado e no PATH.")
        print(f"     Ou use --openscad para informar o caminho completo do executável.")
        print(f"     Exemplo: --openscad 'C:\\Program Files\\OpenSCAD\\openscad.exe'")
        sys.exit(1)
    except Exception as e:
        print(f"  ❌ Erro inesperado: {e}")
        erro_renderizacao = True
    
    # Limpar arquivo SCAD se não for para manter E não houve erro
    if not args.keep_scad and not erro_renderizacao and os.path.exists(scad_file):
        os.remove(scad_file)
        print(f"  🗑️  Arquivo SCAD temporário removido")
    elif erro_renderizacao:
        print(f"  💾 Arquivo SCAD mantido para debug: {scad_file}")

print(f"\n🎉 Processo concluído! {num_placas} placa(s) gerada(s) em: {args.outdir}")

# Dicas finais
print("\n💡 Dicas:")
print("   • Se a renderização estiver lenta, tente:")
print("     --timeout 600  (aumentar o tempo limite)")
print("   • Para debug, use:")
print("     --keep-scad  (mantém arquivos .scad para inspeção)")
print("   • Teste o arquivo .scad diretamente no OpenSCAD GUI para ver erros visuais")