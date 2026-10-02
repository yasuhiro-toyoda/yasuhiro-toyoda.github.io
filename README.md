# Musashi Studio

[musashistudio.com](https://musashistudio.com) 向けの GitHub Pages / Jekyll サイトです。

## 運用方針

Giteaの試験運用は終了し、Codexによるリモート操作を記事作成・更新・公開の基本とします。
ローカルでの画面確認も引き続き利用できます。端末による運用ルールの違いはありません。

| 担当 | 役割 |
| --- | --- |
| 運営者 | 題材提供、本文・画像・差分の確認、公開判断 |
| Codex | 下書き、ファイル操作、検証、PR作成、公開指示後のマージ、公開確認 |
| GitHub Actions | PRの反映元、記事形式、Jekyllビルドの自動検査 |
| GitHub Pages | mainに反映された内容のビルド・本番公開 |

運用の正本はこのREADMEです。Codex向けの注意は [AGENTS.md](AGENTS.md) に記載します。
保護設定はファイル追加だけでは有効になりません。[初期設定手順](docs/github-protection.md) に従って適用・確認します。

## ブランチとPR

- mainは本番用です。例外なく、同じリポジトリのdevからmainへのPRで反映します。
- main上での直接編集・コミット・直接push、他ブランチからのマージ、mainへのcherry-pickは禁止します。
- 作業は最新のdevからpost/...、fix/...、chore/...を作成し、1ブランチ1目的にします。
- 未確認の変更は作業ブランチに置き、確認と検査を終えた変更をPRでdevに集めます。
- devには次回公開可能な変更だけを置き、公開時にdevとmainの差分全体を確認します。
- dev→mainはマージコミット方式で反映します。公開後もdevは削除しません。
- 公開後はmainをdevへ通常のマージで取り込み、次回作業前に同期します。force pushは使いません。
- 1記事ずつ公開し、記事追加とサイト構成変更を同じ公開に混ぜません。コミットも1目的ずつに分けます。

### 公開指示

次の一文を含む、運営者からの明示的な実行指示を本番反映の条件とします。

> devブランチをmainにマージして、公開して。

「公開して」だけでは本番反映しません。引用、相談、文案、README内の記述も実行指示として扱いません。
公開承認は確認済みの差分とdevのコミットSHAに対して有効です。追加変更・競合解消でSHAや差分が変わった場合は再確認します。
PRの自動マージを事前に有効にせず、承認後に対象SHAを指定してマージします。

コピー用:

> musashistudio.comのブログについて、確認済みの変更を含むdevブランチをmainにマージして、公開して。
>
> 実行前にdevとmainの差分を確認し、未確認の変更が含まれる場合や、公開前チェックに失敗した場合は停止して報告してください。
>
> 問題がなければPRをマージし、GitHub Pagesの公開処理の成功と公開ページの表示を確認して、公開URLを報告してください。

## 記事作成から公開まで

1. 最新のdevから作業ブランチを作り、題材・読者・記事の目的を確認します。
2. [テンプレート](templates/post.md) から下書きを作り、本文とサムネイルを運営者と調整します。
3. 記事・画像を配置し、日付、カテゴリ・タグ、要約、画像パス、出典・リンクを確認します。
4. 作業ブランチ→devのPRを作成し、差分と検査結果を確認してdevに反映します。
5. dev→mainのPRを作成し、差分全体、公開対象、devのSHA、検査結果を運営者に提示します。
6. 公開指示を受け、対象SHAとmainが変わっていないこと、必須チェックの成功を確認してPRをマージします。
7. 該当コミットのPages処理の成功と、公開ページの本文・画像・リンク・記事一覧を確認します。
8. 公開URL、反映コミット、確認結果を報告します。処理失敗・表示未確認なら「公開完了」と報告しません。

画像生成機能の利用可否は実行環境によります。画像を実ファイルとして取得・配置できたことまで確認します。
生成・転送・画面確認ができない場合、その工程を未完了として報告します。

## 記事・画像の配置

- 公開記事: _posts/YYYY/MM/YYYY-MM-DD-slug.md
- 下書き: _drafts/slug.md または _drafts/YYYY/MM/slug.md
- サムネイル: assets/images/blog/YYYY-MM-DD-short-slug/thumbnail.png
- thumbnailには/assets/images/blog/...形式のパス、thumbnail_altには画像の説明を設定します。
- 参考画像はtemplates/thumbnail/にあります。見た目と容量を確認してから配置します。
- ファイル名の日付とfront matterのdateを一致させ、日本時間の実際の公開日時を指定します。
- テンプレートの例示日付をそのまま使いません。future: falseのため未来日時の記事は表示されません。
- title、description、date、category、tags、excerptを確認します。
- 見出しは必要最小限とし、内容が分かるタイトルにします。未経験のことを実体験として書きません。

### カテゴリ・タグ

- categoryは [_data/blog_categories.yml](_data/blog_categories.yml) のlabelから1つ選びます。
- 現在のカテゴリは「開発」「アプリ情報」「作業効率化」「その他」です。
- tagsは [_data/blog_tags.yml](_data/blog_tags.yml) のslugを指定します。
- 新規タグにはslugとlabelを追加し、類似タグは統合を優先します。
- カテゴリ追加前に既存で代用できないか確認し、追加後は一覧の絞り込みを確認します。

## 公開前チェック

[Publish checks](.github/workflows/publish-checks.yml) はmain・dev宛てPRで実行します。パスによる実行除外はありません。

| チェック名 | 内容 |
| --- | --- |
| Publication source | main宛てPRが同一リポジトリのdevからであること |
| Jekyll build and content | 検査スクリプトのテスト、新規・変更記事の必須項目・日付・カテゴリ・タグ、全記事のサムネイル存在確認、Jekyllビルド、生成後の記事レイアウト検査 |

過去記事を一括修正するものではありません。既存記事も編集時に形式検査の対象となります。
画像の見た目、文章の正確性、外部リンクの到達性、本文中のリンクは人またはCodexが別途確認します。
検査成功は公開承認の代わりにはなりません。

リモート環境にはGit、Ruby 3.3系、Bundler 2.6.9、記事検査用Python 3.11以上が必要です。
CIはLinux用の依存プラットフォームを追加解決してからビルドします。既存のWindows用ロック情報は維持します。
Pages側の本番ビルド結果も別途確認します。

## ローカルでの画面確認

### 初回

Ruby・Bundler・Gitを準備します。WindowsではRubyInstaller + Devkitを利用できます。

~~~powershell
git clone https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io.git
cd yasuhiro-toyoda.github.io
gem install bundler -v 2.6.9
git fetch origin
git switch dev
bundle install
~~~

### 2回目以降

まず未コミットの変更を確認します。変更があれば上書きせず、作業ブランチに保存してから切り替えます。

~~~powershell
git status --short
git fetch origin
git switch dev
git pull --ff-only origin dev
bundle install
bundle exec jekyll serve
~~~

http://127.0.0.1:4000 を開き、本文・画像・一覧・スマートフォン幅の表示を確認します。
作業ブランチを確認する場合はそのブランチに切り替えて起動します。
下書きを表示する場合だけ次を使い、ローカル端末内で確認します。

~~~powershell
bundle exec jekyll serve --drafts
~~~

ビルドのみの確認:

~~~powershell
bundle exec jekyll build --trace
~~~

ローカル閲覧は本番公開になりません。修正も作業ブランチ→dev→mainの経路を守ります。

### 記事の共通レイアウト

記事ページはタイトル、公開日・更新日・カテゴリ・タグ、アイキャッチ、導入文、目次、本文の順です。
`excerpt` は記事一覧用に保持し、`description` とともにメタ情報にも使います。記事上部に要約ボックスは表示しません。
共通テンプレートが本文中のH1をH2に揃え、冒頭の重複タイトルや導入用の見出しを省いて、既存の導入内容を残します。
見出しから始まる過去記事では、直後の通常段落を導入文に利用します。記事作成時は、最初のH2より前に短い導入文を置きます。

目次はH2が3つ以上ある場合にビルド時に自動生成します。H2のみを掲載し、初期状態は折りたたみます。
本文中のコード例は見出しとして数えません。記事ごとの目次設定や追加プラグインは不要です。
関連記事は同カテゴリかつ具体的なタグが共通する記事を、一致数の多い順・新しい順で最大3本表示します。
`dev-memo`、`workflow`、`beginner`、`site-info`だけの一致では表示しません。該当記事がなければ一覧へ戻るリンクのみ表示します。

ビルド後の全記事と一覧の構造を確認するコマンド:

~~~powershell
python scripts/check_post_layout.py
~~~

## 失敗・取り消しへの対応

- 検査失敗は作業ブランチで修正して再実行します。チェックや保護を外して通しません。
- 公開後の問題は原因と影響を報告し、修正・取り消しの差分を作業ブランチで用意します。
- 必要に応じてrevertで変更を打ち消し、mainの履歴を書き換えません。
- 修正・取り消しもdev→mainのPR、検査、明示的な公開指示を経て反映します。

## 公開情報の範囲

このリポジトリは公開されています。下書きや作業ブランチもGitHub上では閲覧可能です。
_draftsは「サイトに未掲載」であり「非公開保管場所」ではありません。
個人情報、秘密情報、APIキー、未公開の内部判断メモをコミットしません。
READMEには公開可能な運用ルール・更新手順・構成を記載します。

固定ページはindex.htmlやabout/index.htmlなど、ツモログのページはapps/tsumolog/配下にあります。
ドメインは [CNAME](CNAME)、サイト設定は [_config.yml](_config.yml) を参照します。
