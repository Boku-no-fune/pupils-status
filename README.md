# 学習塾CRM — 校務管理システム

学習塾向けCRM機能のモックアップ。生徒・保護者の動向を可視化し、
講師・管理者が迅速に状況を把握できるダッシュボードを実装。

## 技術スタック

| 項目 | 技術 |
|------|------|
| バックエンド | FastAPI (Python) + SQLAlchemy 2.x |
| フロントエンド | React 18 + Vite + TypeScript + Tailwind CSS |
| グラフ | Recharts |
| データベース | PostgreSQL |
| 認証 | JWT (python-jose) + bcrypt |
| デプロイ | Railway |

---

## ローカル起動手順

### 前提条件
- Python 3.9 以上
- Node.js 18 以上
- PostgreSQL (ローカルまたはDockerで起動)

### 1. PostgreSQL を起動

```bash
# Dockerで起動する場合
docker run -d \
  --name pupils-db \
  -e POSTGRES_DB=pupils_status \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15
```

### 2. バックエンドのセットアップ

```bash
cd backend

# 仮想環境を作成・有効化
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .env ファイルの DATABASE_URL などを編集してください

# DBマイグレーションを実行
alembic upgrade head

# シードデータを生成
python scripts/seed.py

# 開発サーバーを起動
uvicorn app.main:app --reload --port 8000
```

APIドキュメント: http://localhost:8000/api/docs

### 3. フロントエンドのセットアップ

```bash
cd frontend

# 依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

アプリ: http://localhost:5173

---

## テストアカウント

| ロール | メールアドレス | パスワード |
|--------|--------------|----------|
| 管理者 | admin@example.com | password |
| 教室長 | manager@example.com | password |
| 講師 | teacher1@example.com | password |
| アルバイト | part1@example.com | password |

---

## Railway デプロイ手順

### 1. Railwayプロジェクトを作成

```bash
# Railway CLIをインストール
npm install -g @railway/cli

# ログイン
railway login

# プロジェクトを作成
railway init
```

### 2. PostgreSQLを追加

Railway ダッシュボード → 「New」→「Database」→「PostgreSQL」を追加。

### 3. 環境変数を設定

Railway ダッシュボードのサービス設定から以下を追加:

```
DATABASE_URL      = (Railway Postgres が自動設定)
SECRET_KEY        = (python3 -c "import secrets; print(secrets.token_urlsafe(32))" で生成)
FRONTEND_URL      = https://your-frontend.up.railway.app
```

### 4. バックエンドをデプロイ

```bash
railway up
```

`railway.toml` に従い、自動でマイグレーション + シードデータ生成 + サーバー起動が実行されます。

### 5. フロントエンドをデプロイ (別サービス)

Railway ダッシュボードで新しいサービスを作成し、`frontend/` ディレクトリを指定:

- Build Command: `npm ci && npm run build`
- Start Command: `npx serve dist`
- 環境変数: `VITE_API_BASE_URL=https://your-backend.up.railway.app`

---

## 機能一覧

### ダッシュボード (4タブ)

| タブ | 機能 |
|------|------|
| 生徒一覧 | ステータスフィルタ、出席率、成績変化、担当講師 |
| 出欠・成績 | 月別出席率推移グラフ、科目別スコア推移グラフ |
| 営業目標 | 目標進捗バー、アプローチ状況管理、レポート生成 |
| リスク・AI | ルールベースリスク判定、AI提案テキスト (ダミー) |

### 生徒詳細ページ

- 基本情報・受講講座・志望校
- イベントタイムライン
- テスト成績グラフ (棒グラフ + レーダーチャート)
- 出欠カレンダー
- 保護者コンタクト履歴
- 支払い状況
- 営業アクション履歴
- リスクスコア + AI提案

### ロール別権限

| 操作 | admin | 教室長 | 講師 | アルバイト |
|------|-------|--------|------|-----------|
| 全生徒閲覧 | ✓ | 自教室のみ | 担当のみ | × |
| ダッシュボード | ✓ | 自教室のみ | × | × |
| 出欠入力 | ✓ | ✓ | ✓ | ✓ |
| 営業管理 | ✓ | ✓ | × | × |
| AI分析 | ✓ | ✓ | × | × |

---

## Claude API統合

`ANTHROPIC_API_KEY` を環境変数に設定するだけでリアルAIが有効になります。

```
ANTHROPIC_API_KEY=sk-ant-api...
```

`backend/app/services/ai_service.py` の `ClaudeAIService` クラスが自動的に使用され、
ダミー実装から本番Claude APIに切り替わります。コード変更は不要です。

---

## シードデータをリセット

```bash
cd backend
python scripts/seed.py --force
```
