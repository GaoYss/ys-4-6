# 小区物业费收缴系统

Django + Vue 实现的小区物业费收缴系统，覆盖楼栋管理、费用标准、账单生成、在线缴费、欠费催缴、票据打印等核心流程。

## 功能模块

- 楼栋管理：维护楼栋、房屋、业主、电话、面积等基础档案。
- 费用生成：配置固定金额或按面积计费的费用标准，按账期批量生成账单。
- 在线缴费：对待缴/逾期账单进行模拟缴费，生成支付流水和票据编号。
- 欠费催缴：识别逾期/待缴账单，生成短信、电话、微信或纸质通知催缴记录。
- 票据打印：查看缴费票据并调用浏览器打印。
- 工作台：统计应收、实收、欠费、楼栋房屋和近期账单。

## 项目结构

```text
backend/
  property_fee/       Django 项目配置
  communities/        物业收费业务 app
    models.py         楼栋、房屋、费用、账单、缴费、催缴模型
    serializers.py    API 序列化
    services.py       账单生成、缴费、催缴等业务服务
    views.py          REST API 视图
frontend/
  src/
    api/              前端接口封装
    components/       通用表格、状态、统计组件
    router/           Vue Router
    views/            工作台和各业务页面
docker-compose.yml    一键启动配置
```

## Docker 启动

```bash
docker compose up --build
```

启动后访问：

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000/api/
- Django Admin：http://localhost:8000/admin/

容器启动时会自动执行迁移并写入演示数据。SQLite 数据保存在 Docker volume `backend_data` 中。

## 本地开发

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 常用 API

- `GET /api/dashboard/` 工作台统计
- `GET/POST /api/buildings/` 楼栋
- `GET/POST /api/rooms/` 房屋
- `GET/POST /api/fee-types/` 费用标准
- `POST /api/bills/generate/` 批量生成账单
- `POST /api/bills/{id}/pay/` 缴费
- `POST /api/reminders/create_overdue/` 生成逾期催缴
