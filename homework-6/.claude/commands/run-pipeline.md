Run the multi-agent banking pipeline end-to-end.

Steps:
1. Check that sample-transactions.json exists in the project root
2. Clear all shared/ directories (input/, processing/, output/, results/)
3. Run the pipeline: `python3 integrator.py`
4. Show a summary of results from shared/results/
5. Report any transactions that were rejected and why
6. Report any transactions flagged for review and their risk score

