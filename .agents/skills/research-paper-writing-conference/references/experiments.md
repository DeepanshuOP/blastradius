# Experiments Writing Guide

## Goal

Convince reviewers with evidence for effectiveness, causality, and practical value.

## Three Core Questions

1. Is the method better than strong, relevant baselines?
2. Which modules/design choices cause the gain?
3. How far does the method generalize, and where does it fail?

## Experiment Planning

Map each important claim to at least one experiment that can actually support it.

- Main comparisons -> effectiveness claims.
- Ablations -> module/design claims.
- Stress tests / challenging settings -> robustness and scope claims.
- Qualitative results -> behavioral or failure-case claims.

## Fair Comparison

Document the dataset, split, preprocessing, evaluation metric, and protocol used for each important comparison.

Do not treat a literature-reported value as directly comparable when the protocol differs materially.

## Figures and Tables

- One table, one message.
- Put the table caption/head above the table.
- Put figure captions below figures.
- Use readable, minimal-ink formatting.
- Keep metric direction and units explicit.
- Use consistent numeric precision.
- Captions should explain setting and notation; the main text should carry the detailed interpretation.

## Ablation Package

Ablations should test the paper's real design claims, not arbitrary knobs added to inflate the experimental section.

## Experimental Rigor Checklist

- Are baselines relevant and strong enough?
- Are metrics standard and sufficient?
- Does every major design claim have a matching ablation or analysis?
- Are the Abstract/Introduction claims supported by actual reported results?
- Are limitations and failure cases visible?
