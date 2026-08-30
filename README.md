# 30min-task-timer

Built with AI / Vibe Coding

## Ubuntuでのセットアップ

Ubuntu 26.04で実行する場合、以下のシステムパッケージが必要です。

```bash
sudo apt update
sudo apt install python3-tk fonts-noto-cjk gir1.2-ayatanaappindicator3-0.1 python3-gi
```

- `python3-tk`: TkinterはUbuntuのpython3に標準で同梱されていないため必須。
- `fonts-noto-cjk`: 日本語表示用フォント（`FONT_FAMILY`はLinuxでは`Noto Sans CJK JP`を使用）。
- `gir1.2-ayatanaappindicator3-0.1` / `python3-gi`: システムトレイアイコン（pystray）の描画に必要。これらが無い場合、トレイアイコンは表示されませんがアプリ本体は起動します。GNOMEではトレイアイコンを表示するために「AppIndicator and KStatusNotifierItem Support」拡張機能の導入も必要です。

Python側の依存関係は通常通りインストールします。

```bash
pip install -r requirements.txt
python3 main.pyw
```

## 画面構成
``` mermaid
flowchart LR
    %% 画面ノード
    TaskSelect[タスク選択画面\ncomming soon]
    TaskManageSelect[タスク管理画面\ncomming soon]
    RequestManage[改修要望管理画面\ncomming soon]
    RequestEdit[要望編集画面\ncomming soon]
    RequestNew[新規要望画面\ncomming soon]
    Count30[30分カウント]
    Count5[5分カウント]

    %% タスク選択画面まわり
    TaskSelect -->|タスクを選択| Count30
    TaskSelect -->|"5分後に再通知"ボタン| Count5
    TaskSelect -->|"タスク管理"ボタン| TaskManageSelect
    TaskSelect -->|"要望"ボタン| RequestManage

    %% タスク管理画面
    TaskManageSelect -->|戻る| TaskSelect

    %% 改修要望管理画面
    RequestManage -->|"要望"ボタン| RequestEdit
    RequestManage -->|"新規追加"ボタン| RequestNew
    RequestManage -->|戻る| TaskSelect

    %% 要望編集画面
    RequestEdit -->|戻る| RequestManage

    %% 新規要望画面
    RequestNew -->|戻る| RequestManage

    %% カウント終了後にタスク選択へ戻る想定
    Count30 --> TaskSelect
    Count5 --> TaskSelect
```
