---
layout: post
title: "Google Drive APIのOAuth設定｜GitHub Actionsで使う認証情報を準備する"
description: "Google Drive APIを使うためのOAuth同意画面、デスクトップ用クライアント、リフレッシュトークンの取得をスクリーンショット付きで解説。GitHub Secretsに登録する情報を整理します。"
date: 2026-10-04 14:33:00 +0900
updated_at:
category: 開発
tags:
  - workflow
  - beginner
  - dev-memo
thumbnail: /assets/images/blog/2026-10-04-google-drive-api-oauth/thumbnail.png
thumbnail_alt: "Google Drive APIのOAuth設定。パソコンの前で鍵を持つ人物とクラウド内のフォルダ"
excerpt: "Secretsに登録する値はどこで取得するのか。Google側の設定から、手元のPythonで認可し、リフレッシュトークンを準備するまでをまとめます。"
---

GitHub ActionsからGoogle Driveを使いたいとき、Secretsの登録欄を開いただけでは設定は終わりません。登録するクライアントIDやリフレッシュトークンを、先にGoogle側で用意する必要があります。

この記事では、自分のGoogle Driveを使う個人用スクリプトを例に、Google Cloudの設定から手元のPCでの認可までを整理します。取得した情報は、既存の[GitHub Actionsのyml解説]({% post_url 2026/04/2026-04-16-GitHub Actions の yml は何を書いているのか %})で紹介したSecretsへ登録します。

画面は2026年4月の記録を使い、説明は2026年10月4日時点の公式資料と照合しました。個人情報、アプリやプロジェクトの識別情報、認証情報の値が写る部分は掲載画像から除去しています。

## 今回準備するものと、OAuthの役割

OAuthは、アプリにどの範囲のアクセスを許可するかを決める仕組みです。Googleへのログインで本人確認をしたうえで、Driveへのアクセスをアプリに許可します。この「許可する」部分を**認可**と呼びます。

| 情報 | 役割 | 準備する場所 |
| --- | --- | --- |
| クライアントID | 利用するアプリを識別する | Google CloudのOAuthクライアント設定 |
| クライアントシークレット | このクライアントの認可処理で使う値 | 同じクライアントの設定・ダウンロードしたJSON |
| アクセストークン | Drive APIを呼び出すときに使う、短期間の利用証明 | 認可後に取得する |
| リフレッシュトークン | 新しいアクセストークンを取得するために使う | オフラインアクセスを伴う認可で取得する |
| フォルダID | Drive内の保存先を指定する | 保存先フォルダを準備するときに確認する |

クライアントIDやフォルダIDは、それだけでDriveを操作できる秘密鍵ではありません。ただし、記事では自分の環境を特定する実際の値を載せる必要はないので省いています。

この記事の到達点は、GitHub Secretsへ登録する認証情報の準備です。CSVのアップロードや保存先フォルダの作成は、別の処理になります。

## 1. Google CloudのプロジェクトでDrive APIを有効にする

Google Driveを利用できるGoogleアカウントと、Google Cloudのプロジェクトを用意します。以後は、APIを有効にするプロジェクトと、OAuthクライアントを作るプロジェクトをそろえます。

1. [Google Cloudコンソール](https://console.cloud.google.com/)で、利用するプロジェクトを選択する
2. **APIとサービス → ライブラリ**で「Google Drive API」を探す
3. **有効にする**を押す。すでに有効なら、そのまま次へ進む

Googleの[Pythonクイックスタート](https://developers.google.com/workspace/drive/api/quickstart/python)でも、最初にDrive APIの有効化を行います。

ここで設定するのはGoogle DriveのAPIです。Google Cloud Storageのバケット作成とは別の作業です。

## 2. OAuth同意画面とアクセス範囲を設定する

**Google Auth Platform**を開き、未設定なら開始画面からアプリ情報を登録します。設定済みの場合は、**ブランディング・対象・データアクセス**から各項目を確認できます。

### アプリ情報と利用対象

アプリ名は、あとでGoogleの認可画面に表示されます。自分が何のために作ったものか分かる名前にします。ユーザーサポートメールと連絡先メールも登録します。

![Google Auth Platformのアプリ情報入力画面。アプリ名とメールアドレスは除去済み](/assets/images/blog/2026-10-04-google-drive-api-oauth/oauth-branding.png)

個人のGoogleアカウントで試す場合は、利用対象を**外部**にし、テストユーザーに自分のアカウントを追加します。「内部」はGoogle Workspaceなどの組織内向けの選択肢なので、「自分しか使わないから内部」とは限りません。

![OAuthアプリの利用対象として内部または外部を選ぶ画面](/assets/images/blog/2026-10-04-google-drive-api-oauth/oauth-audience.png)

連絡先情報とポリシーへの同意を確認して作成したら、**対象 → テストユーザー → ユーザーを追加**から、認可に使うアカウントを登録します。手順の詳細は[OAuth同意画面の設定](https://developers.google.com/workspace/guides/configure-oauth-consent)を参照してください。

### スコープは必要な範囲に絞る

スコープは、アプリに許可する操作範囲です。今回の例では、**データアクセス → スコープを追加または削除**から次のスコープを選び、保存します。

```text
https://www.googleapis.com/auth/drive.file
```

後で実行するPython側でも同じスコープを指定します。

`drive.file` は、アプリが作成したファイルや、利用者がそのアプリに共有・選択したファイルを対象にします。**既存フォルダのIDを指定するだけで、その中の全ファイルにアクセスできるわけではありません。**

新しくアプリから保存先フォルダを作る方法や、Google Pickerで既存の対象を選ぶ方法があります。既存CSVを読み書きする構成では、対象ファイルにアクセスできることも確認が必要です。

Drive全体を操作できる `drive` スコープへ安易に広げず、[Google Drive APIのスコープ一覧](https://developers.google.com/workspace/drive/api/guides/api-specific-auth)で必要な権限を確認します。

## 3. デスクトップ用OAuthクライアントを作る

今回は、**自分のPCでブラウザを開いて認可する**ため、デスクトップアプリ用のクライアントを作ります。GitHub Actions上でブラウザのログイン操作を行う手順ではありません。

1. **Google Auth Platform → クライアント**を開く
2. **クライアントを作成**を選ぶ
3. アプリケーションの種類を**デスクトップアプリ**にする
4. 管理用の名前を付けて作成する
5. 作成したクライアントのJSONをダウンロードする

![OAuthクライアントIDの作成画面。デスクトップアプリを選択し、管理用の名前は除去済み](/assets/images/blog/2026-10-04-google-drive-api-oauth/oauth-client.png)

ダウンロードしたJSONは、次の作業フォルダへ `credentials.json` という名前で保存します。ソースコードへクライアントシークレットを直接書き込む必要はありません。

Googleの[デスクトップアプリ向けOAuthガイド](https://developers.google.com/identity/protocols/oauth2/native-app)に沿って、ローカルのブラウザとループバックアドレスで認可結果を受け取ります。

## 4. 手元のPythonでリフレッシュトークンを取得する

以下はWindowsのPowerShellでの例です。Pythonをインストールし、`py --version` で起動できることを確認しておきます。

### Gitの管理対象外に作業フォルダを用意する

認証情報の一時保存先は、リポジトリやOneDriveなどの同期フォルダから分けます。次の例は、自分のローカルアプリデータ配下に作業フォルダを作ります。

```powershell
$oauthWork = Join-Path $env:LOCALAPPDATA 'drive-oauth-setup'
New-Item -ItemType Directory -Force -Path $oauthWork | Out-Null
Set-Location $oauthWork
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade google-auth-oauthlib
```

このフォルダに `credentials.json` を置きます。ほかの人と共用するフォルダには保存しないでください。

### 値を画面に表示せず保存する

同じフォルダに `get_refresh_token.py` を作り、次のコードを保存します。

```python
import json
import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

WORK_DIR = Path(__file__).resolve().parent
OUTPUT = WORK_DIR / "github-secrets.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

if OUTPUT.exists():
    raise SystemExit("保存済みのファイルがあります。内容を確認してください。")

flow = InstalledAppFlow.from_client_secrets_file(
    str(WORK_DIR / "credentials.json"), SCOPES
)
credentials = flow.run_local_server(
    host="127.0.0.1",
    port=0,
    authorization_prompt_message="開いたブラウザで認可してください。",
    access_type="offline",
    prompt="consent",
)

if not credentials.refresh_token:
    raise SystemExit("リフレッシュトークンを取得できませんでした。")

values = {
    "GOOGLE_CLIENT_ID": credentials.client_id,
    "GOOGLE_CLIENT_SECRET": credentials.client_secret,
    "GOOGLE_REFRESH_TOKEN": credentials.refresh_token,
}
fd = os.open(OUTPUT, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as output_file:
    json.dump(values, output_file, ensure_ascii=False, indent=2)

print("認証情報をgithub-secrets.jsonに保存しました。値は表示しません。")
```

このコードは、Googleの[OAuthクライアントライブラリ](https://googleapis.dev/python/google-auth-oauthlib/latest/reference/google_auth_oauthlib.flow.html)を使います。`port=0` で空いているポートを使い、`127.0.0.1` で自分のPCからの応答だけを受け付けます。認可URLやトークンを `print()` で表示しません。

保存ファイルは平文です。`0o600` は対応するOSでは所有者だけの読み書き権限になりますが、Windowsのアクセス制御をこれだけで設定できるわけではありません。保存先フォルダを共有せず、必要な登録を終えたら一時ファイルを削除します。

### ブラウザでアカウントと許可内容を確認する

PowerShellから実行します。

```powershell
.\.venv\Scripts\python.exe .\get_refresh_token.py
```

ブラウザが開いたら、テストユーザーに登録したアカウントを選びます。自分が設定したアプリであることと、要求される権限が想定どおりであることを確認して許可します。

![Googleの認可画面に表示されるDriveの特定ファイルへのアクセス権限と許可ボタン。アプリ名などは除去済み](/assets/images/blog/2026-10-04-google-drive-api-oauth/oauth-consent.png)

見覚えのないアプリや、必要以上の権限が表示された場合は、そのまま進まず設定を確認します。認可が完了すると同じPCのローカル画面へ戻り、作業フォルダに `github-secrets.json` が作成されます。

保存先はスクリプトと同じフォルダです。2回目以降は既存ファイルを上書きせず停止するので、再取得する場合は、以前のファイルが必要かを確認してから片付けます。

## 5. GitHub Secretsへ登録する

`github-secrets.json` をローカルのエディタで開き、3つの値をそれぞれ対応するRepository Secretへ登録します。JSON全体ではなく、各項目の値だけをコピーします。引用符やカンマは含めません。

| 保存された項目 | GitHub SecretsのName |
| --- | --- |
| `GOOGLE_CLIENT_ID` | `GOOGLE_CLIENT_ID` |
| `GOOGLE_CLIENT_SECRET` | `GOOGLE_CLIENT_SECRET` |
| `GOOGLE_REFRESH_TOKEN` | `GOOGLE_REFRESH_TOKEN` |

保存先の `GOOGLE_DRIVE_FOLDER_ID` は別途設定します。認証情報を取得しただけでは、保存先のフォルダは作成されません。`drive.file` でそのフォルダにアクセスできる構成になっているかも確認します。

{% capture actions_yml_url %}{% post_url 2026/04/2026-04-16-GitHub Actions の yml は何を書いているのか %}{% endcapture %}
{% include bookmark-card.html
  url=actions_yml_url
  title="GitHub Actions の yml は何を書いているのか"
  description="SettingsからSecretsを登録し、env経由でPythonに渡すまでをスクリーンショット付きで説明します。"
  label="関連記事"
%}

GitHub Actionsでは、保存したリフレッシュトークンからアクセストークンを更新してAPIを使います。初回の対話的な認可と、定期実行時のトークン更新を分けて考えると整理しやすくなります。

登録を終えたら、ローカルの `credentials.json` と `github-secrets.json` は必要な保管方針を決め、一時コピーを削除します。コード、実行ログ、Issue、記事用スクショへ値を貼り付けないようにします。

## テスト運用でつまずきやすい点

### 外部・テスト中のトークンは7日で期限切れになる

利用対象が**外部**、公開ステータスが**テスト中**でDriveのスコープを要求した場合、リフレッシュトークンの有効期間は7日です。名前・メール・プロフィールだけの例外には、今回の `drive.file` は当てはまりません。

そのため、ここまでの設定は初回の検証用として考えます。継続運用に進むときは、対象ユーザー・スコープ・必要な審査を確認したうえで公開ステータスを検討し、移行後の設定で認可し直します。「本番環境」にしただけで、過去に発行したトークンが無期限になるとは考えないようにします。

また、権限の取り消しなどでもトークンは使えなくなります。詳細は[Googleのリフレッシュトークンの有効期限](https://developers.google.com/identity/protocols/oauth2#expiration)を確認してください。

### 認可できたのにファイルが見つからない

まず、選択したGoogleアカウント、対象ファイル、許可したスコープを確認します。`drive.file` はDrive全体のアクセス権ではないため、認可の成功と、特定の既存ファイルを操作できることは別です。

「APIが無効」というエラーなら、クライアントを作ったプロジェクトでDrive APIを有効にしたか確認します。認可時に利用を拒否された場合は、テストユーザーの登録や組織側の制限も確認します。

## まとめ

今回の流れは、Drive APIの有効化、OAuth同意画面の設定、デスクトップ用クライアントの作成、ローカルでの認可、GitHub Secretsへの登録です。

まず認証情報を準備し、次に、その権限で保存先を操作できるかを確認します。定期実行へ進める前に、スコープとトークンの期限を押さえておくと、認可とファイル操作の問題を切り分けやすくなります。
