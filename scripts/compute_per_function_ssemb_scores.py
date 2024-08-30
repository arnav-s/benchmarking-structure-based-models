import pandas as pd
import matplotlib.pyplot as plt
import sys, os
from scipy.stats import spearmanr
import yaml


def main():
    with open("config/ssemb.yaml") as yaml_file:
        args = yaml.safe_load(yaml_file)

    proteingym_ref_file = args["proteingym_ref_file"]

    if not os.path.isfile(proteingym_ref_file):
        print(f"ProteinGym repository not found at path: {proteingym_ref_file}\n\
                Please run scripts/fetch_proteingym_assets.sh from the root directory of the project.")
        sys.exit(1)

    reference_df = pd.read_csv(proteingym_ref_file).rename(
        columns={"coarse_selection_type": "Selection Type"}
    )

    ssemb_score_file = (
        pd.read_csv(args["ssemb_score_file_path"])
        .dropna()
        .rename(columns={"dms_id": "DMS_id"})
    )

    dms_assays = ssemb_score_file["DMS_id"].unique().tolist()

    spearman_list = []
    for assay in dms_assays:
        spearman_list.append(
            spearmanr(
                ssemb_score_file[ssemb_score_file["DMS_id"] == assay]["score_ml"],
                ssemb_score_file[ssemb_score_file["DMS_id"] == assay]["score_dms"],
            ).statistic
        )

    ssemb_score_file = pd.DataFrame(
        data={
            "DMS_id": dms_assays,
            "spearman_r": spearman_list,
        }
    )
    """
    ssemb_score_file["Spearman"] = spearmanr(
        ssemb_score_file["score_ml"], ssemb_score_file["score_dms"]
    ).statistic
    """

    model_score_df = ssemb_score_file[["DMS_id", "spearman_r"]].merge(
        reference_df[["DMS_id", "UniProt_ID", "Selection Type"]],
        how="left",
        on="DMS_id",
    )

    average_scores_by_function = (
        model_score_df.groupby(["UniProt_ID", "Selection Type"])["spearman_r"]
        .mean()
        .groupby("Selection Type")
        .mean()
        .round(4)
    )

    print(average_scores_by_function)

    print(f"Average spearman rho: {average_scores_by_function.mean().round(4)}")


if __name__ == "__main__":
    main()
