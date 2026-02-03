# JMA_hypodata_tocsv
気象庁の震源データをcsv化するツール
このスクリプトは**気象庁 震源データ**（ https://www.data.jma.go.jp/eqev/data/bulletin/hypo.html ）からダウンロードできる**固定長フォーマット震源データ**（それぞれの年でファイル名は「h○○○○」（○：年4桁））について、解析しやすい**CSV形式**に変換するためのツールです。

## 1.主な機能
- 固定長テキスト形式の震源データを解析しやすい形式に変換
- 変換する際に、緯度、経度、時刻、マグニチュードを数値化
- 出力形式を3段階から選択可能
- 複数ファイルの一括変換に対応

## 2.利用方法
「hypodata_tocsv.py」を **3.設定項目**で設定の上、実行してください。

## 3.設定項目
コード内にもコメント文で設定事項が記載されています。
変数 `file_setting` `output_format` `import_data` `output_csv` を変更して利用ください。

### `file_setting`
| 値 | 動作 |
| --- | --- |
| `1` | `import_data`で指定した **単一ファイル** を 'output_csv` へ出力 |
| `2` | `import_data`で指定したフォルダ内の **全ファイル** を個別のcsvへ変換（ファイル名は入力されたファイルに`.csv`を付加 |
| `3` | `import_data`で指定したフォルダ内の **全ファイル** を `output_csv` へ変換 |

### `output_format`
| 値 | 動作 |
| --- | --- |
| `1` | 震源データの内容をそのまま付記 |
| `2` | 震源データをある程度解釈できる文字・数値データとして出力 |
| `3` | 震源データを `2` への変換に加え、年月日日時をdatetime型、緯度経度を10進数として出力 |

## 4.変換例
- 固定長フォーマット震源データ<br>
J2023010100080150 012 354059 100 1403927 136 50     03v   721   3110NEAR CHOSHI CITY          9A<br>
- `output_format` = `1`<br>
hypocenter reporting agency,year,month,day,hour,minute,second,second standard error,latitude[degree],latitude[minute],latitude[minute] standard error,longitude[degree],longitude[minute],longitude[minute] standard error,depth[km],depth[km] standard error,magnitude1,magnitude1 type,magnitude2,magnitude2 type,travel time tables,hypocenter evaluation,earthquake cause,maximum seismic intensity,disaster scale,tsunami scale,major regional classification number,minor regional classification number,epicenter region,number of observation points,hypocenter determination Flag<br>
J,2023,01,01,00,08,1.5,0.12,35.0,40.59,1.0,140.0,39.27,1.36,50.0,,0.3,v,,,7,2,1,,,,3,110,NEAR CHOSHI CITY,9,A<br>
- `output_format` = `2`<br>
hypocenter reporting agency,year,month,day,hour,minute,second,second standard error,latitude[degree],latitude[minute],latitude[minute] standard error,longitude[degree],longitude[minute],longitude[minute] standard error,depth[km],depth[km] standard error,magnitude1,magnitude1 type,magnitude2,magnitude2 type,travel time tables,hypocenter evaluation,earthquake cause,maximum seismic intensity,disaster scale,tsunami scale,major regional classification number,minor regional classification number,epicenter region,number of observation points,hypocenter determination Flag<br>
JMA,2023,01,01,00,08,1.5,0.12,35.0,40.59,1.0,140.0,39.27,1.36,50.0,,0.3,JMA_Tuboi velocity_2or3points,,,MA2001A or JMA2020A or JMA2020B or JMA2020C,Optimal solution found using depth-step condition,Natural Earthquakes,,,,3,110,NEAR CHOSHI CITY,9,Automatic JMA Hypocenter<br>
- `output_format` = `3`<br>
hypocenter reporting agency,second standard error,latitude[minute] standard error,longitude[minute] standard error,depth[km],depth[km] standard error,magnitude1,magnitude1 type,magnitude2,magnitude2 type,travel time tables,hypocenter evaluation,earthquake cause,maximum seismic intensity,disaster scale,tsunami scale,major regional classification number,minor regional classification number,epicenter region,number of observation points,hypocenter determination Flag,daytime,latitude,longitude<br>
JMA,0.12,1.0,1.36,50.0,,0.3,JMA_Tuboi velocity_2or3points,,,MA2001A or JMA2020A or JMA2020B or JMA2020C,Optimal solution found using depth-step condition,Natural Earthquakes,,,,3,110,NEAR CHOSHI CITY,9,Automatic JMA Hypocenter,2023-01-01 00:08:01.500000,35.6765,140.6545<br>



## 5.免責事項
本スクリプトについて、作成者は、本ツールの使用によって生じたいかなる損害・不利益・データ損失についても責任を負いません。<br>
自己責任でご利用ください。<br>
スクリプトは作成途中の段階ですので、バグやミスがある可能性があります。<br>
また、**気象庁 震源データ**の利用の際には、気象庁の利用規約を必ずご確認ください。
