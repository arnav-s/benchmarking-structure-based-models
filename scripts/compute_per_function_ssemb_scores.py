import pandas as pd
import matplotlib.pyplot as plt
import sys, os, argparse
from scipy.stats import spearmanr


def main():
    parser = argparse.ArgumentParser()

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
    proteingym_path = args.proteingym_dir

    reference_df = pd.read_csv(
        proteingym_path + os.sep + "reference_files/DMS_substitutions.csv"
    ).rename(columns={"coarse_selection_type": "Selection Type"})

    ssemb_score_file = (
        pd.read_csv(args.ssemb_score_file_path)
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

    print(model_score_df)

    average_scores_by_function = (
        model_score_df.groupby(["UniProt_ID", "Selection Type"])["spearman_r"]
        .mean()
        .groupby("Selection Type")
        .mean()
        .round(4)
    )

    print(average_scores_by_function)

    print(average_scores_by_function.mean().round(4))


if __name__ == "__main__":
    main()
