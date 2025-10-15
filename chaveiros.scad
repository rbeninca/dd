//////////////////////////////////////////////////////////////
// Geração automática de chaveiros (nome e sobrenome pareados)
// Arquivo gerado a partir de: servidores_chaveiros.json
//////////////////////////////////////////////////////////////

// --- modelo e offsets
stl_path = "../modelos/chaveiro_base_v1.stl";
//verificar se  o arquivo existe
stl_offset = [108, -115, 0];
text_offset = [36, 10, 2.5];

// --- texto/estilo
font_name = "Sans Mono:style=Bold";
font_size = 9.0;
text_height = 2.2;

// --- layout da grade
dx = 62; // espaçamento horizontal (entre colunas)
dy = 21; // espaçamento vertical (entre linhas)
start_at = [0, 0, 0];

// --- ajuste automático do “comprimento” (achatamento em X)
texto_max_largura = 30; // largura útil (mm)
char_pitch = 0.70;
min_scale_x = 0.60;

function esc_x(txt) =
  max(
    min_scale_x,
    min(1, texto_max_largura / (len(txt) * font_size * char_pitch))
  );

module chaveiro_com_texto(txt) {
  translate(stl_offset)
    import(stl_path);

  translate(text_offset)
    color("blue")
      scale([esc_x(txt), 1, 1])
        linear_extrude(height=text_height)
          text(
            txt, size=font_size, font=font_name,
            halign="center", valign="center"
          );
}

// =======================
// Vetor de pares [NOME, SOBRENOME]
// =======================
nomes = [
  ["GFIG", "Sobrenome"],  //1
  ["GFIG", "Sobrenome"],  //2
  ["GFIG", "Sobrenome"],  //3
  ["GFIG", "Sobrenome"],  //4
  ["GFIG", "Sobrenome"],  //5
  ["GFIG", "Sobrenome"],  //6
  ["GFIG", "Sobrenome"],  //7
  ["GFIG", "Sobrenome"],  //8
  ["GFIG", "Sobrenome"],  //9
  ["GFIG", "Sobrenome"],  //10
  ["GFIG", "Sobrenome"],  //11
  ["GFIG", "Sobrenome"],  //12
  ["GFIG", "Sobrenome"],  //13
  ["GFIG", "Sobrenome"],  //14
  ["GFIG", "Sobrenome"],  //15
];

// ----------------------------------------------------------
// Nova lógica: TODAS as colunas funcionam como a antiga 3ª.
// Cada par ocupa DUAS linhas: Nome (linha r) e Sobrenome (linha r+1).
// Avança para a próxima coluna quando não couber mais o par na atual.
// 'linhas_por_coluna' deve ser PAR (ex.: 10).
// Capacidade de pares por coluna = linhas_por_coluna / 2.
// ----------------------------------------------------------
module arranjo_pareado_uniforme(pares, linhas_por_coluna = 10) {
  // Garantir paridade (evita quebrar par no final da coluna)
  assert(linhas_por_coluna % 2 == 0, "linhas_por_coluna deve ser par.");

  cap_pares_por_coluna = floor(linhas_por_coluna / 2);

  // Distribui cada par sequencialmente: coluna por coluna
  for (i = [0:len(pares) - 1]) {
    // coluna do par i
    col = floor(i / cap_pares_por_coluna);

    // posição vertical (duas linhas por par)
    pos_no_bloco = i % cap_pares_por_coluna; // 0..cap-1
    r = pos_no_bloco * 2; // linha do Nome
    // r+1 será a linha do Sobrenome

    // Nome
    translate(start_at + [col * dx, -r * dy, 0])
      chaveiro_com_texto(pares[i][0]);

    // Sobrenome logo abaixo
    translate(start_at + [col * dx, -(r + 1) * dy, 0])
      chaveiro_com_texto(pares[i][1]);
  }
}

// ---------- render ----------
arranjo_pareado_uniforme(nomes, linhas_por_coluna=10);
