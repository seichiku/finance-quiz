# finance-quiz（今日の小テスト）

竹中さん専用の学習小テストLP。火・木・土の10時に、直近で学んだ3教材から各5問の4択を自動出題する（2026-10-08に週次12問テストから移行）。

- LP: https://seichiku.github.io/finance-quiz/ （3タブ＝📈今日の金融／🎓マイキークラブ／📜今日の三類法）
- 出題データ: `questions.json`（v2）。ローカル定期タスク `gakushu-quiz`（火木土10:00）が Notion の教材から生成して上書き
- 公開: `publish_quiz.py` が検証 → commit & push(main) → Pages 反映確認 → Chatwork（せいこ↔竹中DM）へ案内1通
- サーバー無し・ログインなし。自己ベストは端末の localStorage（`fq2_<date>_<key>`）

## questions.json（v2）

```json
{
  "version": 2,
  "date": "2026-10-10",
  "label": "10/10(土)",
  "generated": "2026-10-10T10:05+09:00",
  "sets": [
    { "key": "finance", "title": "📈 今日の金融", "range": "Day1〜2（10/9〜10/10）",
      "questions": [
        { "id": "f1", "cat": "指標・バリュエーション", "q": "…設問…",
          "c": ["選択肢1","選択肢2","選択肢3","選択肢4"],
          "a": 2, "exp": "…解説…", "src": "Day2 PERって何？", "url": "https://app.notion.com/p/…" }
      ] },
    { "key": "mikey",  "title": "🎓 マイキークラブ", "range": "10/9(金) 講義", "questions": [] },
    { "key": "sanrui", "title": "📜 今日の三類法", "range": "Day3〜4（10/9〜10/10）", "questions": [] }
  ]
}
```

- `key` は finance / mikey / sanrui。教材が無いセットは配列から外す（1〜3セット）
- 各セット5問。`a` は正解番号（1始まり）
- `python3 publish_quiz.py --dry-run` で検証と Chatwork 本文の確認だけできる

## 旧構成（〜2026-10-08）

毎週日曜のクラウド routine が12問（金融6＋マイキー6）を生成していた。8/11以降は `claude/awesome-volta-*` ブランチへ push されて main に届いていなかった（LP未更新の原因）。routine は廃止（無効化）済み。
