---
layout: post
title: "GitHub Actionsを使った無料スクレイピング術"
description: "Python で取得・整形・CSV 出力・保存を分けて、GitHub Actions で回しやすい無料スクレイピング構成を整理します。"
date: 2026-04-16 00:00:00 +0900
updated_at:
category: 開発
tags:
  - workflow
  - beginner
  - dev-memo
excerpt: "スクレイピング処理を main / fetch / normalize / csv / upload に分けておくと、壊れにくく直しやすい構成にできます。"
---
{% capture related_yml %}
`workflow yml` の書き方だけを知りたい場合は、[GitHub Actions の yml は何を書いているのか]({{ '/blog/2026/04/16/github-actions-yml/' | relative_url }}) を先に読むと流れを追いやすいです。
{% endcapture %}
{% include callout.html type="info" title="関連記事" icon="🧩" content=related_yml %}

Python でスクレイピングしたデータを CSV にまとめ、GitHub Actions で定期実行する構成を整理します。

この記事では、全体をどう分割すると運用しやすいかに絞って、Python 側の役割分担を中心にまとめます。Secrets の受け渡しや `workflow yml` の意味は別記事に切り出しました。

## この記事で扱うこと

- Python スクリプトをどう役割分担するか
- データ取得から保存までをどうつなぐか
- 壊れやすい処理をどこで切り分けるか
- Secrets をコードに直書きしない考え方

反対に、この記事では次の内容は扱いません。

- 対象サイト固有の HTML 構造
- OAuth や API キーの取得画面
- Google Drive 側の初期設定手順
- `workflow yml` の詳しい書き方

## 全体の構成

今回の構成はかなりシンプルです。

GitHub Actions で定時に自動実行しつつ、

1. Web ページからデータを取得する
2. 保存しやすい形に整える
3. 書き込み先の CSV がなければ用意する
4. CSV に書き出す
5. Google Drive に保存する

という流れで動かします。

ファイル構成は、考え方としては次のようなイメージです。

```text
main.py
fetch_data.py
normalize.py
to_csv.py
drive_download.py
upload_to_drive.py
.github/workflows/upload-to-drive.yml
```

このように役割ごとにファイルを分けておくと、あとから修正しやすくなります。

スクレイピング処理はどうしても壊れやすいので、「取得」「整形」「保存」を一枚岩にしないのはかなり大事です。

## main.py は全体の司令塔

`main.py` は、各処理を順番に呼び出すだけの司令塔です。

イメージとしてはこうです。

```python
from fetch_data import fetch_data
from normalize import normalize
from to_csv import write_csv
from upload_to_drive import upload_csv
from drive_download import download_today_csv_if_exists

download_today_csv_if_exists()

raw = fetch_data()
normalized = normalize(raw)

csv_path = write_csv(normalized)

upload_csv(csv_path)
```

`main.py` の役割はとても単純です。

- まず既存の CSV があるか確認する
- 最新データを取得する
- データを整形する
- CSV に書き出す
- 最後に Google Drive にアップロードする

ポイントは、`main.py` 自体に細かいロジックを書かないことです。

各ファイルに役割を持たせておけば、`main.py` は流れだけを読めば処理全体を把握できるようになります。

## fetch_data.py は「取得」に専念する

ここはスクレイピング本体で、HTML を取得し、必要な表やテキストを取り出して、Python で扱いやすい形に変換します。

イメージとしては次のようになります。

```python
import requests
import pandas as pd
from io import StringIO

URL = "<TARGET_URL>"
SHOP = "<TARGET_NAME>"

def fetch_data() -> list[dict]:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers, timeout=10)
    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))
    df_raw = max(tables, key=lambda x: x.shape[0])

    records = []

    records.append({
        "shop": SHOP,
        "model": "...",
        "condition": "...",
        "remarks": "...",
        "price": 12345,
    })

    return records
```

ここで意識したいのは、「取得」と「整形」を混ぜすぎないことです。

`fetch_data.py` では次の役割だけに絞ります。

- `requests` で HTML を取得する
- `pandas.read_html()` などで表を取り出す
- 必要な列や行を抜き出す
- いったん `list[dict]` の形で返す

この段階で価格の丸めや日付変換まで全部やり始めると、あとからルール変更が入ったときに直しづらくなります。

## normalize.py は保存しやすい形にそろえる

スクレイピング直後のデータは、サイト都合の形になっています。

そのため、保存前に自分で使いやすい形へそろえる処理を 1 か所に寄せておくと運用しやすくなります。

たとえば、次のような処理です。

- 価格を数値型にそろえる
- 不要な空白や記号を取り除く
- 日付や取得時刻の列を追加する
- 列順を固定する
- 欠損値を補う

この層を分けておくと、取得元サイトが少し変わっても、保存形式を保ちやすくなります。

特に「今後 CSV ではなく DB に保存したい」といった変更が入ったときに、整形ルールを使い回しやすいです。

## to_csv.py は CSV 出力専用にする

スクレイピング結果は、そのままだと項目が揃っていなかったり、時刻が入っていなかったりします。

そこで `to_csv.py` では、最終的に保存するファイルの責務だけを持たせます。

たとえばここでやることは次のようなものです。

- 今日の日付を使ってファイル名を作る
- ヘッダー行をそろえる
- 既存 CSV に追記するか、新規作成するかを決める
- 文字コードや改行を安定させる

CSV に関する判断をここに集めておくと、あとから Excel 向けに調整したいときも修正箇所が明確です。

## Drive 連携は処理を分けておく

保存先が Google Drive のような外部サービスになる場合は、ダウンロード処理とアップロード処理も分けておくほうが安全です。

今回の構成では次の 2 つに分けます。

- `drive_download.py`: 既存の CSV を取得する
- `upload_to_drive.py`: できあがった CSV を保存する

こうしておくと、認証まわりのトラブルとスクレイピング本体のトラブルを切り分けやすくなります。

また、保存先を Google Drive から別サービスに変えたくなったときも、差し替え範囲をかなり限定できます。

## 分けておくと何が楽か

今回のようにファイルを分けておくと、運用と保守の両面でかなり楽になります。

- 取得元サイトの仕様変更に強くなる
- 保存先を CSV から DB に変えやすい
- GitHub Actions 側の不具合と Python 側の不具合を切り分けやすい
- 公開できる部分だけ抜き出して記事化しやすい
- 秘匿したい部分だけ伏せやすい

特に記事化の観点では大きくて、`fetch_data.py` の一部だけ伏せても、`normalize.py` や `to_csv.py` の考え方はそのまま公開できます。

## まとめ

{% capture article_points %}
- Python 側は「取得」「整形」「保存」で分ける
- `main.py` は流れだけをまとめる
- Secrets や実行タイミングの管理は GitHub Actions 側に寄せる
{% endcapture %}
{% include callout.html type="tip" title="今回のポイント" icon="💡" content=article_points %}

GitHub Actions を使った無料スクレイピング環境は、構成さえシンプルにしておけばかなり扱いやすいです。

取得部分ばかりに目が向きがちですが、実際にはその後の整形や保存、実行基盤まで含めて設計したほうが長持ちします。

`workflow yml` をどう書くかは別記事に分けたので、GitHub Actions 側の設定を整理したい場合は [GitHub Actions の yml は何を書いているのか]({{ '/blog/2026/04/16/github-actions-yml/' | relative_url }}) を続けて読むのがおすすめです。
