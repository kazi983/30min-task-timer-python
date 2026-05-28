# 30min-task-timer

Built with AI / Vibe Coding

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
