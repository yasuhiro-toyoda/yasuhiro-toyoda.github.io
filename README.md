# Musashi Studio

`musashistudio.com` 向けの GitHub Pages / Jekyll サイトです。

## README に記載すること

- 公開しても問題ない運用ルール
- 記事追加や更新の手順
- タグ管理の方法
- ディレクトリ構成と関連ファイルの場所
- ローカル確認や公開フローの概要

## README に記載しないこと

- ログイン情報や API キーなどの秘密情報
- ドメイン管理サービスや外部サービスの管理画面情報
- 個人情報や内部向けの連絡先
- セキュリティ上の弱点になりうる詳細情報
- 未公開の企画や内部判断メモ

## セットアップ

1. Ruby と Bundler をインストールします。
2. 依存関係を入れます。

```powershell
bundle install
```

3. ローカルサーバーを起動します。

```powershell
bundle exec jekyll serve
```

4. `http://127.0.0.1:4000` を開いて確認します。

## 公開

- `main` ブランチへ push すると GitHub Pages で公開される想定です。
- カスタムドメイン設定は [CNAME](/CNAME) を使っています。

## 記事運用ルール

- 記事は [`_posts`](/_posts) に Markdown で追加します。
- ファイル名は `_posts/YYYY-MM-DD-slug.md` の形式にします。
- 新規記事は [`_posts/_post-template.md`](/_posts/_post-template.md) をコピーして作成します。
- `title` `description` `date` `category` `tags` `excerpt` は必ず確認してから公開します。
- 見出しは必要最小限にし、内容がすぐ分かるタイトルを付けます。
- 公開記事として読まれる前提で、個人情報や機密情報は含めません。

## タグ運用ルール

- 利用するタグは [`_data/blog_tags.yml`](/_data/blog_tags.yml) で管理します。
- 記事の `tags` には `blog_tags.yml` にある `slug` を指定します。
- 新しいタグを追加する場合は、`slug` と表示名の `label` をセットで追加します。
- タグは増やしすぎず、似た意味のものは統合を優先します。

## 更新メモ

- 記事は [`_posts`](/_posts) に Markdown で追加します。
- 固定ページは `index.html` や [`about/index.html`](/about/index.html) などの HTML ファイルで管理します。
- ツモログの固定ページは [`apps/tsumolog/`](/apps/tsumolog/) 配下にあります。
