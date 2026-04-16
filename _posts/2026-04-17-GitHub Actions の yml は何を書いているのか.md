---
layout: post
title: "GitHub Actions の yml は何を書いているのか"
description: "GitHub Actions の workflow yml で何を書くのかを、schedule / runs-on / checkout / secrets / python 実行の順で整理します。"
date: 2026-04-16 12:00:00 +0900
updated_at:
category: 開発
tags:
  - workflow
  - beginner
  - dev-memo
excerpt: "GitHub Actions の yml は、いつ動かすか、どんな環境で動かすか、Secrets をどう渡すかを書くための設定ファイルです。"
---
{% capture related_scraping %}
スクレイピング全体の構成から見たい場合は、[GitHub Actionsを使った無料スクレイピング術]({{ '/blog/2026/04/16/GitHub-Actionsを使った無料スクレイピング術/' | relative_url }}) を先に読むと流れがつかみやすいです。
{% endcapture %}
{% include callout.html type="info" title="元記事はこちら" icon="🔗" content=related_scraping %}

GitHub Actions の `workflow yml` は、見た目は短いですが役割がはっきりしています。

この記事では「いつ動かすか」「どんな環境で動かすか」「Secrets をどう渡すか」「最後に何を実行するか」に分けて見ていきます。

## 今回見る yml

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

アクセス集中の時間帯は遅延したり、特に午前7時から11時ごろまでは実行されないこともあります。
{% endcapture %}
{% include callout.html type="warning" title="schedule の注意点" icon="⚠️" content=schedule_notice %}

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

## env: で Secrets を Python に渡す

```yaml
env:
  GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
  GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
  GOOGLE_REFRESH_TOKEN: ${{ secrets.GOOGLE_REFRESH_TOKEN }}
  GOOGLE_DRIVE_FOLDER_ID: ${{ secrets.GOOGLE_DRIVE_FOLDER_ID }}
```

ここはかなり大事です。

GitHub Actions では、リポジトリに登録した Secrets を `env:` 経由で実行プロセスに渡せます。

Python 側では `os.environ["..."]` で受け取ります。

つまり、`yml` と Python の役割分担はこうです。

- `yml`: Secrets を安全に渡す
- Python: 環境変数として受け取って使う

この構造にしておけば、ソースコードを公開しても認証情報はコード上に出ません。

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
- `env:` で Secrets を渡し、処理本体は Python に寄せる
{% endcapture %}
{% include callout.html type="tip" title="今回のポイント" icon="💡" content=yml_points %}

GitHub Actions の `workflow yml` は、見た目よりずっと役割が明確です。

`yml` では実行条件と環境づくりに専念して、実際の処理は Python に寄せておくと、壊れにくく読みやすい構成になります。
