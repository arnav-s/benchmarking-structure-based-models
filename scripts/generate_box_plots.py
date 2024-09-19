import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json, glob
from scipy.stats import spearmanr
import os

MODEL_NAMES = ["TranceptEVE L", "VESPA",  "GEMME", "ProtSSN (ensemble)",\
               "ESM-IF1", "SaProt (650M)", ]

def fetch_model_scores(zero_shot_scores_path, dms_substitution_assay_path, model_names, config):
    dms_ids = [f.split('.csv')[0] for f in os.listdir(dms_substitution_assay_path)]
    dms_scores = {}
    for m_name in model_names:
    for dms_id in dms_ids:
        dms_scores[dms_id] = pd.read_csv(dms_substitution_assay_path + os.sep + dms_id + '.csv')[['mutant', 'mutated_sequence', 'DMS_score']]
            #pd.read_csv(zero_shot_scores_path+ os.sep + config[m_name]["location"] + os.sep + dms_id + '.csv')
            model_score_df = pd.read_csv(zero_shot_scores_path+ os.sep + config[m_name]["location"] + os.sep + dms_id + '.csv')
            if 'mutated_sequence' in model_score_df.columns:
                dms_scores[dms_id] = dms_scores[dms_id].merge(model_score_df[['mutated_sequence', config[m_name]["input_score_name"]]], how='left', on='mutated_sequence')
            else:
                dms_scores[dms_id] = dms_scores[dms_id].merge(model_score_df[['mutant', config[m_name]["input_score_name"]]], how='left', on='mutant')
            dms_scores[dms_id][config[m_name]["input_score_name"]] = dms_scores[dms_id][config[m_name]["input_score_name"]]*config[m_name]["directionality"]
    return dms_scores


def create_ensemble_df(dms_substitution_assay_path, zero_shot_scores_path, config):
    model_names = ['ESM-IF1', "VESPA",  "GEMME", "TranceptEVE_L", "Tranception_L"]
    dms_scores = fetch_model_scores(zero_shot_scores_path, dms_substitution_assay_path, model_names, config)
    dms_ids = list(dms_scores.keys())
    
    for m_name in model_names:



def main():
    config = {}
    with open("../ProteinGym/config.json", "r") as f:
        config = json.load(f)["model_list_zero_shot_substitutions_DMS"]
    zero_shot_score_path = '/Users/arnavsharma/Develop/gitterLab/ProteinGym/data/zero_shot_model_scores/substitution_scores'
    dms_assay_path = '/Users/arnavsharma/Develop/gitterLab/ProteinGym/data/DMS_substitutions'

    bm_file = pd.read_csv('assets/DMS_substitutions_Spearman_DMS_level.csv')
    dms_ids = [id for id in bm_file['DMS ID'] if id != 'BRCA2_HUMAN_Erwood_2022_HEK293T']
    model_scores = []

    for mname in MODEL_NAMES:
        model_scores.append(bm_file[mname].to_numpy())
        #print(dms_scores)
    ssemb_scores_df = pd.read_csv('assets/df_total_proteingym_1.csv').dropna()
    dms_ids_ssemb = ssemb_scores_df['dms_id'].unique().tolist()
    ssemb_corrs = []
    for dms_id in dms_ids_ssemb:
        ssemb_corrs.append(spearmanr(ssemb_scores_df[ssemb_scores_df['dms_id'] == dms_id]['score_dms'],
                                     ssemb_scores_df[ssemb_scores_df['dms_id'] == dms_id]['score_ml']).statistic)
    model_scores.append(np.array(ssemb_corrs))
    print(len(ssemb_corrs))
    
    ensemble_df = create_ensemble_df()
    

    
    # Matplotlib figure
    fig, ax = plt.subplots( nrows=1, ncols=1, figsize=(10, 10), dpi=600)
    fig
    ax.boxplot(model_scores, labels=MODEL_NAMES+['SSEmb'], showmeans=True)
    fig.savefig(f'all_boxplots.png')
    plt.close(fig)

    return

if __name__ == '__main__':
    main()
