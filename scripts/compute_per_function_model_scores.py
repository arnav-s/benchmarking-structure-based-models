import pandas as pd
import matplotlib.pyplot as plt
import sys, os
import yaml


def main():
    with open("config/proteingym.yaml") as yaml_file:
        args = yaml.safe_load(yaml_file)

    proteingym_bm_file = args["proteingym_bm_file"]
    if not os.path.isfile(proteingym_bm_file):
        print(f"ProteinGym repository not found at path: {proteingym_bm_file}\n\
                Please run scripts/setup_proteingym.sh from the root directory of the project.")
        sys.exit(1)

    model_names = args["model_names"]

    print(f"Computing Scores for {model_names}")

    benchmark_df = pd.read_csv(args["proteingym_bm_file"])

    dms_assays = set(
        pd.read_csv(args["ssemb_score_file_path"]).dropna()["dms_id"].unique()
    )

    for model_name in model_names:
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
