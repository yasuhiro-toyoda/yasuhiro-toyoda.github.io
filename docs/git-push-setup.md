# `git push` できないときの設定手順

このリポジトリでは現在 `git remote -v` の結果が空で、push先が未設定です。

## 1) リモートを追加する

GitHub なら通常は `origin` を作成します。

```bash
git remote add origin <YOUR_REPO_URL>
```

例:

```bash
git remote add origin git@github.com:<user>/<repo>.git
# または
git remote add origin https://github.com/<user>/<repo>.git
```

## 2) ブランチを初回 push する

現在ブランチを upstream 付きで push します。

```bash
git push -u origin $(git branch --show-current)
```

## 3) 2回目以降

upstream が設定された後は以下だけで push できます。

```bash
git push
```

## よくあるエラー

- `No configured push destination`
  - 原因: remote 未設定。上記 1) を実施。
- `Permission denied (publickey)`
  - 原因: SSH鍵未設定。SSH鍵登録か HTTPS 利用に切替。
- `Repository not found`
  - 原因: URL誤り or 権限不足。URLとアクセス権を確認。
