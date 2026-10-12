# Gitで削除したファイルを戻す：検証記録

検証日：2026年10月12日（日本時間）。実行ログの作成時刻は18:01:41です。

## 実行環境と方法

- Linux 6.18.44 / x86_64 / glibc 2.39
- Git 2.51.1、Python 3.12.14
- PythonのsubprocessからGitコマンドを実行。Windows 11やPowerShellでの実行ではありません。
- ケースごとに新規の一時リポジトリを作成。ブログリポジトリでは復元実験をしていません。
- pushの検証にはローカルのbareリポジトリを使用。GitHubの権限やブランチ保護の検証ではありません。
- グローバルGit設定を無効にし、架空の名前・メールアドレスを一時リポジトリ内だけに設定。
- 実行時のstdout、stderr、終了コード、ファイル内容、status、履歴を記録し、期待結果と照合。

## 再実行

Git 2.23以降とPython 3.11以降がある環境で、リポジトリのルートから実行します。追加のPythonパッケージは不要です。

```text
python3 docs/git-file-recovery/verify_recovery.py
```

Windowsでは、Pythonの起動コマンドが `python` または `py` の環境もあります。スクリプトはGitを直接呼び出します。今回の実行結果はLinuxで得たものであり、Windowsで同じ結果を確認したという意味ではありません。

新規の一時ディレクトリ内で操作し、終了後にそのディレクトリを削除します。コマンドログに表示されるシェル引用はLinuxでの表示用で、記事のPowerShellコードとは区別してください。コミットハッシュは実行ごとに変わります。

## 結果

9ケースすべてで期待結果を確認しました。失敗を期待したケースでは、Gitがエラーまたは競合を返すことを確認しています。

| ケース | 確認した結果 |
| --- | --- |
| 1. 未ステージの削除 | 実ファイルを復元。他の未コミット編集を維持。HEADは変更なし |
| 2. ステージ済みの削除 | `--staged` だけでは実ファイルは欠落したまま。`--source=HEAD --staged --worktree` で両方を復元 |
| 3. ステージした編集後に実ファイルを削除 | HEADではなくインデックスの版が戻り、ステージ済みの編集は残る |
| 4. 複数の変更を含む削除コミットから1ファイルを復元 | 復元後は `??`、add後は `A `。他のステージ済み・未ステージの編集を維持。HEADは変更なし |
| 5. push済みの削除をrestore＋commitで復元 | 通常のpush成功。bare側のファイル内容を確認。削除コミットも履歴に残る |
| 6. push済みの複合コミットをrevert | 同じコミットに含まれる別ファイルの編集も取り消される。後続の無関係なコミットは残る |
| 7. 再追加とぶつかるrevert | add/add競合。`revert --abort` で元の内容・HEAD・cleanな状態に戻る |
| 8. 一度もaddしていない新規ファイルの削除 | restoreが終了コード1で失敗し、ファイルは欠落したまま |
| 9. addしていない編集後の削除 | 記録済みの古い版だけが戻り、新しい編集は戻らない |

[実行ログ](verification-output.txt)と[検証スクリプト](verify_recovery.py)を参照してください。

## 検証の範囲

通常のテキストファイルを扱っています。マージコミットの取り消し、名前変更・移動が絡む復元、Git LFS、サブモジュール、浅いclone、Windows固有の大文字小文字・改行・文字コードの違い、サーバーの権限や保護設定は今回の実行検証の対象外です。

## 公式資料

確認日：2026年10月12日。

- https://git-scm.com/docs/git-restore
- https://git-scm.com/docs/git-restore/2.23.0
- https://git-scm.com/docs/git-status
- https://git-scm.com/docs/git-log
- https://git-scm.com/docs/git-show
- https://git-scm.com/docs/gitrevisions
- https://git-scm.com/docs/git-fetch
- https://git-scm.com/docs/git-branch
- https://git-scm.com/docs/git-revert
- https://git-scm.com/docs/git-add

記事では基本コマンドの列挙を既存記事に任せ、状態を見て復元方法を選ぶ具体例に絞っています。
