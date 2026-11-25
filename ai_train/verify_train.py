import importlib.util, sys, os, re, subprocess, tempfile
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lt', os.path.join(here, 'lessons_train.py'))
lt = importlib.util.module_from_spec(spec); spec.loader.exec_module(lt)
src = open(os.path.join(here, '..', 'learn_python.py'), encoding='utf-8').read()
start = src.index('def norm(text):'); end = src.index('def load_state():')
ns = {'re': re, 'os': os, 'subprocess': subprocess, 'sys': sys, 'tempfile': tempfile}
exec(src[start:end], ns)
bad = []; n = 0
for l in lt.LESSONS:
    for k, s in enumerate(l['steps']):
        n += 1
        code = "\n".join(x['write'] for x in l['steps'][:k + 1])
        ok, msg, out = ns['check_step'](s, code)
        if not ok:
            bad.append((l['id'], k + 1, msg[:300], out[-300:]))
print('steps', n, 'failed', len(bad))
for b in bad:
    print(b)
