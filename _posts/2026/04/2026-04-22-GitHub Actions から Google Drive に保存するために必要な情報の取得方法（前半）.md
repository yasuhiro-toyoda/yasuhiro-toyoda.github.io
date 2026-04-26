---
layout: post
title: "GitHub Actions から Google Drive に保存する方法（前半）"
description: "2026-04-22-GitHub Actions から Google Drive に保存するために必要な４つの情報を取得する方法（前半）"
date: 2026-04-21 00:00:00 +0900
updated_at:
category: 開発
tags:
  - dev-memo
excerpt: "2026-04-22-GitHub Actions から Google Drive に保存するために必要な情報の取得方法（前半）"
---

私はgithub actionsでwebスクレイピングをし、Google driveに保存しています。

以前、github actionsの設定とPythonのコードは記事にしましたが、トークンの取得周りは取り扱わなかったので自分の備忘録を兼ねて記事にしておきます。

スクリーンショットが多いので前半後半に分けて公開予定です。

過去の関連記事はこちら
{% include bookmark-card.html
  url="https://musashistudio.com/blog/2026/04/15/GitHub-Actions%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%9F%E7%84%A1%E6%96%99%E3%82%B9%E3%82%AF%E3%83%AC%E3%82%A4%E3%83%94%E3%83%B3%E3%82%B0%E8%A1%93/"
  title="GitHub Actionsを使った無料スクレイピング術"
  description="Python で取得・整形・CSV 出力・保存を分けて、GitHub Actions で回しやすい無料スクレイピング構成を整理します。"
  label="Reference"
%}
{% include bookmark-card.html
  url="https://musashistudio.com/blog/2026/04/16/GitHub-Actions-%E3%81%AE-yml-%E3%81%AF%E4%BD%95%E3%82%92%E6%9B%B8%E3%81%84%E3%81%A6%E3%81%84%E3%82%8B%E3%81%AE%E3%81%8B/"
  title="GitHub Actions の yml は何を書いているのか"
  description="GitHub Actions の workflow yml で何を書くのかを、schedule / runs-on / checkout / secrets / python 実行の順で整理します。"
  label="Reference"
%}

## 今回やること

# **1.Google Cloud 側（前半）**

**⓪Google Cloudアカウント作成**

**① プロジェクト作成**

**② Google Drive API を有効化**

**③ OAuth 同意画面の設定**

**④ OAuth クライアント作成**

**⑤ Refresh Token の取得**

# **2. Google Drive 側（後半）**

**⑥ 保存先フォルダの用意**

**⑦ フォルダIDの取得**

**⑧ 共有設定の確認**

# **3. GitHub 側（後半）**

**⑨ Repository Secrets の登録**

**⑩ workflow yml で env に渡す**

飛ばしがちや設定もありますので、丁寧に解説していきます。

---

# **1.Google Cloud 側**

## **① プロジェクト作成**
1. ブラウザで「google cloud」と検索するか、下記のURLからアクセス
{% include bookmark-card.html
  url="https://cloud.google.com/"
  title="Google Cloud - The cron schedule expression generator"
  description="Google Cloudの公式サイト"
  label="Reference"
%}
2. 
