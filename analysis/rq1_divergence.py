import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def compute_metrics(C, GT):
    if not isinstance(C, set): C = set(C)
    if not isinstance(GT, set): GT = set(GT)
    overlap = C & GT
    precision = len(overlap) / len(C) if C else 0.0
    recall = len(overlap) / len(GT) if GT else 0.0
    jaccard = len(overlap) / len(C | GT) if (C or GT) else 0.0
    return precision, recall, jaccard

def main():
    print("Loading data...")
    outcomes = pd.read_parquet('data/interim/outcomes.parquet')
    binding = pd.read_parquet('data/interim/binding.parquet')
    changesets = pd.read_parquet('data/interim/changesets.parquet')
    cochange = pd.read_parquet('data/interim/cochange.parquet')
    instances = pd.read_parquet('data/interim/instances_raw.parquet')
    
    strict_labels = outcomes[outcomes['split'] == 'strict'].copy()
    strict_labels = pd.merge(strict_labels, instances[['run_id', 'repo', 'pr_number', 'run_started_at']], on=['run_id'], how='inner')
    
    bound = binding[binding['status'] == 'exact'].set_index(['repo', 'test_id'])['resolved_path'].to_dict()
    
    run_to_gt = {}
    for _, row in strict_labels.iterrows():
        key = (row['repo'], row['run_id'])
        tid = row['test_id']
        path = bound.get((row['repo'], tid))
        if path:
            if key not in run_to_gt:
                run_to_gt[key] = set()
            run_to_gt[key].add(path)
            
    pr_to_changed = {}
    for _, row in changesets.iterrows():
        key = (row['repo'], str(row['pr_number']))
        if key not in pr_to_changed:
            pr_to_changed[key] = set()
        pr_to_changed[key].add(row['filename'])
        
    cochange['support'] = cochange['support'].astype(int)
    co_support_map = {}
    for row in cochange.itertuples():
        r = row.repo_full
        f = row.file_a
        s = row.support
        if (r, f) not in co_support_map:
            co_support_map[(r, f)] = []
        co_support_map[(r, f)].append(s)

    cochange_sorted = cochange.sort_values(by=['repo_full', 'file_a', 'conf_a_to_b'], ascending=[True, True, False])
    co_lookup = {}
    for repo, grp in cochange_sorted.groupby('repo_full'):
        co_lookup[repo] = {}
        for fa, subgrp in grp.groupby('file_a'):
            co_lookup[repo][fa] = subgrp['file_b'].tolist()

    valid_runs = strict_labels.drop_duplicates(subset=['run_id'])
    
    # --------------------------------------------------------------------------
    # AXIS 1: APPLICABILITY
    # --------------------------------------------------------------------------
    print("\nAXIS 1 - APPLICABILITY")
    all_changed_files = []
    instance_silent = []
    
    for _, row in valid_runs.iterrows():
        repo = row['repo']
        run_id = row['run_id']
        pr = str(row['pr_number'])
        if (repo, run_id) not in run_to_gt:
            continue
            
        F = pr_to_changed.get((repo, pr), set())
        
        instance_has_partner = False
        for f in F:
            supports = co_support_map.get((repo, f), [])
            partners_ge_3 = sum(1 for s in supports if s >= 3)
            partners_ge_2 = sum(1 for s in supports if s >= 2)
            partners_all = len(supports)
            all_changed_files.append({
                'repo': repo, 'file': f, 
                'ge_3': partners_ge_3, 'ge_2': partners_ge_2, 'all': partners_all
            })
            if partners_all > 0:
                instance_has_partner = True
        instance_silent.append(not instance_has_partner)
        
    df_files = pd.DataFrame(all_changed_files)
    tot = len(df_files)
    ge3_cnt = len(df_files[df_files['ge_3'] > 0])
    ge2_cnt = len(df_files[df_files['ge_2'] > 0])
    print(f"Total changed files in instances with GT: {tot}")
    print(f">=1 partner at support >=3: {ge3_cnt} / {tot} ({ge3_cnt/tot:.1%})")
    print(f">=1 partner at support >=2: {ge2_cnt} / {tot} ({ge2_cnt/tot:.1%})")
    
    bins = [0, 1, 3, 6, 11, np.inf]
    labels = ['0', '1-2', '3-5', '6-10', '11+']
    dist = pd.cut(df_files['all'], bins=bins, labels=labels, right=False)
    print("Distribution of partners-per-changed-file (any support):")
    dist_counts = dist.value_counts().sort_index()
    print(dist_counts)
    
    silent_cnt = sum(instance_silent)
    tot_inst = len(instance_silent)
    print(f"Instances with at least one changed file with any partner: {tot_inst - silent_cnt} / {tot_inst} ({(tot_inst - silent_cnt)/tot_inst:.1%})")
    print(f"Proxy is entirely silent on {silent_cnt} / {tot_inst} ({silent_cnt/tot_inst:.1%}) of instances.")
    
    # --------------------------------------------------------------------------
    # AXIS 2: ACCURACY & BASELINES
    # --------------------------------------------------------------------------
    print("\nAXIS 2 - ACCURACY & NULL BASELINES (conditional on proxy firing)")
    all_outcomes = pd.merge(outcomes, instances[['run_id', 'repo', 'run_started_at']], on='run_id', how='inner')
    hist_all = all_outcomes.copy()
    hist_all['resolved_path'] = hist_all.apply(lambda r: bound.get((r['repo'], r['test_id'])), axis=1)
    hist_all = hist_all.dropna(subset=['resolved_path'])
    
    def evaluate_k(k):
        results_co = []
        results_b1 = []
        results_b2 = []
        
        for _, row in valid_runs.iterrows():
            repo = row['repo']
            run_id = row['run_id']
            pr = str(row['pr_number'])
            run_time = row['run_started_at']
            
            GT = run_to_gt.get((repo, run_id))
            if not GT: continue
            
            F = pr_to_changed.get((repo, pr))
            if not F: continue
            
            C_co = set()
            if repo in co_lookup:
                for f in F:
                    if f in co_lookup[repo]:
                        C_co.update(co_lookup[repo][f][:k])
                C_co = C_co - F
            
            if len(C_co) == 0:
                # Conditional on proxy firing
                continue
                
            p, r, j = compute_metrics(C_co, GT)
            results_co.append({'precision': p, 'recall': r, 'jaccard': j, 'predicted_size': len(C_co)})
            
            # Baseline 1: tests in F
            p1, r1, j1 = compute_metrics(F, GT)
            results_b1.append({'precision': p1, 'recall': r1, 'jaccard': j1, 'predicted_size': len(F)})
            
            # Baseline 2: top k failing tests prior to run_time
            hist = hist_all[(hist_all['repo'] == repo) & (hist_all['run_started_at'] < run_time)]
            if len(hist) > 0:
                top_k = hist['resolved_path'].value_counts().head(k).index.tolist()
                C_b2 = set(top_k)
            else:
                C_b2 = set()
                
            p2, r2, j2 = compute_metrics(C_b2, GT)
            results_b2.append({'precision': p2, 'recall': r2, 'jaccard': j2, 'predicted_size': len(C_b2)})

        return pd.DataFrame(results_co), pd.DataFrame(results_b1), pd.DataFrame(results_b2)

    k_vals = [5, 10, 20]
    co_perf, b1_perf, b2_perf = [], [], []
    for k in k_vals:
        df_co, df_b1, df_b2 = evaluate_k(k)
        n = len(df_co)
        print(f"\n=== k={k} (n={n}) ===")
        if n > 0:
            print(f"Co-change: Precision: {df_co['precision'].mean():.3f}, Recall: {df_co['recall'].mean():.3f}, Jaccard: {df_co['jaccard'].mean():.3f} (Med size: {df_co['predicted_size'].median()})")
            print(f"Baseline 1 (Changeset): Precision: {df_b1['precision'].mean():.3f}, Recall: {df_b1['recall'].mean():.3f}, Jaccard: {df_b1['jaccard'].mean():.3f} (Med size: {df_b1['predicted_size'].median()})")
            print(f"Baseline 2 (Historical Top-k): Precision: {df_b2['precision'].mean():.3f}, Recall: {df_b2['recall'].mean():.3f}, Jaccard: {df_b2['jaccard'].mean():.3f} (Med size: {df_b2['predicted_size'].median()})")
            
            co_perf.append((df_co['precision'].mean(), df_co['recall'].mean()))
            b1_perf.append((df_b1['precision'].mean(), df_b1['recall'].mean()))
            b2_perf.append((df_b2['precision'].mean(), df_b2['recall'].mean()))

    # --------------------------------------------------------------------------
    # FIGURES
    # --------------------------------------------------------------------------
    os.makedirs('paper/generated', exist_ok=True)
    
    # Fig 1
    plt.figure(figsize=(8, 5))
    dist_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Applicability: Distribution of Partners-per-Changed-File')
    plt.xlabel('Number of Co-change Partners')
    plt.ylabel('Number of Changed Files')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('paper/generated/fig1_applicability.pdf')
    plt.close()
    
    # Fig 2
    if len(co_perf) > 0:
        plt.figure(figsize=(8, 5))
        ks = [str(k) for k in k_vals]
        
        # Plot recall
        plt.plot(ks, [x[1] for x in co_perf], marker='o', label='Co-change Recall')
        plt.plot(ks, [x[1] for x in b1_perf], marker='s', linestyle='--', label='Baseline 1 (Changeset) Recall')
        plt.plot(ks, [x[1] for x in b2_perf], marker='^', linestyle=':', label='Baseline 2 (Hist Top-k) Recall')
        
        plt.title('Accuracy vs k (Conditional on Proxy Firing)')
        plt.xlabel('k (Top-k recommendations)')
        plt.ylabel('Recall')
        plt.ylim(0, 1.0)
        plt.legend()
        plt.tight_layout()
        plt.savefig('paper/generated/fig2_accuracy.pdf')
        plt.close()
        print("\nGenerated paper/generated/fig1_applicability.pdf and paper/generated/fig2_accuracy.pdf")

if __name__ == '__main__':
    main()
