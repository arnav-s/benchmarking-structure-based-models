import pandas as pd
import matplotlib.pyplot as plt
import sys, os
import yaml
import json, glob
from scipy.stats import spearmanr
import numpy as np
import argparse

def calc_toprecall(true_scores, model_scores, top_true=10, top_model=10):  
    top_true = (true_scores >= np.percentile(true_scores, 100-top_true))
    top_model = (model_scores >= np.percentile(model_scores, 100-top_model))
    
    TP = (top_true) & (top_model)
    recall = TP.sum() / (top_true.sum()) if top_true.sum() > 0 else 0
    
    return (recall)

METRIC_FUNC_MAP = {
    'spearman': spearmanr,
    'recall': calc_toprecall
}

def apply_metric_func(metric: str, label_scores, pred_scores):
    if metric == 'spearman':
        return METRIC_FUNC_MAP[metric](label_scores, pred_scores).statistic
    else:
        return METRIC_FUNC_MAP[metric](label_scores, pred_scores)


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


def create_ensemble_df(dms_substitution_assay_path, zero_shot_scores_path, config, metric):

    dms_scores = fetch_model_scores(zero_shot_scores_path, dms_substitution_assay_path, ['ESM-IF1', "VESPA",  "GEMME", "Tranception_L"], config)
    dms_ids = list(dms_scores.keys())
    ensemble_data = {'Ensemble1':[], 'Ensemble2':[], 'Ensemble3':[], 'Ensemble4':[]}
    # Create ensembles

    for dms_id in dms_ids:

        ensemble2_score = 0.5*dms_scores[dms_id][config['ESM-IF1']["input_score_name"]] + 0.5*dms_scores[dms_id][config['Tranception_L']["input_score_name"]]
        ensemble_data['Ensemble2'].append(apply_metric_func(metric, dms_scores[dms_id]['DMS_score'].tolist(),
                                                ensemble2_score.tolist()))
        ensemble3_score = 0.5*dms_scores[dms_id][config['ESM-IF1']["input_score_name"]] + 0.5*dms_scores[dms_id][config['GEMME']["input_score_name"]]
        ensemble_data['Ensemble3'].append(apply_metric_func(metric, dms_scores[dms_id]['DMS_score'].tolist(),
                                                ensemble3_score.tolist()))
        ensemble4_score = 0.5*dms_scores[dms_id][config['ESM-IF1']["input_score_name"]] + 0.5*dms_scores[dms_id][config['VESPA']["input_score_name"]]
        ensemble_data['Ensemble4'].append(apply_metric_func(metric, dms_scores[dms_id]['DMS_score'].tolist(),
                                                ensemble4_score.tolist()))
    
        ensemble_data['DMS_id'] = dms_ids
    
    dms_scores = fetch_model_scores(zero_shot_scores_path, dms_substitution_assay_path, ['ESM-IF1', "TranceptEVE_L"], config)
    dms_ids = list(dms_scores.keys())
    for dms_id in dms_ids:
        ensemble1_score = 0.5*dms_scores[dms_id][config['ESM-IF1']["input_score_name"]] + 0.5*dms_scores[dms_id][config['TranceptEVE_L']["input_score_name"]]
        ensemble_data['Ensemble1'].append(apply_metric_func(metric, dms_scores[dms_id]['DMS_score'].tolist(),
                                                ensemble1_score.tolist()))
    return pd.DataFrame(ensemble_data)

def main():

    args = parser.parse_args()
    if not os.path.isdir('ProteinGym'):
        print(f"ProteinGym repo not set up. Please run scripts/setup_proteinGym.sh to set the repository up.")
        sys.exit(1)

    config = {}
    with open("ProteinGym/config.json", "r") as f:
        config = json.load(f)["model_list_zero_shot_substitutions_DMS"]
    zero_shot_score_path = 'ProteinGym/data/zero_shot_substitutions_scores/'
    if not os.path.isdir(zero_shot_score_path):
        print(f"ProteinGym zero-shot scores not found. Please download and extract scores to {zero_shot_score_path}.")
        sys.exit(1)

    dms_assay_path = 'ProteinGym/data/DMS_ProteinGym_substitutions/'
    if not os.path.isdir(dms_assay_path):
        print(f"ProteinGym assays not found. Please download and extract zero-shot substitution assays to {dms_assay_path}.")
        sys.exit(1)

    bm_file = pd.read_csv('assets/DMS_substitutions_Spearman_DMS_level.csv')
    dms_ids = [id for id in bm_file['DMS ID'] if id != 'BRCA2_HUMAN_Erwood_2022_HEK293T']
    
    ensemble_df = create_ensemble_df(dms_assay_path, zero_shot_score_path, config, args.metric)

    ref_file = pd.read_csv("ProteinGym/reference_files/DMS_substitutions.csv")
    ensemble1_score = []
    ensemble2_score = []
    ensemble3_score = []
    ensemble4_score = []
    for dms_id in dms_ids:
        ensemble1_score.append(ensemble_df[ensemble_df['DMS_id'] == dms_id]['Ensemble1'].item())
        ensemble2_score.append(ensemble_df[ensemble_df['DMS_id'] == dms_id]['Ensemble2'].item())
        ensemble3_score.append(ensemble_df[ensemble_df['DMS_id'] == dms_id]['Ensemble3'].item())
        ensemble4_score.append(ensemble_df[ensemble_df['DMS_id'] == dms_id]['Ensemble4'].item())

    ensemble1_df = pd.DataFrame(data={'DMS_id': dms_ids, 'spearmanr': ensemble1_score})
    ensemble1_df = ensemble1_df.merge(ref_file[['DMS_id', 'UniProt_ID', 'coarse_selection_type']], how='left', on='DMS_id')

    ensemble2_df = pd.DataFrame(data={'DMS_id': dms_ids, 'spearmanr': ensemble2_score})
    ensemble2_df = ensemble2_df.merge(ref_file[['DMS_id', 'UniProt_ID', 'coarse_selection_type']], how='left', on='DMS_id')

    ensemble3_df = pd.DataFrame(data={'DMS_id': dms_ids, 'spearmanr': ensemble3_score})
    ensemble3_df = ensemble3_df.merge(ref_file[['DMS_id', 'UniProt_ID', 'coarse_selection_type']], how='left', on='DMS_id')

    ensemble4_df = pd.DataFrame(data={'DMS_id': dms_ids, 'spearmanr': ensemble4_score})
    ensemble4_df = ensemble4_df.merge(ref_file[['DMS_id', 'UniProt_ID', 'coarse_selection_type']], how='left', on='DMS_id')

    print('TranceptEVE + ESM-IF')
    print(ensemble1_df.groupby(['UniProt_ID', 'coarse_selection_type'])['spearmanr'].mean().groupby('coarse_selection_type').mean().round(4))
    print(ensemble1_df.groupby(['UniProt_ID', 'coarse_selection_type'])['spearmanr'].mean().groupby('coarse_selection_type').mean().mean().round(4))

    print('Tranception + ESM-IF')
    print(ensemble2_df.groupby(['UniProt_ID', 'coarse_selection_type'])['spearmanr'].mean().groupby('coarse_selection_type').mean().round(4))
    print(ensemble2_df.groupby(['UniProt_ID', 'coarse_selection_type'])['spearmanr'].mean().groupby('coarse_selection_type').mean().mean().round(4))

    print('GEMME + ESM-IF')
    print(ensemble3_df.groupby(['UniProt_ID', 'coarse_selection_type'])['spearmanr'].mean().groupby('coarse_selection_type').mean().round(4))
    print(ensemble3_df.groupby(['UniProt_ID', 'coarse_selection_type'])['spearmanr'].mean().groupby('coarse_selection_type').mean().mean().round(4))

    print('VESPA + ESM-IF')
    print(ensemble4_df.groupby(['UniProt_ID', 'coarse_selection_type'])['spearmanr'].mean().groupby('coarse_selection_type').mean().round(4))
    print(ensemble4_df.groupby(['UniProt_ID', 'coarse_selection_type'])['spearmanr'].mean().groupby('coarse_selection_type').mean().mean().round(4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metric", type=str, default='spearman')
    main()
