---
layout: post
title: Gitのuser.name・user.emailは何の設定？GitHub・GitLabのアカウントとの違い
description: Gitのuser.name・user.emailと、GitHub・GitLabのアカウントや認証情報の違いを図解。メールの関連付け、公開用アドレス、仕事用と個人用の設定を整理します。
date: 2026-11-13 10:33:15+09:00
category: 開発
tags:
- git
- beginner
thumbnail: /assets/images/blog/2026-11-13-git-identity-accounts/thumbnail.png
thumbnail_alt: Gitの名前とメール設定。ノートPCに向かう人物と、アカウントと鍵のアイコン
excerpt: Gitの名前・メールと、GitHub・GitLabへのログインはどう関係するのか。commitとpushの図から、作者情報、認証、メールの関連付けを整理します。
---

Gitの初期設定で入力する、この2つのコマンド。

```shell
git config --global user.name "Hanako Example"
git config --global user.email "hanako@example.com"
```

使い始めたころは、「お作法だから」と淡々と打ち込んでいた方もいると思います。少なくとも、昔の私はそうでした。

少し慣れてきたところで「あれ？」となったのが、この名前とメールアドレスです。名前はGitHubのユーザー名に合わせるのか。メールアドレスはログインに使うものなのか。GitLabを使うときも設定を変えるのか。

`user.name`と`user.email`は、**コミットに記録する名前とメールアドレス**です。一方、GitHub・GitLabのアカウントやSSHキーなどの認証情報は、接続先で操作するために使います。

名前とメールアドレスを設定すること、サービスにログインすること、リポジトリにpushすること。それぞれの役割を、図と具体例で整理します。

## Gitの作者情報とアカウント認証の違い

まずは、どこで何を使うのかを並べます。

| 項目 | 役割 | 使う場面 |
| --- | --- | --- |
| Gitの`user.name` | コミットに記録する名前 | PC上でコミットを作るとき |
| Gitの`user.email` | コミットに記録するメールアドレス | PC上でコミットを作るとき、サービス上で作者とアカウントを関連付けるとき |
| GitHub・GitLabのアカウント | サービス上の利用者を識別する | ブラウザで利用するとき、アクセス権を管理するとき |
| SSHキーやHTTPS用の認証情報 | 接続している利用者を確認する | 認証が必要なGit操作でサーバーに接続するとき |

`user.name`は、GitHubやGitLabのユーザー名と違う文字列にできます。たとえば、Gitの名前を`Hanako Example`、GitHubのユーザー名を`hanako-dev`にする使い方です。

Gitが名前を記録するときに、GitHubへ「この名前の人はいますか」と問い合わせる処理はありません。GitHubやGitLabのアカウントを作る前でも、手元のリポジトリでコミットを作れます。この関係は、GitHub・GitLabのどちらを使っても共通です。[GitHubのユーザー名設定の説明](https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git)

## commitとpushの動作をおさらい

PC上でファイルを編集してコミットすると、その履歴には名前やメールアドレスが入ります。そのコミットをサーバーに送る操作がpushです。

![PC上でuser.nameとuser.emailをコミットに記録し、push時には別の認証情報でGitHubまたはGitLabへ接続する関係図。]({{ '/assets/images/blog/2026-11-13-git-identity-accounts/identity-and-authentication.png' | relative_url }})

図の名前とメールアドレスは、履歴の中に残る情報です。下側の認証情報は、サーバーへの接続に使います。

SSH接続では、サーバーに登録した公開鍵に対応する秘密鍵を使います。HTTPS接続では、トークンや認証情報を管理するツールなどを使います。接続先では、認証に加えて対象リポジトリへの操作権限も確認されます。[GitHubの認証の説明](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github)・[GitLabのSSH認証](https://docs.gitlab.com/user/ssh/)・[GitLabのアクセストークン](https://docs.gitlab.com/user/profile/personal_access_tokens/)

そのため、`user.name`を別のアカウント名に変更しても、そのアカウントの権限が手に入るわけではありません。pushの認証エラーが出たときは、接続先URLや認証情報、リポジトリの権限を確認します。

なお、コミットには作者を表す`author`と、コミットを作成した人を表す`committer`の情報があります。自分の変更を新しいコミットとして記録する例では、この2つに同じ名前・メールアドレスを使います。[Gitの設定の説明](https://git-scm.com/docs/git-config)

## メールアドレスでコミットとアカウントを結び付ける

ここでメールアドレスが登場します。GitHubやGitLabは、コミットに記録されたメールアドレスを使って、作者とサービス上のアカウントを関連付けます。

| 確認すること | GitHub | GitLab |
| --- | --- | --- |
| PCで使う名前の設定 | Gitの`user.name` | Gitの`user.name` |
| PCで使うメールの設定 | Gitの`user.email` | Gitの`user.email` |
| アカウントと結び付けるメール | 自分のアカウントに追加したメールアドレス、またはGitHub提供のnoreplyアドレス | 自分のアカウントで確認済みのメールアドレス、またはGitLab提供のprivate commit email |
| サービス上の設定変更後 | PC側のGit設定も確認する | PC側のGit設定も確認する |

たとえば、GitHubに登録したメールアドレスが`hanako@example.com`で、コミットにも同じアドレスが記録されていれば、そのコミットをアカウントに関連付けられます。

反対に、PCに古いメールアドレスが残っていると、コミットが期待したアカウント表示につながらない原因になります。pushには成功したのに、作者の表示が思っていたものと違う。この場合は、認証情報に加えてコミット内のメールアドレスを確認してください。

GitLabのプロフィールにある`Commit email`は、GitLabの画面上で行うGit操作に使う設定です。PCのターミナルから作るコミットには、そのPCのGit設定が使われます。[GitHubのコミット用メールの説明](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)・[GitLabのプロフィール設定](https://docs.gitlab.com/user/profile/)

## 実際のメールアドレスを公開したくないときは？

公開リポジトリへ送るコミットには、名前とメールアドレスも含まれます。プロフィール画面でメールを非表示にしていても、コミットに実際のアドレスを入れていれば、その履歴から確認できます。

個人のメールアドレスを出したくない場合は、各サービスが提供するコミット用アドレスを使えます。

- **GitHub**では、アカウントのメール設定に表示されるnoreplyアドレスを使います。
- **GitLab**では、プロフィールで`Use a private email`を選び、表示されたprivate commit emailを使います。

アドレスは自分の設定画面からコピーします。PC上の対象リポジトリを開き、次の`YOUR_PRIVATE_COMMIT_EMAIL`をコピーしたアドレスに置き換えて設定してください。

```shell
git config --local user.email "YOUR_PRIVATE_COMMIT_EMAIL"
```

GitHubとGitLabで別々のコミット用アドレスを使うときは、各リポジトリのメール設定で指定します。[GitHubのコミット用メールの説明](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)・[GitLabのprivate commit emailの説明](https://docs.gitlab.com/user/profile/#use-an-automatically-generated-private-commit-email)

## 個人用と仕事用で名前やメールを使い分ける

最初に出てきた`--global`は、そのPCで自分のOSユーザーが使うGitの共通設定です。対象リポジトリに個別の設定があると、そちらが優先されます。

| 指定 | 設定の対象 | 使う場面 |
| --- | --- | --- |
| `--global` | 自分のOSユーザーで使うGitの共通設定 | 複数のリポジトリで同じ名前・メールを使う |
| `--local` | 現在のリポジトリ | 仕事用、個人用、サービスごとに設定を変える |

仕事用のリポジトリに別のメールアドレスを設定するなら、そのフォルダー内で実行します。

```shell
git config --local user.name "Hanako Example"
git config --local user.email "hanako@example.org"
```

現在のリポジトリで使われる設定は、次のコマンドで確認できます。

```shell
git config --get user.name
git config --get user.email
```

どのファイルから設定が読み込まれたかも確認したいときは、`--show-origin`を付けます。

```shell
git config --show-origin --get user.email
```

アカウントを切り替えたつもりでも、Gitのメール設定はそのまま、ということがあります。新しいリポジトリで作業を始めるときに、この2項目を確認しておくと混乱を減らせます。[Gitの設定の説明](https://git-scm.com/docs/git-config)

## 【重要】設定を変えても過去のコミットは変わらない

`user.name`や`user.email`を変更すると、その後に作るコミットに反映されます。すでに作ったコミットの名前・メールアドレスは、そのまま残ります。

検証用のリポジトリでも、次の動作を確認しました。

| 操作 | 1件目のコミットのメール | 次に作ったコミットのメール |
| --- | --- | --- |
| `hanako@example.com`でコミット | `hanako@example.com` | — |
| 設定を`hanako@example.org`に変更 | `hanako@example.com` | — |
| 変更後にもう一度コミット | `hanako@example.com` | `hanako@example.org` |

直近のコミットに記録された情報は、次のコマンドで確認できます。

```shell
git log -1 --format=fuller
```

これから使う設定と、すでに履歴に入った情報は、確認する場所が違います。公開済みの履歴を直す場合は、共同作業への影響も含めて別の作業として扱います。[GitHubの名前変更の説明](https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git)

## 困ったときに確認する場所

| 症状 | 最初に確認する場所 |
| --- | --- |
| コミットに記録された名前が違う | そのリポジトリの`user.name`と、コミット内の作者情報 |
| サービス上で期待した作者の表示にならない | コミット内のメールと、アカウントに登録したメール |
| 設定を変えたのに古いコミットの表示が同じ | そのコミットを作った時点の名前・メール |
| pushで認証エラーになる | 接続先URL、SSHキーやHTTPS用認証情報 |
| 認証できてもpushを拒否される | リポジトリの権限、ブランチ保護、サーバー側のルール |

サーバー側でコミットのメールアドレスなどを検査するルールが設定されている場合は、その条件も確認します。作者情報を記録する処理と、接続先が受け入れる条件を順に追うと、どの設定を直すかを絞れます。

GitHubからGitLabへ移っても、`user.name`と`user.email`の役割は共通です。最初に確認するのは、コミットに残す名前・メールと、接続先で使う認証情報です。

## 参考資料

- [Git公式　git config](https://git-scm.com/docs/git-config)
- [GitHub公式　Setting your username in Git](https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git)
- [GitHub公式　Setting your commit email address](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)
- [GitLab公式　User account](https://docs.gitlab.com/user/profile/)

