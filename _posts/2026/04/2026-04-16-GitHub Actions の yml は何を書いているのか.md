---
layout: post
title: "GitHub Actions の yml は何を書いているのか"
description: "GitHub Actions の workflow yml の役割を整理し、Repository Secretsの登録手順をスクリーンショット付きで解説します。"
date: 2026-04-16 12:00:00 +0900
updated_at: 2026-10-04 14:00:00 +0900
category: 開発
tags:
  - workflow
  - beginner
  - dev-memo
thumbnail: /assets/images/blog/2026-04-16-github-actions-yml/thumbnail.png
thumbnail_alt: "GitHub Actionsのymlの読み方。設定を読む人物と時計・鍵を描いたイラスト"
excerpt: "GitHub Actions の yml の読み方と、Secretsを画面から登録してPythonに渡すまでの流れを整理します。"
---
{% assign related_scraping_url = '/blog/2026/04/16/GitHub-Actionsを使った無料スクレイピング術/' | relative_url %}
{% include bookmark-card.html
  url=related_scraping_url
  title="GitHub Actionsを使った無料スクレイピング術"
  description="スクレイピング全体の構成から見たい場合は、こちらを先に読むと流れがつかみやすいです。"
  label="元記事"
  domain="Musashi Digital Studio"
%}

GitHub Actions の `workflow yml` は、見た目は短いですが役割がはっきりしています。

この記事では「いつ動かすか」「どんな環境で動かすか」「Secrets をどう渡すか」「最後に何を実行するか」に分けて見ていきます。

## 今回見る yml

{% raw %}
```yaml
name: Scheduled Scraper

on:
  schedule:
    - cron: "0 * * * *"
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run scraper
        env:
          GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
          GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
          GOOGLE_REFRESH_TOKEN: ${{ secrets.GOOGLE_REFRESH_TOKEN }}
          GOOGLE_DRIVE_FOLDER_ID: ${{ secrets.GOOGLE_DRIVE_FOLDER_ID }}
        run: python main.py
```
{% endraw %}

見た目は短いですが、それぞれ意味があります。

## on: は実行タイミングを決める

```yaml
on:
  schedule:
    - cron: "0 * * * *"
  workflow_dispatch:
```

ここでは、ワークフローを**「定期実行」**するか、**「手動実行」**するかを決めています。

- `schedule`: cron 形式で自動実行
- `workflow_dispatch`: GitHub の画面から手動実行

最初のうちは `workflow_dispatch` を入れておくのがおすすめです。

定期実行だけにすると、設定した時間まで実行されずデバッグが遅々として進みません。

{% include bookmark-card.html
  url="https://crontab.guru/"
  title="Crontab.guru - The cron schedule expression generator"
  description="cron 式を人間向けに確認できる定番サイト。GitHub Actions の schedule を書くときに便利です。"
  label="Reference"
%}

{% capture schedule_notice %}
定期実行は、設定した時刻どおりに毎回ぴったり動くとは限りません。

GitHub Actionsの負荷が高い時間帯、特に毎時0分付近では、実行が遅れることがあります。負荷が十分に高い場合は、待機中のジョブが破棄される場合もあります。毎時0分を避けた時刻にすることも対策の1つです。[GitHub公式のscheduleの注意点](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)も確認してください。
{% endcapture %}
{% include callout.html type="warning" title="schedule の注意点" content=schedule_notice %}

## runs-on は実行環境を決める

`runs-on: ubuntu-latest`

これは GitHub が用意している Linux 環境で動かす、という意味です。

Python のスクレイピング用途なら、まずはこれで十分です。

特別な理由がない限り、最初は `ubuntu-latest` で問題ありません。

## actions/checkout はリポジトリを取得する

`uses: actions/checkout@v4`

これは実行対象のリポジトリをランナー上に展開するステップです。

これがないと、`main.py` も `requirements.txt` も見つかりません。

## actions/setup-python で Python を入れる

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
```

ここでは Python のバージョンを指定しています。

ローカルと Actions で Python のバージョンがズレると、ライブラリや構文で事故ることがあります。

自分の開発環境とそろえておくのが基本です。

## 依存ライブラリをインストールする

```yaml
- name: Install dependencies
  run: pip install -r requirements.txt
```

ここでは `requirements.txt` に書いたライブラリを一括で入れています。

たとえば今回のような構成なら、次のようなライブラリが入ります。

- `requests`
- `pandas`
- `lxml`
- `google-api-python-client`
- `google-auth`

このステップがあることで、毎回クリーンな GitHub Actions 環境でも同じ依存関係を再現できます。

## GitHubの画面でSecretsを登録する

`yml` にSecretsの参照を書く前に、GitHub側に値を登録しておきます。ここでは、上のサンプルで使う4つの値を **Repository secrets** に登録します。

掲載画面は2026年4月に撮影したものです。アカウント名・リポジトリ名・URL・プロフィール画像などが写る範囲は切り取り、認証情報やフォルダIDの実際の値は掲載していません。

### 1. SettingsからActionsのSecretsを開く

対象リポジトリの **Settings** を開き、左側の **Secrets and variables → Actions** を選びます。リポジトリ上部にもActionsタブがありますが、Secretsの登録先はSettings内です。

![Settingsの左メニューでSecrets and variablesを展開し、Actionsを選べる状態](/assets/images/blog/2026-04-16-github-actions-yml/secrets-menu.png)

### 2. New repository secretを選ぶ

**Secrets** タブの **Repository secrets** にある **New repository secret** を押します。上にあるEnvironment secretsとは登録先が異なるので、今回はRepository secretsを使います。

![SecretsタブにあるRepository secretsの一覧とNew repository secretボタン](/assets/images/blog/2026-04-16-github-actions-yml/repository-secrets.png)

この画面では、Google認証用の3件がすでに登録されています。続いて `GOOGLE_DRIVE_FOLDER_ID` を追加する例で説明します。初めて設定する場合は、次の4件を1件ずつ登録します。

| Nameに入れる名前 | Secretに入れる値 |
| --- | --- |
| `GOOGLE_CLIENT_ID` | 使用するOAuthクライアントのクライアントID |
| `GOOGLE_CLIENT_SECRET` | そのOAuthクライアントのクライアントシークレット |
| `GOOGLE_REFRESH_TOKEN` | Googleへの認証で取得したリフレッシュトークン |
| `GOOGLE_DRIVE_FOLDER_ID` | 保存先のGoogle DriveフォルダID |

これらの名前は、この記事のサンプルに合わせたものです。GitHubが自動で値を発行するわけではないので、Google側で準備した値を登録します。

値の取得から始める場合は、[Google Drive APIのOAuth設定]({% post_url 2026/10/2026-10-04-google-drive-api-oauth %})で、クライアント作成とリフレッシュトークンの準備を説明しています。

### 3. NameとSecretを入力して保存する

**Name** は `yml` から参照するための名前、**Secret** は保存する実際の値です。たとえばNameに `GOOGLE_DRIVE_FOLDER_ID`、Secretに保存先のフォルダIDを入力し、**Add secret** を押します。

![New secretフォームでNameにGOOGLE_DRIVE_FOLDER_IDを入力した状態。Secret欄は未入力](/assets/images/blog/2026-04-16-github-actions-yml/new-secret.png)

画像のSecret欄は未入力です。実際に保存するときは自分の値を入力してください。登録後は一覧に戻り、必要な4つの名前がそろっていることを確認します。

操作の詳細は[GitHub公式ドキュメント「GitHub Actionsでのシークレットの使用」](https://docs.github.com/ja/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)でも確認できます。

## env: で Secrets を Python に渡す

{% raw %}
```yaml
env:
  GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
  GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
  GOOGLE_REFRESH_TOKEN: ${{ secrets.GOOGLE_REFRESH_TOKEN }}
  GOOGLE_DRIVE_FOLDER_ID: ${{ secrets.GOOGLE_DRIVE_FOLDER_ID }}
```
{% endraw %}

ここはかなり大事です。

GitHub Actions では、リポジトリに登録した Secrets を `env:` 経由で実行プロセスに渡せます。

Python 側では `os.environ["..."]` で受け取ります。

つまり、`yml` と Python の役割分担はこうです。

- `yml`: Secrets を安全に渡す
- Python: 環境変数として受け取って使う

たとえば `GOOGLE_CLIENT_ID` の行では、左側がPythonに渡す環境変数名、右側の `secrets.GOOGLE_CLIENT_ID` がGitHubに登録したSecretの参照です。上で登録したNameと、`secrets.` の後ろの名前をそろえます。

Secretが未登録だったり、参照する名前を間違えたりすると、その参照は空文字列になります。認証エラーが出たら、まず登録先のリポジトリと名前の対応を確認します。

この構造なら、認証情報の値を `yml` やPythonのソースコードに直接書かずに済みます。ただし、確認のために `print()` や `echo` で値を出力しないようにします。実行ログやスクリーンショットにも認証情報を残さないことが大切です。

## 最後に python main.py を実行する

`run: python main.py`

ここでやっと本体を動かします。

大事なのは、`workflow yml` に細かいロジックを書きすぎないことです。

ロジックは Python 側に寄せて、`yml` は「どういう環境で」「いつ」「何を実行するか」だけを書くようにした方が管理しやすいです。

## yml でやりすぎないほうがいい理由

設定ファイルに分岐や変換ロジックを寄せすぎると、次のような問題が起きやすくなります。

- 動作確認がしづらい
- 途中失敗したときの切り分けがしづらい
- ローカル実行との差分が大きくなる
- 記事化しづらくなる

`yml` は実行基盤の説明書、Python は処理本体、と役割を切り分けておくと保守しやすくなります。

## まとめ

{% capture yml_points %}
- `on:` で実行タイミングを決める
- `runs-on` と `setup-python` で実行環境をそろえる
- SettingsでRepository Secretsを登録し、Nameと参照名をそろえる
- `env:` で Secrets を渡し、処理本体は Python に寄せる
{% endcapture %}
{% include callout.html type="tip" title="今回のポイント" content=yml_points %}

GitHub Actions の `workflow yml` は、見た目よりずっと役割が明確です。

`yml` では実行条件と環境づくりに専念して、実際の処理は Python に寄せておくと、壊れにくく読みやすい構成になります。
