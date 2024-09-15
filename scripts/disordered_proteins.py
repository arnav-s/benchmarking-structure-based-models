import pandas as pd

EXPECTED_PROTEIN_GYM = 186
EXPECTED_DISPROT = 16695


def main():
    uniprot_df = pd.read_csv('assets/uniprot_idmapping_2024_09_13.tsv', sep='\t')
    assert len(uniprot_df) == EXPECTED_PROTEIN_GYM

    disprot_df = pd.read_csv('assets/DisProt_release_2024_06_with_ambiguous_evidences_with_evidences_marked_as_obsolete.tsv', sep='\t')
    assert len(disprot_df) == EXPECTED_DISPROT
    # Remove obsolete evidence
    disprot_df['obsolete'].fillna(False, inplace=True)
    disprot_df = disprot_df[~disprot_df['obsolete']]

    common_ids = set(uniprot_df['Entry']).intersection(set(disprot_df['acc']))
    print(f'{len(common_ids)} of {EXPECTED_PROTEIN_GYM} unique UniProt IDs from Protein Gym are in DisProt:')
    for common_id in sorted(common_ids):
        print(common_id)


if __name__ == "__main__":
    main()
