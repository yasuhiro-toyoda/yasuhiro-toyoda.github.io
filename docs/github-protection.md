# GitHubの保護設定

これは適用する設定と手順です。ファイルの存在はGitHub側で有効になったことを意味しません。
現在の状態はSettings → Rules → Rulesetsと、PRの必須チェック欄で確認します。

## main用ルールセット

Settings → Rules → Rulesets → New ruleset → New branch rulesetで次を設定します。

| 項目 | 値 |
| --- | --- |
| Name | Protect main publication |
| Enforcement status | Active |
| Bypass list | 空欄（管理者・Codexを含め例外なし） |
| Target branches | Include by pattern: main |
| Restrict deletions | 有効 |
| Block force pushes | 有効 |
| Require a pull request before merging | 有効 |
| Required approvals | 0 |
| Require review from Code Owners | 無効 |
| Require approval of the most recent reviewable push | 無効 |
| Allowed merge methods | Merge |
| Require status checks to pass | 有効 |
| Required checks | Publication source / Jekyll build and content |
| Expected source | GitHub Actions |
| Require branches to be up to date before merging | 有効 |
| Do not require status checks on creation | 無効 |

Restrict updatesやRequire linear historyは有効にしません。通常のマージができなくなります。
Settings → GeneralでもAllow merge commitsを有効、Automatically delete head branchesを無効にしてdevを維持します。
公開前の自動マージは使用しません。

## 初回導入

1. 現在のmainからdevを作成します。
2. 実装した作業ブランチ→devのPRを作成し、両チェックが成功することを確認します。
3. そのPRをdevに反映します。本番サイトはまだ更新されません。
4. dev→mainのPRを作成し、必須チェックの候補に2つの名前が表示されることを確認します。
5. 上記のmain用ルールセットを有効にします。候補がない場合は名前を推測せず実行履歴を確認します。
6. dev→mainのPRで両チェックの成功とルールの適用を確認します。
7. READMEの明示的な公開指示を受けた後にのみ、この初回PRをマージします。

CIを定義した作業ブランチのPRでもチェックは実行できます。mainへの直接pushは不要です。

## 確認すること

- dev→mainのPRではPublication sourceが成功する。
- main宛てでdev以外・別リポジトリ由来の場合、Publication sourceが失敗する。
- ビルド失敗・記事検査失敗時はマージできない。
- mainへの直接push、force push、削除を許可していない。
- 管理者も通常操作でルールを回避できない。

Publication sourceはPRに含まれるワークフローで判定します。事故防止のチェックであり、書き込み権限を持つ人が検査コードを変更することまで防ぐものではありません。
ワークフロー変更も差分レビューの対象にします。
同じアカウントを運営者とCodexが使う場合、GitHubは両者の承認意思を区別できません。READMEの公開指示を守ります。

## 設定用JSON

[main-ruleset.json](main-ruleset.json) は上記のREST API用設定です。
GitHub管理権限がある環境では、新規作成時に次を使えます。既に同名ルールがある場合は重複作成せず確認します。

~~~shell
gh api --method POST repos/yasuhiro-toyoda/yasuhiro-toyoda.github.io/rulesets --input docs/main-ruleset.json
~~~

実行にはリポジトリ管理権限が必要です。コードの書き込み権限だけでは適用できません。
JSONをGitに追加しても適用されないため、APIの成功応答とRulesets画面を確認します。

## 参考

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/rest/repos/rules#create-a-repository-ruleset
