"""Compact data for the film's pictures: copies the saved results of every step into ../src/values.json."""
import json

out = {s: json.load(open(f'files/{s}.json')) for s in
       ['step1', 'step2', 'step3', 'step4', 'step5', 'step6', 'step7', 'exercise']}
json.dump(out, open('../src/values.json', 'w'), indent=1)
print('wrote ../src/values.json')
