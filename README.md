# finance-quiz（今週の金融テスト）

竹中さん専用の週次・金融クイズLP。「毎朝の金融お題」（Notion）で1週間に学んだ内容を、日曜にルールクイズ風のカードUIでテストして定着を確認する。

- LP: https://seichiku.github.io/finance-quiz/
- 出題データ: `questions.json`（毎週日曜、cloud routine がその週のNotionお題から10問を自動生成して上書き）
- サーバー無し・ログインなし。LPは同じ場所の `questions.json` を読むだけ。自己ベストは端末のlocalStorageに保存。

## questions.json の形

```json
{
  "week": "2026-07-13〜07-19",
  "generated": "2026-07-20",
  "questions": [
    { "id": "q1", "cat": "指標・バリュエーション", "q": "…設問…",
      "c": ["選択肢1","選択肢2","選択肢3","選択肢4"],
      "a": 2, "exp": "…解説…", "src": "Day5 …", "url": "https://app.notion.com/p/…" }
  ]
}
```

- `a` は正解の選択肢番号（1始まり）
- 更新は cloud routine「📈 週次の金融テスト（問題自動生成）」が questions.json をコミット＆プッシュ→GitHub Pagesが反映
