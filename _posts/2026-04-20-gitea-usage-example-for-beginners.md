---
layout: post
title: "Gitea入門　使い方（実例あり）"
description: "Giteaでリポジトリを作成し、ローカルで編集したファイルをGitコマンドでpushする流れを実例付きで整理します。"
date: 2026-04-20 00:04:00 +0900
updated_at:
category: 開発
tags:
  - gitea
  - beginner
  - workflow
  - dev-memo
excerpt: "Giteaでリポジトリを作り、`git clone` `git add` `git commit` `git push` で変更を反映するまでを、短い実例で確認します。"
---
## この記事を読んでわかること
> - **Giteaでリポジトリを作って使い始める流れ**
> - **ローカル作業とGitea画面がどうつながるか**
> - **`git clone` `git add` `git commit` `git push` の実例**

## はじめに

Giteaを導入できたら、次に知りたいのは「実際にどう使うのか」だと思います。
ただ、最初から多機能な使い方を覚えようとすると少し重たく感じます。

そこで今回は、**Giteaでリポジトリを1つ作り、ローカルでファイルを追加して push する**ところまでに絞って見ていきます。
まずはこの流れがわかれば、日常的な使い方の土台は十分です。

## 本文

### 今回の例

今回は、Giteaが `http://localhost:3000` で動いている前提で進めます。
作るリポジトリ名は `sample-note` とします。

### まずはGitea側でリポジトリを作る

Giteaにログインしたら、新規作成メニューからリポジトリを作成します。

設定は最初なら次のような内容で十分です。

- リポジトリ名: `sample-note`
- 公開設定: リポジトリをプライベートにするにチェック(サンプルなので)
- README を作成: あり

README を最初に作っておくと、あとで `git clone` しやすくなります。

### ローカルに clone する

リポジトリ作成後、Gitea 画面に表示される HTTPS か SSH のURLをコピーします。
今回は HTTPS の例で進めます。

```powershell
git clone http://localhost:3000/ユーザー名/sample-note.git
cd sample-note
```

これで、Gitea上のリポジトリを自分のPCに取り込めます。

### ファイルを追加して commit する

次に、テスト用のファイルを1つ追加してみます。
PowerShell なら、次のように作れます。

```powershell
Set-Content memo.txt "Giteaの動作確認です"
git status
git add memo.txt
git commit -m "memo.txtを追加"
```

ここでやっていることは単純です。

- `git status` で変更を確認する
- `git add` でコミット対象に入れる
- `git commit` で履歴として記録する

### Giteaへ push する

コミットできたら、Giteaへ送ります。

```powershell
git push
```

初回 clone 済みのリポジトリなら、これだけでそのまま反映できることが多いです。
push が終わったら、Gitea のブラウザ画面を更新してみてください。

`memo.txt` が見えるようになっていれば成功です。

### Gitea画面ではどこを見るか

初心者のうちは、Gitea画面では次の3か所を見れば十分です。

- Files: 今あるファイルを確認する
- Commits: 変更履歴を見る
- Branches: 今どのブランチがあるかを見る

まずは「ローカルで commit した内容が、push 後にブラウザでも見える」とつながればOKです。

### 慣れてきたら次に覚えたいこと

基本の流れに慣れてきたら、次はこのあたりを少しずつ足すと使いやすくなります。

- ブランチを分けて作業する
- Pull Request を使う
- Issue で作業内容をメモする

ただし最初は、**作る、clone する、commit する、push する**の流れだけでも十分です。

## まとめ

Giteaの使い方は、最初から難しく考えなくて大丈夫です。
**Giteaでリポジトリを作り、ローカルで編集し、Gitコマンドで push する。**
まずはこの一連の流れを体験することが大切です。

1回でも自分の手で反映できると、GiteaとGitの役割がかなり見えやすくなります。
そのあとでブランチやPull Requestに進むと、理解が自然につながります。
