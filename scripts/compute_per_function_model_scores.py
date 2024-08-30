import pandas as pd
import matplotlib.pyplot as plt
import sys, os, argparse


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model_name",
        type=str,
        help="Provide model name for which scores should be computed",
    )
    parser.add_argument(
        "--proteingym_dir",
        type=str,
        default="./ProteinGym/",
        help="Path of proteinGym repository",
        required=False,
    )
    # TODO: Remove this argument if we're able to run the entirety of ProteinGym
    parser.add_argument(
        "--ssemb_score_file_path",
        type=str,
        help="Path to score file for SSEmb model. This is needed to short list DMS assays",
    )

    args = parser.parse_args()

    print(f"Computing Scores for {args.model_name}")

    proteingym_path = args.proteingym_dir
    model_name = args.model_name

    print(f"Computing Scores for {model_name}")

    benchmark_df = pd.read_csv(
        proteingym_path
        + os.sep
        + "benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv"
    )

    dms_assays = set(
        pd.read_csv(args.ssemb_score_file_path).dropna()["dms_id"].unique()
    )

    model_score_df = benchmark_df[
        [model_name, "DMS ID", "UniProt ID", "Selection Type", "Taxon"]
    ]
    model_score_df = model_score_df[model_score_df["DMS ID"].isin(dms_assays)]

    average_scores_by_function = (
        model_score_df.groupby(["UniProt ID", "Selection Type"])
        .mean()
        .groupby("Selection Type")
        .mean()
        .round(4)
    )

    print(average_scores_by_function)

    print(average_scores_by_function.mean().round(4))


if __name__ == "__main__":
    main()
