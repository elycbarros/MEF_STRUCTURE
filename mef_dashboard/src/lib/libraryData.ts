export interface Citation {
  bookId: string;
  citation: string;
  context: string;
}

export const LIBRARY_KNOWLEDGE: Record<string, Citation[]> = {
  "punching_shear": [
    {
      bookId: "teatini",
      citation: "Teatini (2014), Cap. 8 - Punção em Lajes",
      context: "Verificação da tensão cisalhante no contorno C' conforme NBR 6118."
    },
    {
      bookId: "ibracon_v1",
      citation: "IBRACON Vol 1, Seção 15.4",
      context: "Critérios de armadura de punção e conectores tipo stud."
    }
  ],
  "stability_global": [
    {
      bookId: "chopra",
      citation: "Chopra (2014), Dynamics of Structures",
      context: "Análise dinâmica para determinação de modos de vibração e efeitos de segunda ordem."
    },
    {
      bookId: "poulos",
      citation: "Poulos (2017), Tall Building Foundation Design",
      context: "Impacto da rigidez da fundação na estabilidade global (Gama-Z)."
    }
  ],
  "ise_winkler": [
    {
      bookId: "ise_ebook",
      citation: "Ebook ISE, Seção 3.2 - Modelo de Winkler",
      context: "Uso de molas independentes para representar a rigidez do solo (kv)."
    },
    {
      bookId: "velloso_v1",
      citation: "Velloso e Lopes, Vol 1",
      context: "Determinação do coeficiente de recalque a partir de ensaios de placa."
    }
  ],
  "wind_effects": [
    {
      bookId: "simiu_scanlan",
      citation: "Simiu & Scanlan (1996), Wind Effects",
      context: "Modelagem de turbulência e forças aerodinâmicas em edifícios esbeltos."
    }
  ]
};
