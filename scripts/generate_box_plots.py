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
    
    for dms_id in dms_ids:
        if dms_id == 'BRCA2_HUMAN_Erwood_2022_HEK293T':
            continue
        dms_scores[dms_id] = pd.read_csv(dms_substitution_assay_path + os.sep + dms_id + '.csv')[['mutant', 'mutated_sequence', 'DMS_score']]
            #pd.read_csv(zero_shot_scores_path+ os.sep + config[m_name]["location"] + os.sep + dms_id + '.csv')
        for m_name in model_names:
            model_score_df = pd.read_csv(zero_shot_scores_path+ os.sep + config[m_name]["location"] + os.sep + dms_id + '.csv')
            if 'mutant' in model_score_df.columns:
                dms_scores[dms_id] = dms_scores[dms_id].merge(model_score_df[['mutant', config[m_name]["input_score_name"]]], how='left', on='mutant')
            else:
                dms_scores[dms_id] = dms_scores[dms_id].merge(model_score_df[['mutated_sequence', config[m_name]["input_score_name"]]], how='left', on='mutated_sequence')

            dms_scores[dms_id][config[m_name]["input_score_name"]] = dms_scores[dms_id][config[m_name]["input_score_name"]]*config[m_name]["directionality"]
    return dms_scores


def create_ensemble_df(dms_substitution_assay_path, zero_shot_scores_path, config, model_names):

    dms_scores = fetch_model_scores(zero_shot_scores_path, dms_substitution_assay_path, ['ESM-IF1', "VESPA",  "GEMME", "Tranception_L"], config)
    dms_ids = list(dms_scores.keys())
    ensemble_data = {'Ensemble1':[], 'Ensemble2':[], 'Ensemble3':[], 'Ensemble4':[]}
    # Create ensembles

    for dms_id in dms_ids:

        ensemble2_score = 0.5*dms_scores[dms_id][config['ESM-IF1']["input_score_name"]] + 0.5*dms_scores[dms_id][config['Tranception_L']["input_score_name"]]
        ensemble_data['Ensemble2'].append(spearmanr(dms_scores[dms_id]['DMS_score'],
                                                ensemble2_score).statistic)
        ensemble3_score = 0.5*dms_scores[dms_id][config['ESM-IF1']["input_score_name"]] + 0.5*dms_scores[dms_id][config['GEMME']["input_score_name"]]
        ensemble_data['Ensemble3'].append(spearmanr(dms_scores[dms_id]['DMS_score'],
                                                ensemble3_score).statistic)
        ensemble4_score = 0.5*dms_scores[dms_id][config['ESM-IF1']["input_score_name"]] + 0.5*dms_scores[dms_id][config['VESPA']["input_score_name"]]
        ensemble_data['Ensemble4'].append(spearmanr(dms_scores[dms_id]['DMS_score'],
                                                ensemble4_score).statistic)
    
        ensemble_data['DMS_id'] = dms_ids
    
    dms_scores = fetch_model_scores(zero_shot_scores_path, dms_substitution_assay_path, ['ESM-IF1', "TranceptEVE_L"], config)
    dms_ids = list(dms_scores.keys())
    for dms_id in dms_ids:
        ensemble1_score = 0.5*dms_scores[dms_id][config['ESM-IF1']["input_score_name"]] + 0.5*dms_scores[dms_id][config['TranceptEVE_L']["input_score_name"]]
        ensemble_data['Ensemble1'].append(spearmanr(dms_scores[dms_id]['DMS_score'],
                                                ensemble1_score).statistic)
    return pd.DataFrame(ensemble_data)

def main():
    config = {}
    with open("../ProteinGym/config.json", "r") as f:
        config = json.load(f)["model_list_zero_shot_substitutions_DMS"]
    zero_shot_score_path = '../ProteinGym/data/zero_shot_substitutions_scores/'
    dms_assay_path = '../ProteinGym/data/DMS_ProteinGym_substitutions/'

    bm_file = pd.read_csv('assets/DMS_substitutions_Spearman_DMS_level.csv')
    dms_ids = [id for id in bm_file['DMS ID'] if id != 'BRCA2_HUMAN_Erwood_2022_HEK293T']
    model_scores = []

    for mname in MODEL_NAMES:
        model_scores.append(bm_file[mname].to_numpy())

    ssemb_scores_df = pd.read_csv('assets/df_total_proteingym_1.csv').dropna()
    dms_ids_ssemb = ssemb_scores_df['dms_id'].unique().tolist()
    ssemb_corrs = []
    for dms_id in dms_ids_ssemb:
        ssemb_corrs.append(spearmanr(ssemb_scores_df[ssemb_scores_df['dms_id'] == dms_id]['score_dms'],
                                     ssemb_scores_df[ssemb_scores_df['dms_id'] == dms_id]['score_ml']).statistic)
    model_scores.append(np.array(ssemb_corrs))
    
    ensemble_df = create_ensemble_df(dms_assay_path, zero_shot_score_path, config, ['ESM-IF1', "VESPA",  "GEMME", "Tranception_L", "TranceptEVE_L"])
    #ensemble_df = pd.read_csv('./ensembled_scores.csv')

    ensemble1_score = []
    ensemble2_score = []
    ensemble3_score = []
    ensemble4_score = []
    for dms_id in dms_ids:
        ensemble1_score.append(ensemble_df[ensemble_df['DMS_id'] == dms_id]['Ensemble1'].item())
        ensemble2_score.append(ensemble_df[ensemble_df['DMS_id'] == dms_id]['Ensemble2'].item())
        ensemble3_score.append(ensemble_df[ensemble_df['DMS_id'] == dms_id]['Ensemble3'].item())
        ensemble4_score.append(ensemble_df[ensemble_df['DMS_id'] == dms_id]['Ensemble4'].item())

    model_scores.append(np.array(ensemble1_score))
    model_scores.append(np.array(ensemble2_score))
    model_scores.append(np.array(ensemble3_score))
    model_scores.append(np.array(ensemble4_score))


    
    # Matplotlib figure
    fig, ax = plt.subplots( nrows=1, ncols=1, figsize=(15, 10), dpi=600)
    fig
    ax.boxplot(model_scores, labels=MODEL_NAMES + ['SSEmb', 'Ensemble1', 'Ensemble2', 'Ensemble3', 'Ensemble4'], showmeans=True, vert=False)
    fig.savefig(f'all_boxplots.png')
    plt.close(fig)

    return

if __name__ == '__main__':
    main()
