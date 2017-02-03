# evaluation

Evaluation and agreement scripts for the DISCOSUMO project. Each evaluation script takes both manual annotations as automatic summarization output. The formatting of these files is highly project-specific. However, the evaluation functions for precision, recall, ROUGE, Jaccard, Cohen's kappa and Fleiss' kappa may be applicable to other domains too.

- The script `agreement_and_eval.pl` also implements three baselines: random, position and length.
- The script `eval.pl` is the only script that assumes that the ground truth labels are in the featurefile (also for the oracle ranking) and therefore only takes one argument.
- The script `agreement_fleisskappa.py` does not evaluate but only implements Fleiss' Kappa, and takes only the manual annotations as input.

The `postids_per_thread.queries.txt`, `106long20threads.postfeats.norm.out` and `106long20threads.threadfeats.out` are needed for some of the scripts to know the post ids per thread or number of posts per thread.