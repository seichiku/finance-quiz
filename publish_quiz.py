#!/usr/bin/env python3
"""小テスト公開スクリプト（2026-10-08）

questions.json（v2）を検証 → git commit & push（main） → GitHub Pages 反映確認 → Chatwork（せいこ↔竹中DM）へ案内を1通。
使い方: python3 publish_quiz.py [--dry-run] [--no-post] [--no-push]
  --dry-run : 検証と本文表示だけ（push も投稿もしない）
  --no-post : push はするが Chatwork へ投稿しない
  --no-push : Chatwork 投稿だけ（push 済みのとき）
終了: 0=正常 / 1=検証NG / 2=push失敗 / 3=Chatwork失敗（pushは済み）
"""
import argparse, datetime, json, os, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
QFILE = os.path.join(HERE, 'questions.json')
ROOM = '445977352'          # せいこ↔竹中DM
LP = 'https://seichiku.github.io/finance-quiz/'
POST_SH = os.path.expanduser('~/.claude/skills/chatwork-post/post.sh')
TITLES = {'finance': '📈 今日の金融', 'mikey': '🎓 マイキークラブ', 'sanrui': '📜 今日の三類法'}
WD = '月火水木金土日'

def fail(msg, code):
    print(json.dumps({'error': msg}, ensure_ascii=False)); sys.exit(code)

def validate(d):
    errs = []
    if d.get('version') != 2: errs.append('version は 2')
    try: datetime.date.fromisoformat(d.get('date', ''))
    except Exception: errs.append('date は YYYY-MM-DD')
    sets = d.get('sets')
    if not isinstance(sets, list) or not (1 <= len(sets) <= 3): errs.append('sets は1〜3個')
    seen = set()
    for s in sets or []:
        k = s.get('key')
        if k not in TITLES: errs.append(f'key が不正: {k}')
        if k in seen: errs.append(f'key 重複: {k}')
        seen.add(k)
        qs = s.get('questions')
        if not isinstance(qs, list) or len(qs) != 5: errs.append(f'{k}: questions は5問')
        for i, q in enumerate(qs or [], 1):
            if not q.get('q'): errs.append(f'{k} Q{i}: q が空')
            c = q.get('c')
            if not isinstance(c, list) or len(c) != 4 or any(not str(x).strip() for x in c): errs.append(f'{k} Q{i}: c は4択')
            if q.get('a') not in (1, 2, 3, 4): errs.append(f'{k} Q{i}: a は1〜4')
            if not q.get('exp'): errs.append(f'{k} Q{i}: exp が空')
        if qs and len({q.get('a') for q in qs}) == 1: errs.append(f'{k}: 正解番号が全問同じ')
    return errs

def body_for(d):
    dt = datetime.date.fromisoformat(d['date'])
    label = d.get('label') or f"{dt.month}/{dt.day}({WD[dt.weekday()]})"
    lines = [f"[info][title]📝 今日の小テスト {label}[/title]"]
    for s in d['sets']:
        rng = f"（{s['range']}）" if s.get('range') else ''
        lines.append(f"{TITLES[s['key']]} {len(s['questions'])}問{rng}")
    missing = [TITLES[k] for k in ('finance', 'mikey', 'sanrui') if k not in {s['key'] for s in d['sets']}]
    if missing: lines.append('お休み: ' + '・'.join(missing))
    lines.append(f"解く→ {LP}")
    q1 = d['sets'][0]['questions'][0]
    lines.append(f"第1問: {q1['q']}")
    lines.append('[/info]')
    return '\n'.join(lines)

def git(*args):
    return subprocess.run(['git', '-C', HERE, *args], capture_output=True, text=True)

def push(d):
    if git('rev-parse', '--abbrev-ref', 'HEAD').stdout.strip() != 'main':
        r = git('checkout', 'main')
        if r.returncode: fail('git checkout main 失敗: ' + r.stderr[-300:], 2)
    git('add', 'questions.json')
    if not git('diff', '--cached', '--quiet').returncode:
        print('変更なし（commit スキップ）')
    else:
        r = git('commit', '-m', f"小テスト自動更新: {d['date']}")
        if r.returncode: fail('git commit 失敗: ' + r.stderr[-300:], 2)
    r = git('push', 'origin', 'main')
    if r.returncode: fail('git push 失敗: ' + r.stderr[-300:], 2)
    print('push OK')
    # Pages 反映待ち（最大3分）
    for _ in range(18):
        try:
            with urllib.request.urlopen(f'{LP}questions.json?t={int(time.time())}', timeout=20) as r:
                if json.load(r).get('date') == d['date']:
                    print('Pages 反映確認 OK'); return True
        except Exception: pass
        time.sleep(10)
    print('Pages 反映を3分以内に確認できず（push自体は成功）'); return False

def post(body):
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write(body); p = f.name
    for _ in range(2):
        r = subprocess.run(['bash', POST_SH, ROOM, p], capture_output=True, text=True)
        if r.returncode == 0: os.unlink(p); return True
    os.unlink(p); print(r.stdout[-300:], r.stderr[-300:]); return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--no-post', action='store_true'); ap.add_argument('--no-push', action='store_true')
    a = ap.parse_args()
    try: d = json.load(open(QFILE, encoding='utf-8'))
    except Exception as e: fail(f'questions.json を読めない: {e}', 1)
    errs = validate(d)
    if errs: fail('検証NG: ' + ' / '.join(errs), 1)
    print(f"検証OK: date={d['date']} sets={[ (s['key'], len(s['questions'])) for s in d['sets'] ]}")
    body = body_for(d)
    if a.dry_run:
        print('--- (dry-run) Chatwork本文 ---'); print(body); return 0
    if not a.no_push: push(d)
    if not a.no_post:
        if not post(body): fail('Chatwork投稿失敗', 3)
        print('Chatwork投稿 OK')
    return 0

if __name__ == '__main__':
    sys.exit(main())
