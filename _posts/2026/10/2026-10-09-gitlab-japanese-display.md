---
layout: post
title: "GitLabを日本語表示に変更する方法"
description: "GitLabを日本語表示にする手順を実画面付きで説明します。Preferencesの言語設定、保存・再読み込み、英語が残る場合とSelf-Managedの確認点をまとめました。"
date: 2026-10-09 20:55:00 +0900
category: 開発
tags:
  - dev-memo
  - beginner
  - workflow
thumbnail: /assets/images/blog/2026-10-09-gitlab-japanese-display/thumbnail.png
thumbnail_alt: GitLabの表示言語を日本語に切り替える設定を紹介するイラスト
excerpt: "GitLabの日本語化はPreferencesから設定できます。実画面を見ながら、言語の選択・保存と、英語が残る場合の確認点を整理します。"
---

GitLabの画面を日本語にするには、自分のアカウントの「Preferences」で表示言語を変更します。英語の設定画面でも、項目名が分かれば順番に操作できます。

この記事ではGitLab.comの画面例を使い、日本語への切り替え方と、変更しても英語が残る場合の確認ポイントを紹介します。

## まずは日本語化の手順

1. GitLabにログインし、自分のアバターをクリック
2. 「Preferences」を開く
3. 「Localization」の「Language」で「Japanese - 日本語」を選択
4. 「Save changes」をクリック
5. 表示が変わらなければ、ページを再読み込み

公式ドキュメントでも、この順序で表示言語を変更する方法が案内されています。設定後に再読み込みが必要になる場合もあります。[GitLab公式の表示言語変更手順](https://docs.gitlab.com/user/profile/preferences/#change-your-display-language-on-the-gitlab-ui)

以下のスクリーンショットは2026年6月9日のGitLab.comの画面例です。個人情報や周辺画面を除いて切り抜いています。公式手順は2026年10月9日に確認しました。画面の配置や翻訳率は、利用時期やバージョンによって異なることがあります。

## 画像で確認する設定方法

### 1 アバターからPreferencesを開く

ログイン後、自分のアバターをクリックしてアカウントメニューを開き、「Preferences」を選びます。プロジェクトの設定ではなく、自分のアカウントにある項目を探してください。

現在の公式手順ではアバターは右上と案内されています。配置が画像と異なる場合も、アカウントメニュー内の「Preferences」が目印です。

GitLab.comを使っている場合は、ログイン後に[Preferencesを直接開く](https://gitlab.com/-/profile/preferences)こともできます。会社独自のURLで使っているGitLabでは、そのサイトのアカウントメニューから進んでください。

![アカウントメニューのPreferences項目](/assets/images/blog/2026-10-09-gitlab-japanese-display/preferences-menu.png)

図1　アカウントメニューからPreferencesを開く

### 2 Localizationで日本語を選ぶ

Preferencesのページを下へスクロールし、「Localization」を探します。その中の「Language」の選択欄を開き、「Japanese - 日本語」を選びます。

見つけにくい場合は、ブラウザーのページ内検索で「Localization」を検索すると、該当箇所を探しやすくなります。

![Languageの選択欄を開いてJapanese - 日本語の候補を表示した画面　選択と保存を行う前](/assets/images/blog/2026-10-09-gitlab-japanese-display/language-japanese.png)

図2　Languageの選択肢にJapanese - 日本語がある画面　選択と保存を行う前

### 3 Save changesで保存する

言語を選んだら、「Save changes」をクリックします。選択しただけで画面を閉じず、保存まで済ませましょう。

保存後は、メニューや設定項目の表示を確認します。英語のままならページを再読み込みし、Languageの選択が日本語になっているかを見直してください。

## 日本語にならないときの確認ポイント

### 画面全体が英語のまま

まず「Save changes」で保存したかを確認し、ページを再読み込みします。続いてPreferencesを開き直し、Languageが日本語のままになっているか確認してください。複数のアカウントや会社用のGitLabを使っている場合は、設定したアカウントと、いま開いているサイトが同じかも確認しましょう。

### 一部の項目だけ英語が残る

GitLabの翻訳には未対応の文字列や、翻訳が不完全な箇所があります。一部の項目が英語でも、それだけで設定の失敗とは判断できません。[GitLab公式の翻訳に関する説明](https://docs.gitlab.com/development/i18n/)

画像に表示される翻訳率は撮影時点のものです。「Japanese」を選べば、すべての画面が完全に日本語になるという意味ではありません。

### 会社のGitLabで画面が違う

自社運用のGitLab Self-Managedでは、導入されているバージョンによって画面が異なることがあります。自分の表示言語を変えたいときは、まずアカウントのPreferencesを確認してください。

組織全体の既定の言語を変える場合は、管理者向けの別設定です。公式には「Admin」→「Settings」→「Preferences」→「Localization」で変更する手順があり、GitLab Self-ManagedとGitLab Dedicatedが対象です。一般ユーザーが自分の表示言語を変える操作と混同しないようにしましょう。[GitLab公式の管理者向け言語設定](https://docs.gitlab.com/administration/settings/localization/#change-the-default-language)

## まとめ

GitLabの日本語化は、アバターから「Preferences」を開き、「Localization」の「Language」で日本語を選んで保存すれば設定できます。表示が変わらない場合は再読み込みと保存内容を確認し、一部だけ英語が残る場合は翻訳状況も考慮してください。
