# 30min-task-timer

Built with AI / Vibe Coding

## ディレクトリ構成

30MIN-TASK-TIMER/
│
├── README.md              # プロジェクトの説明書
├── requirements.txt       # 依存ライブラリのリスト
├── .gitignore             # git管理外ファイルのリスト
├── main.pyw               # アプリケーションの起動エントリーポイント
│
├── app/                   # アプリケーションのメインソースコード
│   ├── __init__.py        # 空ファイルのままにしておくか、インポートを綺麗にまとめるためだけに使う
│   ├── config.py          # 定数、カラーコード、フォントなどの設定
│   │
│   ├── models/            # データの処理、ビジネスロジック（Model）
│   │   ├── __init__.py
│   │   ├── timer.py                    
│   │   ├── task_manager.py                    
│   │   └── improvement_request_manager.py
│   │
│   ├── views/             # 画面の見た目、レイアウト（View）
│   │   ├── __init__.py
│   │   ├── task_select_window.py             # タスク選択画面
│   │   ├── task_confirm_dialogs.py           # タスク選択確認ダイアログ
│   │   ├── task_manager_window.py            # タスク管理画面
│   │   └── improvement_request_window.py     # 改善要望画面
│   │
│   └── controllers/       # ViewとModelを繋ぐ制御（Controller）ボタン制御等
│       ├── __init__.py
│       ├── app_controller.py                     # 画面切り替え用コントローラー
│       ├── task_select_controller.py             # タスク選択コントローラー
│       ├── task_manager_controller.py            # タスク管理コントローラー
│       ├── improvement_request_controller.py     # 改善要望コントローラー
│       └── dialog_controller.py                  # ダイアログ制御
│
├── assets/                # 静的リソース
│   ├── icons/             # アイコン画像（.ico, .png）
│   └── images/            # 背景画像やロゴ
│
└── tests/                 # テストコード
    ├── __init__.py
    └── test_models.py