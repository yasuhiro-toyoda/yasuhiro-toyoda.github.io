---
layout: post
title: "GitHubを1人で使うときのmain保護設定｜PR承認0人・必須チェックの実例"
description: "GitHubのRulesetsでmainを保護する設定例。PR必須・承認0人・必須ステータスチェック・回避者なしの設定と、PRでの確認手順を紹介します。"
date: 2026-09-29 00:16:00 +0900
category: 開発
tags:
  - workflow
  - dev-memo
thumbnail: /assets/images/blog/2026-09-29-github-main-protection/thumbnail.jpg
thumbnail_alt: "1人でもmainを守る。Gitのブランチと盾を描いたmainブランチ保護設定のイメージ"
excerpt: "1人で運営するブログでもmainを保護。PR承認0人と必須チェックを使い、devからmainへ反映するための設定手順を紹介します。"
---

開発では、完成前の変更や動作しないコードが公開用のブランチに入ると、ほかの作業や利用者に影響します。`main`ブランチを保護し、変更内容と検査結果を確認してから反映することは、安定して運用するための基本的な仕組みです。

私の場合、GitHubでブログを1人で運営しています。共同開発者はいませんが、記事の編集中に公開してしまったり、ビルドできない変更を`main`へ入れたりする可能性はあります。1人でも確認の手順が必要だと考え、作業用の`dev`からPRを作り、検査に成功してから`main`へ反映するようにしました。

この記事では、実際に設定したGitHubのルールセットと、設定後の確認手順を紹介します。GitHub Actionsのワークフローや記事検査スクリプトの作り方は、別の記事にまとめます。

## 今回設定するルール

私のブログでは、作業ブランチから`dev`へ変更を集め、公開時に`dev`から`main`へPRを作成します。`main`の保護設定は次のとおりです。

| 項目 | 設定値 |
| --- | --- |
| 対象 | `main` |
| PRを経由した変更 | 必須 |
| 必要な承認数 | 0人 |
| 必須ステータスチェック | 2件 |
| 回避できる人・アプリ | 登録しない |
| 強制プッシュ・ブランチ削除 | 禁止 |

承認0人なら、単独運営でも自分でPRを確認してマージできます。ただし、PRの承認者による第三者チェックは入りません。変更内容を読むことと、公開するかどうかを決めることは自分の作業として残ります。

## 1. `dev`と検査を用意する

ルールを設定する前に、`main`とは別に`dev`ブランチを作ります。次に、`main`宛てのPRで動くGitHub Actionsのワークフローを用意し、PR上でチェックが実際に表示・成功するところまで確認します。

私のブログで使用しているチェックは次の2件です。

| チェック名 | 確認すること |
| --- | --- |
| `Publication source` | `main`宛てのPRが、同じリポジトリの`dev`から作られているか |
| `Jekyll build and content` | 記事の形式や画像ファイルを検査し、Jekyllでビルドできるか |

前者は公開元を限定するための検査、後者は記事とサイトの検査です。実際のワークフローは[このリポジトリの`publish-checks.yml`](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/blob/main/.github/workflows/publish-checks.yml)で確認できます。

**注意：ルールセットの設定だけで検査が作られるわけではありません。** 必須チェックに指定する名前は、PRで実行されたチェックの表示名を確認して入力します。別のリポジトリで試す場合は、自分のワークフローに表示された名前を使ってください。

## 2. `main`用のルールセットを作る

GitHubで対象リポジトリを開き、**Settings → Rules → Rulesets → New ruleset → New branch ruleset**へ進みます。画面の名称が変わっている場合は、GitHub公式の[ルールセット作成手順](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)も確認してください。

私が指定した主な値は次のとおりです。

| 設定欄 | 指定する値 |
| --- | --- |
| Ruleset name | `Protect main publication` |
| Enforcement status | `Active` |
| Bypass list | 空欄 |
| Target branches | `main`を対象にする |
| Require a pull request before merging | 有効、Required approvalsは`0` |
| Require status checks to pass | 有効、上記2件を指定 |
| Expected source | `GitHub Actions` |
| Require branches to be up to date before merging | 有効 |
| Restrict deletions / Block force pushes | 有効 |

マージ方法には`Merge`を許可しました。私の運用では`dev`を公開後も残すため、リポジトリ全体の設定でもマージコミットを許可し、PRのマージ後に作業元ブランチを自動削除しない設定にしています。

`Bypass list`を空欄にしても、リポジトリの設定を変更できる権限まで消えるわけではありません。ここで防ぐのは、通常の変更操作でルールを回避して`main`に反映することです。

## 3. PRで動作を確かめる

設定を保存したら、`dev`から`main`へのPRを開き、次を確認します。

1. PRのチェック欄に`Publication source`と`Jekyll build and content`が表示される。
2. 両方が成功するまでマージできない。
3. 両方が成功し、必要な条件を満たすとマージできる。

`main`宛てのPRを`dev`以外から作ったときは、私の`Publication source`が失敗する設計です。**GitHubのルールセットだけで「PRの元は必ず`dev`」と判定しているわけではありません。** この点はワークフロー側の検査に任せています。

## 1人運用での公開手順

記事を更新するときは、作業ブランチから`dev`へPRで変更を集めます。公開時には`dev`から`main`へのPRを作成し、差分と必須チェックを確認してからマージします。

私の環境ではCodexにも作業を依頼しますが、**PRのチェックが通っただけでは公開指示にはしません。** 対象の差分を確認したうえで「devブランチをmainにマージして、公開して」と明示してから反映します。同じGitHubアカウントで作業する場合、GitHubの承認人数だけでは人とAIの公開判断を区別できないためです。

これで、単独運営でも「作業する」「検査する」「公開を決める」を順に確認できるようになりました。次の記事では、今回必須にした2つのチェックをGitHub Actionsで作る手順を紹介します。

---

参考： [GitHub Docs：ルールセットの作成](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository) ／ [本ブログの保護設定手順](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/blob/main/docs/github-protection.md)
