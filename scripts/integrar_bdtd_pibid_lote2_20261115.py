"""Integra leituras de registros BDTD recentes com PIBID no título."""

from scripts.integrar_bdtd_pibid_lote1_20261115 import ANALISES, integrar


BASE = ANALISES / "triagem_bdtd_pibid_lote1_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_bdtd_pibid_lote2_20261115.csv"
SAIDA = ANALISES / "triagem_bdtd_pibid_lote2_20261115.xlsx"


if __name__ == "__main__":
    integrar(BASE, DECISOES, SAIDA, lote_recente=True)
    print(f"Base criada: {SAIDA}")
