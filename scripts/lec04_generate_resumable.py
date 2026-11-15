import json
import time
from pathlib import Path
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai import DeferredToolRequests
from app.agent import agent, build_model

path = Path('data/eval/my_cases.jsonl')
cases = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
model = build_model()
for case in cases:
    if case['answer']:
        continue
    for attempt in range(4):
        try:
            result = agent.run_sync(case['question'], model=model)
            if isinstance(result.output, DeferredToolRequests):
                raise RuntimeError(f"Case {case['id']} requested approval and needs review; no actions were approved")
            case['answer'] = str(result.output)
            path.write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in cases), encoding='utf-8')
            print('generated', case['id'], flush=True)
            break
        except ModelHTTPError as exc:
            if exc.status_code not in (429, 503) or attempt == 3:
                raise
            print(f"retry {case['id']} after HTTP {exc.status_code}", flush=True)
            time.sleep(30)
    time.sleep(4)
print('completed', len(cases), 'cases')
