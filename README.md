# Musashi Studio

`musashistudio.com` 向けの GitHub Pages / Jekyll サイトです。

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

## 運用メモ

- 記事は [`_posts`](/_posts) に Markdown で追加します。
- 固定ページは `index.html` や [`about/index.html`](/about/index.html) などの HTML ファイルで管理します。
- ツモログの固定ページは [`apps/tsumolog/`](/apps/tsumolog/) 配下にあります。
