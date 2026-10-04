# 記事のレスポンシブ表示検査

運用の正本は [README](../README.md)。本手順は #32 の回帰検査と、本番公開前の実機確認を補足します。

## 自動検査

READMEの依存関係を準備し、リポジトリ直下で実行します。

```powershell
bundle exec jekyll build --trace
python scripts/check_post_layout.py
python -m pip install -r tests/requirements-browser.txt
python -m playwright install chromium webkit
python scripts/check_responsive_layout.py
```

LinuxでブラウザのOS依存関係が不足する場合は `python -m playwright install --with-deps chromium webkit` を利用します。

- 全生成記事を320 / 375 / 390 / 430 / 768 / 1039 / 1040 / 1041 / 1440pxで検査します。
- タイトル・本文・記事フッターの幅を `min(画面幅 - 40px, 760px)` と照合し、左右位置、配置順、Gridの列数、ページ横overflowも確認します。
- 390pxで目次を開閉して見出しへ移動し、長いコードはwheel入力で右端・左端へ実際にスクロールさせます。
- 元のGrid領域名とコードoverflowの不具合を検査中に一時的に再現し、検査が検出することも確認します。ソースファイルは変更しません。
- ローカル画像とナビゲーション先を検査し、トップ・記事一覧の横overflowも確認します。
- ブラウザはローカルサーバー以外の通信を遮断します。GAへのアクセス送信や外部リンク先の検査は行わず、外部Webフォントはフォールバックフォントになります。

測定値と390pxの画面キャプチャは `_layout-report/` に出力します。このフォルダはGitに登録しません。
CIでは既存の `Jekyll build and content` チェック内で実行し、測定値・画像とビルド済みサイトをActionsのArtifactsに14日間保存します。Artifactsは公開用のステージングURLではありません。

## 運営者の実機確認

READMEに従い最新のdevを取得し、未コミットの作業を上書きしないことを確認して `bundle exec jekyll serve` で表示します。iPhoneで確認する場合は、信頼できる同一LAN内のPCで `bundle exec jekyll serve --host 0.0.0.0` を実行し、Safariで `http://<PCのLAN内IP>:4000/` を開きます。外部公開・ルーターのポート開放は不要です。確認終了後はサーバーを停止し、一時的な受信許可を戻します。

現行テンプレートのGAスクリプトはローカルビルドにも含まれます。手動確認時にアクセスを計測させたくない場合は、確認用ブラウザのコンテンツブロッカーなどで計測通信を遮断してください。自動検査は前述の通信遮断を行います。

確認項目:

- 本文の右側だけに大きな空白がなく、タイトル・本文・記事末尾が同じ幅で表示される。
- 長いコードを指で左右へ動かして末尾まで読める。ページ全体は横に動かない。
- 目次の開閉・見出しリンク、画像、表、長いURL・インラインコード、関連記事、一覧へ戻るリンクが正常。
- トップ・記事一覧・PC表示に意図しない変化がない。

Issueに確認対象dev SHA、機種、iOS/Safariのバージョン、画面幅または向き、結果を記録します。WebKitの自動検査はiOS Safari実機の代わりではありません。

運営者の確認と明示的な公開指示が完了するまで、mainへのマージ・本番公開は行いません。
