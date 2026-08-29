# VALIDATED: never successfully run to completion as of this commit
import pandas as pd
from pathlib import Path
from src.parse.changeset import extract_changeset

def main():
    instances = pd.read_parquet('data/interim/instances_raw.parquet')
    
    records = []
    missing_count = 0
    total = len(instances)
    
    print(f"Processing {total} instances...")
    count = 0
    unique_prs = instances[['repo', 'pr_number', 'head_sha']].drop_duplicates()
    print(f'Distinct PRs to process: {len(unique_prs)}')
    for _, row in unique_prs.iterrows():
        repo = row['repo']
        pr = str(row['pr_number'])
        head_sha = row['head_sha']
        
        cs = extract_changeset(repo, pr, head_sha)
        if cs is None:
            missing_count += 1
            continue
            
        # We store one row per file change? Or one row per PR?
        # "Write changesets.parquet. Report row counts, per-flag counts..."
        # If we need the changed files for RQ1 overlap, it's better to store per-file, or store as a list.
        # But pandas doesn't like lists. Let's store one row per file, and attach the flags to each row.
        # Or store PR-level flags in a separate dataframe?
        # Let's just output PR-level records to a list of dicts, and file-level records?
        # "Write data/interim/changesets.parquet. Report row counts..."
        # I'll store one row per changed file.
        for f in cs.files:
            records.append({
                'repo': repo,
                'pr_number': pr,
                'head_sha': head_sha,
                'filename': f.filename,
                'status': f.status,
                'additions': f.additions,
                'deletions': f.deletions,
                'previous_filename': f.previous_filename,
                'touches_test_file': cs.touches_test_file,
                'touches_build_config': cs.touches_build_config,
                'touches_ci_config': cs.touches_ci_config,
                'is_docs_only': cs.is_docs_only,
                'is_truncated': cs.is_truncated
            })
            
        count += 1
        if count % 1000 == 0:
            print(f"  Processed {count} valid payloads...")
            
    df = pd.DataFrame(records)
    df.to_parquet('data/interim/changesets.parquet')
    
    print(f"Wrote changesets.parquet with {len(df)} rows.")
    print(f"Missing payloads: {missing_count} out of {total} PRs.")
    
    if not df.empty:
        # Group by PR to count PR-level flags
        pr_df = df[['repo', 'pr_number', 'touches_test_file', 'touches_build_config', 'touches_ci_config', 'is_docs_only', 'is_truncated']].drop_duplicates()
        print("\nPer-flag counts (PR level):")
        print(f"  touches_test_file: {pr_df['touches_test_file'].sum()}")
        print(f"  touches_build_config: {pr_df['touches_build_config'].sum()}")
        print(f"  touches_ci_config: {pr_df['touches_ci_config'].sum()}")
        print(f"  is_docs_only: {pr_df['is_docs_only'].sum()}")
        print(f"  is_truncated: {pr_df['is_truncated'].sum()}")
        
if __name__ == "__main__":
    main()
