# ブランド素材の使い方

2026-10-04にF4の文字ロゴとG1の共通アイコンを正式採用しました。
支給素材は `musashi-brand-assets-2026-10-04.zip`、関連Issueは [#14](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/issues/14) と [#15](https://github.com/yasuhiro-toyoda/yasuhiro-toyoda.github.io/issues/15) です。

正式名は **Musashi Digital Studio**、短縮名は **Musashi Studio** です。
G1のMはMusashiの頭文字を表し、MDSという略称は使用しません。

## 掲載場所と素材

| 場所・用途 | 素材 | 仕様 |
| --- | --- | --- |
| 共通ヘッダー | `assets/brand/wordmark-f4.svg` | 2段の文字ロゴ。背景透過、viewBox 1300 × 448 |
| 暗い背景 | `assets/brand/wordmark-f4-white.svg` | 白抜き版 |
| 単色印刷など | `assets/brand/wordmark-f4-mono.svg` | 濃紺1色 |
| 背景のないシンボル | `assets/brand/symbol-g1.svg` | 濃紺のM。背景透過 |
| SVGが使えない掲載先 | `assets/brand/wordmark-f4*.png` | 通常・白抜き・単色の透過PNG。通常・白抜きは2倍サイズも同梱 |
| favicon | `assets/brand/icons/favicon.svg` / `favicon.ico` | G1。ICOには16 / 32 / 48pxを格納 |
| 小サイズの確認・PNG用途 | `assets/brand/icons/favicon-16.png` / `favicon-32.png` / `favicon-48.png` | G1の16 / 32 / 48px |
| Appleのホーム画面 | `assets/brand/icons/apple-touch-icon.png` | G1の180 × 180px |
| manifest | `assets/brand/icons/icon-192.png` / `icon-512.png` | G1の192 / 512px。`purpose: any` |
| 屋号のSNSプロフィール | `assets/brand/icons/social-1024.png` | G1の1024 × 1024px。プロフィールへの設定は別途実施 |

ヘッダーのロゴはトップページへリンクし、`site.title` を代替テキストに使用します。
表示幅はPCで200〜260px、640px以下では最大220pxとし、縦横比を保ちます。
SVGの文字は輪郭のパスで構成されているため、表示先にフォントを追加する必要はありません。

## 配色と使い分け

| 用途 | 色 | サイトのCSSとの対応 |
| --- | --- | --- |
| Musashi・単色ロゴ・アイコン背景 | `#1f3d5a` | `--accent-strong` |
| Digital Studio | `#2f5f8f` | `--accent` |
| アイコンのM・白抜きロゴ | `#ffffff` | 白 |

明るい背景には通常版、暗い背景には白抜き版を使います。
G1は背景込みの正方形を原本とし、角丸・円形への切り抜きは表示先に任せます。
個別アプリのアイコンはそのアプリの名前・機能に応じて別途設計できます。

## manifestと更新時の確認

`site.webmanifest` はJekyllで処理し、正式名・短縮名を `_config.yml` から、`id`・`start_url` を `relative_url` から生成します。
アイコンのパスはmanifest自身を基準に解決します。表示モードは `browser` です。
名称や掲載パスを変えた場合は、HTMLだけでなく生成後のmanifestも確認してください。

1. `bundle exec jekyll build --trace` と `python scripts/check_post_layout.py` を実行する。
2. PC・スマートフォン幅でヘッダー、説明文、ナビゲーションの重なりや横方向のはみ出しを確認する。
3. ロゴのトップページリンクと正式名の代替テキスト、キーボード操作を確認する。
4. favicon、Apple用アイコン、manifest、manifest内の画像が正常に読み込めることと、サイズ・配色を確認する。
5. 公開指示後は、公開ページと実際のタブ・端末のホーム画面でも反映を確認する。

今回の採用・実装と本番公開は別工程です。公開はREADMEのdev→main手順と明示的な公開指示に従います。

## 組み込み後の表示

2026-10-04にJekyllでビルドしたサイトをChromiumで確認した画像です。

| PC（1440px幅） | スマートフォン幅（390px） |
| --- | --- |
| ![PC幅のヘッダーとトップページ](brand-assets/desktop.png) | ![スマートフォン幅のヘッダーとトップページ](brand-assets/mobile.png) |
