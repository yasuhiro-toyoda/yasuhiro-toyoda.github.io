---
layout: post
title: "GitHub Actionsでブログ公開前のチェックを作る"
description: "1人で運営するJekyllブログに、公開元ブランチ・記事情報・サムネイル・ビルドの検査を追加。実際のGitHub Actions設定と、PRで失敗したときの確認方法を紹介します。"
category: 開発
tags:
  - workflow
  - dev-memo
excerpt: "devからmainへ公開する前に、記事の日付や画像の指定ミスをPRで確認。実際に使っている2つの必須チェックと、失敗時の直し方をまとめます。"
published: false
---

{% comment %}
公開前の準備：本文確認後、実際の公開日時に合わせてdateとファイル名を設定する。
アイキャッチを配置し、thumbnailとthumbnail_altを追加する。
published: falseは公開が決まった時点で解除する。
コードは2026年10月1日時点のmainを参照。公開前に実際の設定との差分を再確認する。
{% endcomment %}

このブログは、GitHubとJekyllを使って1人で運営しています。記事や画像の変更は作業用の`dev`に集め、公開するときに`main`へ反映する流れです。

記事を読んで内容に問題がなくても、日付の書き方が違っていたり、指定した画像がリポジトリに入っていなかったりすると、思ったとおりに公開できません。本文を直すたびに、ファイルの形式まで全部目で確認するのも手間です。

そこで、PRを作ったときにGitHub Actionsで検査するようにしています。確認するのは、公開元のブランチと、記事・画像・サイトのビルドです。

[前回の記事](https://musashistudio.com/blog/2026/09/28/github-main-protection/)では、検査に通るまで`main`へマージできないようにする保護設定を紹介しました。今回は、その設定で必須にした2つのチェックの中身を見ていきます。

## 公開前に確認する2つのこと

PRに表示されるチェック名は、次の2つです。

| チェック名 | 確認すること |
| --- | --- |
| `Publication source` | `main`宛てのPRが、同じリポジトリの`dev`から作られているか |
| `Jekyll build and content` | 記事情報とサムネイルの指定を検査し、Jekyllでサイトをビルドできるか |

作業ブランチから`dev`へ集めるときも、`dev`から`main`へ公開するときも、同じワークフローを動かします。記事の不備は、公開用のPRを作る前にも見つけられます。

この記事の設定は、私のブログのディレクトリ構成やカテゴリ・タグに合わせたものです。別のJekyllサイトで使う場合は、記事の配置や必須項目を自分のサイトに合わせて変更してください。

`on`や`steps`など、ymlの基本的な読み方は[「GitHub Actions の yml は何を書いているのか」](https://musashistudio.com/blog/2026/04/16/GitHub-Actions-%E3%81%AE-yml-%E3%81%AF%E4%BD%95%E3%82%92%E6%9B%B8%E3%81%84%E3%81%A6%E3%81%84%E3%82%8B%E3%81%AE%E3%81%8B/)にまとめています。

## ワークフローを用意する

設定ファイルは`.github/workflows/publish-checks.yml`です。実際に使っている内容を載せます。

{% raw %}
```yaml
name: Publish checks

on:
  pull_request:
    branches: [main, dev]
    types: [opened, synchronize, reopened, ready_for_review, edited]

permissions:
  contents: read

concurrency:
  group: publish-checks-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  source:
    name: Publication source
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Require same-repository dev for main
        env:
          BASE_BRANCH: ${{ github.base_ref }}
          HEAD_BRANCH: ${{ github.head_ref }}
          HEAD_REPOSITORY: ${{ github.event.pull_request.head.repo.full_name }}
          BASE_REPOSITORY: ${{ github.repository }}
        run: |
          if [ "$BASE_BRANCH" = "main" ]; then
            if [ "$HEAD_BRANCH" != "dev" ] || [ "$HEAD_REPOSITORY" != "$BASE_REPOSITORY" ]; then
              echo "::error::main accepts pull requests only from dev in the same repository."
              exit 1
            fi
          fi
          echo "Publication source accepted."

  build:
    name: Jekyll build and content
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
        with:
          fetch-depth: 0
          persist-credentials: false
      - name: Install content-check dependency
        run: python3 -m pip install -r requirements-ci.txt
      - name: Test content checker
        run: python3 -m unittest discover -s tests -v
      - name: Check content in the PR merge result
        env:
          BASE_SHA: ${{ github.event.pull_request.base.sha }}
        run: python3 scripts/check_content.py --base "$BASE_SHA"
      - uses: ruby/setup-ruby@14594264cd68ce8a2345dd349bc3d138a4ef85c8 # v1
        with:
          ruby-version: '3.3'
          bundler: '2.6.9'
      - name: Install Jekyll dependencies
        run: |
          bundle lock --add-platform x86_64-linux
          bundle install
      - name: Build site
        env:
          JEKYLL_ENV: production
          TZ: Asia/Tokyo
        run: bundle exec jekyll build --trace
```
{% endraw %}

[リポジトリのワークフロー](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/blob/main/.github/workflows/publish-checks.yml)でも確認できます。

このymlに加えて、次のファイルを使っています。ymlだけをコピーしても、検査スクリプトや設定ファイルがなければ実行できません。

- [`scripts/check_content.py`](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/blob/main/scripts/check_content.py)：記事情報とサムネイルを検査するPythonスクリプト
- [`tests/test_content.py`](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/blob/main/tests/test_content.py)：検査スクリプト自体のテスト
- [`requirements-ci.txt`](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/blob/main/requirements-ci.txt)：YAMLを読むためのPyYAMLを指定
- [`_data/blog_categories.yml`](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/blob/main/_data/blog_categories.yml)と[`_data/blog_tags.yml`](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/blob/main/_data/blog_tags.yml)：使用できるカテゴリとタグ
- `Gemfile`と`Gemfile.lock`：Jekyllなど、サイトのビルドに必要な依存関係

`pull_request.branches`に書いている`main`と`dev`は、PRの反映先です。PR作成時や追加コミット時、再オープン時などに動くようにしています。

`paths`による実行対象の絞り込みは入れていません。記事以外にも、画像、レイアウト、設定ファイルの変更が公開に影響するためです。同じPRに追加の変更が来た場合は、`concurrency`の設定で古い実行をキャンセルします。

`permissions`は`contents: read`とし、この検査ではリポジトリに書き込みません。Actionの参照には、現行のワークフローと同じコミットSHAを載せています。

## Publication sourceで公開元を確認する

1つ目のジョブは短く、PRの反映先と作成元を比較しています。

- `main`宛てなら、作成元が`dev`で、同じリポジトリからのPRかを確認する
- `dev`宛てなら、この公開元の制限はかけない

`dev`という名前のブランチであっても、別のリポジトリにあるものは通しません。ブランチ名に加えて、リポジトリ名も比較するのはそのためです。

条件に合わない場合は、次のメッセージを出して`exit 1`で終了します。

```text
main accepts pull requests only from dev in the same repository.
```

これにより、作業ブランチから直接`main`へPRを作ってしまった場合に気づけます。通常の流れは、作業ブランチ→`dev`→`main`です。

なお、このチェックはPR内のワークフローで実行します。書き込み権限を持つ人が検査コード自体を変えることまで防ぐものではありません。`.github/workflows/`や検査スクリプトの変更も、PRの差分で確認します。

## Jekyll build and contentで記事とサイトを確認する

2つ目のジョブでは、検査スクリプトのテスト、記事の検査、Jekyllのビルドを順番に実行します。途中で失敗すれば、そのジョブは失敗になり、後ろの通常ステップへは進みません。

### 変更した記事の必須項目を調べる

記事の検査では、front matterに次の項目が入っているかを確認します。

```python
REQUIRED = ("title", "description", "date", "category", "tags", "excerpt")
```

空欄だけでなく、日付やカテゴリ・タグの書き方も確認します。

| 項目 | このブログでの検査内容 |
| --- | --- |
| 記事のパス | `_posts/YYYY/MM/YYYY-MM-DD-slug.md`という配置か |
| 日付 | `+09:00`相当の時差を含み、ファイル名・ディレクトリと年月日が一致するか |
| 公開日時 | 実行時点より未来の日付になっていないか |
| カテゴリ | `blog_categories.yml`にあるラベルか |
| タグ | 空でないリストで、すべて`blog_tags.yml`にあるslugか |
| サムネイルの説明 | `thumbnail`を設定した記事に`thumbnail_alt`があるか |

例えば、`_posts/2026/09/2026-09-30-example.md`という記事なら、日付は次のように書きます。

```yaml
date: 2026-09-30 12:00:00 +0900
category: 開発
tags:
  - workflow
  - dev-memo
```

これは書式の例です。実際の記事では、ファイル名と`date`を公開する日時に合わせます。予約投稿は今回の検査では認めず、まだ未来の日時ならエラーにします。

こうした必須項目や日付の検査は、PRで追加・変更された記事を対象にしています。過去記事の形式を、導入時に全部そろえ直す必要がない構成です。過去記事も編集したときには検査対象になります。

### サムネイルは全記事分を確認する

サムネイルの参照は、変更した記事に限らず全記事を調べます。古い画像を削除した場合に、その画像を使っている過去記事を見落とさないためです。

設定されている`thumbnail`について、`/assets/`から始まるローカルのパスか、指定先が実ファイルとして存在するかを確認します。全記事のfront matterも読み込むため、YAMLが壊れていればそこで失敗します。

ここで調べているのは、front matterの`thumbnail`です。**本文中の画像、リンク先の到達性、画像の見た目は、このスクリプトでは確認していません。** また、`thumbnail`自体を必須にする検査でもありません。

### PRを反映した状態でビルドする

`pull_request`イベントで通常の`actions/checkout`を使うと、マージ可能なPRでは、反映先と変更内容を組み合わせたマージ結果が取得されます。作業ブランチ単独では通っても、反映先と合わせると壊れる場合を確認するためです。[GitHub公式の説明](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#how-the-merge-branch-affects-your-workflow)も参照してください。

記事検査にはPRの反映先のコミットSHAを渡し、そのコミットと検査中の`HEAD`を比較しています。`fetch-depth: 0`は、比較に必要な履歴を取得するための設定です。

最後にRuby 3.3、Bundler 2.6.9で依存関係を用意し、次のコマンドを実行します。

```shell
bundle exec jekyll build --trace
```

ここでは`JEKYLL_ENV=production`、`TZ=Asia/Tokyo`を指定しています。`Gemfile.lock`にはLinux向けのプラットフォーム情報を追加してからインストールしますが、これはActionsの実行環境内での変更です。このワークフローからリポジトリへコミットする処理はありません。

ビルドに成功すれば、少なくともその環境でサイトを生成できたことがわかります。実際の公開は、この後に動くGitHub Pages側の処理でも確認が必要です。

## PRで成功と失敗を確かめる

導入時は、ワークフローと必要なファイルを作業ブランチに追加し、`dev`宛てのPRでチェックが動くことを確認します。その変更を`dev`へ反映してから、`dev`→`main`のPRでも2つのチェック名を確認します。

ワークフローを置いただけでは、失敗したPRのマージを禁止する設定にはなりません。`main`のルールセットで、実際に表示された`Publication source`と`Jekyll build and content`を必須チェックに指定します。設定手順は[前回の記事](https://musashistudio.com/blog/2026/09/28/github-main-protection/)を参照してください。

動作確認では、正常な記事が通ることに加えて、止めたい変更が失敗することも確認します。検証用の作業ブランチで試し、確認のために壊した変更は`dev`や`main`へマージしません。

| 試すこと | 期待する結果 |
| --- | --- |
| 同じリポジトリの`dev`→`main` | `Publication source`が成功する |
| `dev`以外のブランチ→`main` | `Publication source`が失敗する |
| 変更記事の`description`を空欄にする | `Jekyll build and content`が記事検査で失敗する |
| `thumbnail`に存在しない画像を指定する | `Jekyll build and content`が記事検査で失敗する |
| 原因を修正し、同じPRへ追加コミットする | 新しい実行で検査がやり直される |

スクリプト側の[`tests/test_content.py`](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/blob/main/tests/test_content.py)にも、必須項目の欠落、日付の不一致、存在しないサムネイルなどのテストを用意しています。

### 失敗したらジョブ内のどこで止まったかを見る

PRのチェック欄から失敗したジョブを開き、赤くなったステップのログを確認します。`Jekyll build and content`が失敗していても、Jekyllの実行前に止まっている場合があります。

記事検査では、対象の記事パスと理由が並びます。表示される文言と、見直す場所の例は次のとおりです。

| エラーの文言 | 見直すところ |
| --- | --- |
| `description is required` | front matterの説明文が空になっていないか |
| `filename, directory and date must match` | ファイル名・配置先・`date`の年月日が一致しているか |
| `future date would hide this post from publication` | 公開日時がまだ先になっていないか |
| `tags must contain registered slugs only` | 表示名ではなく、登録済みのslugを書いているか |
| `thumbnail file does not exist` | 画像を追加し忘れていないか。パスや大文字・小文字が一致しているか |

`Publication source`で失敗した場合は、記事を直す前にPRの向きを確認します。作業ブランチから`main`へ直接送っていたら、まず`dev`宛てのPRとして確認し、その後に`dev`から`main`へのPRを用意します。

`Test content checker`で止まった場合は、検査スクリプトやテストの変更を確認します。`Install Jekyll dependencies`なら依存関係の解決・取得、`Build site`ならJekyllのエラー本文を確認します。ネットワークの一時的な失敗と、毎回同じ場所で出る記事や設定のエラーも分けて見ます。

修正は作業ブランチへコミットし、同じPRに反映します。`dev`→`main`の段階で見つかった不備も、作業ブランチ→`dev`のPRで修正してから公開用PRの再検査を確認します。保護設定や検査を外して通すことはしません。

チェック自体が出ない場合は、PRの反映先、ワークフローの構文、マージ競合の有無を確認します。`pull_request`のワークフローは、マージ競合があると実行されないため、競合を解消したうえで結果を確認します。

## 最後に自分で確認すること

自動検査で確認できるのは、決めた条件だけです。チェックが2つとも成功しても、公開前には次の確認が残ります。

- 本文に誤りがないか。試していないことを体験談として書いていないか
- アイキャッチや本文中の画像が、意図したものになっているか
- 外部リンク・内部リンクが正しいか
- スマートフォン幅でも、表やコード、見出しが読めるか
- `dev`→`main`の差分に、今回公開しない変更が混ざっていないか

ワークフローや検査スクリプトを変更したPRでは、その変更で必要な検査が抜けていないかも確認します。

私の運用ではCodexに作業を依頼することもありますが、**検査の成功だけで公開を決めることはしません。** 差分と内容を確認し、公開すると決めてから`main`へ反映します。マージ後にはGitHub Pagesの処理と、公開ページの本文・画像・リンクも確認します。

1人で運営するブログでも、日付、カテゴリ、画像パス、ビルドの確認は毎回必要です。機械で判断できるものをPRで先に調べておけば、本文や画像を確認するときに見るものを減らせます。

まずは、自分のブログで間違えたくない項目を決め、その条件をチェックにしていくところから始めるとよいと思います。
