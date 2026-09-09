import argparse
import csv
from datetime import datetime
from pathlib import Path


def parse_data(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use o formato AAAA-MM-DD.") from exc


def escreve_csv(caminho, colunas, linhas):
    destino = Path(caminho)
    with destino.open("w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo, delimiter=";")
        writer.writerow(colunas)
        writer.writerows(linhas)
    return destino.resolve()


def exporta_controle(args):
    from dependencies import _conecta_notas, _to_iso_date

    conn = None
    try:
        conn, engine = _conecta_notas()
        cursor = conn.cursor()
        marcador = "%s" if engine == "postgres" else "?"
        filtros = [f"date >= {marcador}", f"date <= {marcador}"]
        params = [args.inicio, args.fim] if engine == "postgres" else [_to_iso_date(args.inicio), _to_iso_date(args.fim)]

        if args.empresa is not None:
            filtros.append(f"cod_cliente = {marcador}")
            params.append(args.empresa)

        where_sql = " AND ".join(filtros)
        query = f"""
            SELECT
                cod_cliente,
                tipo,
                tipo_nota_emitida,
                SUM(quantidade) AS total_notas,
                COUNT(*) AS lancamentos,
                SUM(tempo_minutos) AS tempo_minutos
            FROM registros
            WHERE {where_sql}
            GROUP BY cod_cliente, tipo, tipo_nota_emitida
            ORDER BY cod_cliente, tipo, tipo_nota_emitida
        """
        cursor.execute(query, tuple(params))
        linhas = cursor.fetchall()
        return [
            [
                linha[0],
                linha[1],
                linha[2],
                float(linha[3] or 0),
                int(linha[4] or 0),
                float(linha[5] or 0),
            ]
            for linha in linhas
        ]
    finally:
        if conn is not None:
            conn.close()


def exporta_dominio(args):
    from dependencies import conecta_odbc

    conn = conecta_odbc()
    try:
        cursor = conn.cursor()
        params = [args.inicio, args.fim]
        filtro_empresa = ""
        if args.empresa is not None:
            filtro_empresa = " AND codi_emp = ?"
            params.append(args.empresa)

        consultas = [
            (
                "Saida",
                f"""
                    SELECT codi_emp, COUNT(nume_sai)
                    FROM bethadba.efsaidas
                    WHERE ddoc_sai >= ? AND ddoc_sai <= ?{filtro_empresa}
                    GROUP BY codi_emp
                """,
            ),
            (
                "Servico",
                f"""
                    SELECT codi_emp, COUNT(nume_ser)
                    FROM bethadba.efservicos
                    WHERE ddoc_ser >= ? AND ddoc_ser <= ?{filtro_empresa}
                    GROUP BY codi_emp
                """,
            ),
        ]

        linhas = []
        for documento, query in consultas:
            cursor.execute(query, tuple(params))
            for codigo_empresa, total in cursor.fetchall():
                linhas.append([codigo_empresa, documento, "", int(total or 0), "", ""])
        return sorted(linhas, key=lambda item: (item[0], item[1]))
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Exporta o total de notas emitidas para CSV."
    )
    parser.add_argument(
        "--fonte",
        choices=["controle", "dominio"],
        required=True,
        help="controle = tabela registros do app; dominio = ODBC fiscal do Dominio/Betha.",
    )
    parser.add_argument("--inicio", required=True, type=parse_data, help="Data inicial: AAAA-MM-DD.")
    parser.add_argument("--fim", required=True, type=parse_data, help="Data final: AAAA-MM-DD.")
    parser.add_argument("--empresa", type=int, help="Codigo da empresa/cliente, opcional.")
    parser.add_argument(
        "--saida",
        default="notas_emitidas_resumo.csv",
        help="Arquivo CSV de destino.",
    )
    args = parser.parse_args()

    if args.fim < args.inicio:
        parser.error("--fim nao pode ser menor que --inicio.")

    if args.fonte == "controle":
        linhas = exporta_controle(args)
    else:
        linhas = exporta_dominio(args)

    colunas = [
        "codigo_empresa",
        "documento",
        "tipo_nota",
        "total_notas",
        "lancamentos",
        "tempo_minutos",
    ]
    destino = escreve_csv(args.saida, colunas, linhas)
    total = sum(float(linha[3] or 0) for linha in linhas)
    print(f"Arquivo gerado: {destino}")
    print(f"Total de notas: {total:.2f}")


if __name__ == "__main__":
    main()
