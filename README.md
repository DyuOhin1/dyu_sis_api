# OHIN1-API 設計總表

## 1. API 設計原則

- **API 風格**: RESTful

- **URL 結構**: No-Params 格式

- **身份驗證**: JWT，包含學生學號、icloud 及 sis 的 Connection 物件

  : 

  ```json
  {
    "s_id": "f1000000",
    "sis" : {
        "session_id" : "...",
        "login_timestamp" : "..."
    },
    "ic" : {
        "session_id" : "...",
        "login_timestamp" : "..."
    }
  }
  ```

- **回應格式**: 統一標準化

- **Middleware 依賴**: Dyu SIS LIB，已封裝為 FastAPI 依賴

## 2. FastAPI 相關設計

- **FastAPI 背景任務**: 用於自動快取資料、記錄 API 日誌
- **Pydantic 模型**: 確保 API 回傳格式一致，並進行型別驗證

## 3. MongoDB 快取策略

- **快取資料庫**: MongoDB

- **快取範圍**: 請假資訊不快取，其他所有資訊快取

- **快取有效期**: 3 天

- **快取檢查方式**: 手動檢查 `cache_timestamp` 是否過期

- 快取更新條件

  :

  1. 若數據未過期，直接回傳快取
  2. 若超過 3 天，重新抓取並更新快取
  3. 若 `refresh=true`，強制重新抓取

- 快取 Schema 設計

  :

  每個 Collection 應長這樣儲存，每個 Collection id 放學生學號，並記錄首次創建時間，以及最後更新時間，若第一次創建，則更新時間設為 null，cache_duration 為此筆資料的更新間隔，程式比較 updated_timestamp 與當前時間比較若大於 cache_duration 則更新於 data 欄位的詳細資訊。

  ```json
  {
      "_id": "student_id",
      "created_timestamp": 1700000000, 
      "updated_timestamp" : 1700000001,
      "cache_duration" : 86400,
      "data" : {
          ...
      }
  }
  ```

- 快取查詢流程

  :

  1. 查詢 MongoDB 是否有該 `student_id` 快取
  2. 檢查 `cache_timestamp`
  3. 若有效，直接回傳
  4. 若過期或 `refresh=true`，重新抓取並更新快取

- **強制刷新機制**: 透過 `?refresh=true` 參數來強制更新快取

## 4. 安全性策略

- Session 劫持防範

  :

  - 使用 HttpOnly Cookie 儲存 JWT
  - 檢查 IP 變動，自動重新登入

- 重放攻擊防禦

  :

  - JWT 內含 `iat` 時間戳，設定過期時間為一小時
  - 加入 Nonce（唯一請求識別碼）

- **API Rate Limiting**: 防止濫用，限制單個用戶請求頻率

- **CSRF 保護**: 目前不需要，除非 JWT 存在 Cookie 內

## 5. FastAPI Router 設計

### 專案目錄

```bash
/A-API
│── app.py                      # FastAPI 主應用入口
│── config.py                     # 配置檔案 (JWT 設定、MongoDB 連線)
│── models/                       # Pydantic 資料模型
│   │── auth.py                    # 身份驗證相關模型
│   │── student.py                 # 學生基本資訊模型
│   │── leave.py                   # 請假模型
│   │── graduation.py               # 畢業資訊模型
│── routes/                       # FastAPI 路由 (API 定義)
│   │── auth.py                    # 登入/登出
│   │── student.py                 # 學生資訊 API
│   │── leave.py                   # 請假 API
│   │── graduation.py               # 畢業 API
│── services/                     # 服務層 (封裝業務邏輯)
│   │── auth_service.py             # 身份驗證服務
│   │── student_service.py          # 學生資訊服務
│   │── leave_service.py            # 請假處理服務
│   │── graduation_service.py       # 畢業相關業務
│── utils/                        # 工具函式 (快取、身份驗證等)
│   │── cache.py                    # MongoDB 快取管理
│   │── auth.py                     # JWT 驗證
│   │── nonce.py                    # Nonce 防重放機制
│── database.py                    # MongoDB 連線設定
│── requirements.txt               # 依賴安裝
│── README.md                      # API 文件
```

### 認證與登入

- `POST /login` - 登入
  - 登入系統，登入成功配發 jwt token
- `POST /logout` - 登出
  - 登出系統，登出成功使 jwt token 失效

### 畢業資訊

- `GET /graduation/workplace-exp`
- `GET /graduation/english`
- `GET /graduation/chinese`
- `GET /graduation/computer`
- `GET /graduation/pdf`
- `GET /graduation`

### 個人資訊

- `GET /personal/course`

- `GET /personal/course/pdf`
- `GET /personal/course/warning`
- `GET /personal/barcode`
- `GET /personal/image`
- `GET /personal/injury`
- `GET /personal/privacy`
- `GET /personal/military`
- `GET /personal/advisors`
- `GET /personal/rewards-and-penalties`
- `GET /personal/enrollment/pdf`
- `GET /personal/enrollment`
- `GET /personal/scholarship`
- `GET /personal/printer-point`
- `GET /personal/dorm`

### 請假管理

+ `GET /leave/courses`

+ `POST /leave`

+ `GET /leave/{leave_id}`

+ `DELETE /leave/{leave_id}`

+ `POST /leave/document`

+ `GET /leave`