# AI_finance_news

一个自动抓取并总结每日金融新闻的前后端一体化示例应用。

## 功能
- 自动抓取多家金融媒体 RSS，汇总最新新闻
- 基于关键词权重的轻量级摘要生成
- 前端仪表盘展示今日新闻亮点与列表

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

打开浏览器访问 `http://127.0.0.1:8000/app` 查看页面。

## API 示例

- `GET /api/news?limit=20`
- `GET /api/digest?limit=10`
