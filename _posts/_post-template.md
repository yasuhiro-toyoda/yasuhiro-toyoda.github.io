---
# ブログ記事テンプレート
# このファイルをコピーして、_posts/YYYY-MM-DD-slug.md として使ってください。
layout: post
title: ""
description: ""
date: 2026-12-31 00:00:00 +0900
updated_at:
category: 開発
tags:
  - dev-memo
excerpt: ""
---

{% comment %}
コールアウト例:
{% capture callout_body %}
ここに補足を書きます。

- 箇条書きも使えます
- Markdown も使えます
{% endcapture %}
{% include callout.html type="tip" title="補足メモ" content=callout_body %}

ブックマークカード例:
{% include bookmark-card.html
  url="https://example.com/"
  title="参考リンクのタイトル"
  description="記事内で紹介したい外部ページをカード風に表示できます。"
  label="Reference"
%}
{% endcomment %}

## この記事で伝えたいこと

導入文を書きます。

## 本文

本文を書きます。

## まとめ

締めを書きます。
