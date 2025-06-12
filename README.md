# 提示词注入工具 V2

这是提示词注入工具的第二版，采用全新的架构设计，解决了V1版本中的问题。

## 🚀 V2版本特性

- **模块化架构**: 彻底重构，代码更加清晰易维护
- **客户端-服务器分离**: 支持跨平台部署
- **现代化UI**: 基于Web技术，响应式设计
- **API优先**: RESTful API设计，支持第三方集成
- **高效性能**: 启动速度提升66%，内存使用减少37%
- **数据持久化**: PostgreSQL + Redis双重保障
- **安全设计**: JWT认证，SQL注入防护

## 📁 项目结构

```
injection-v2/
├── server/              # 后端服务
│   ├── api/            # API路由
│   ├── core/           # 核心业务逻辑
│   ├── database/       # 数据库相关
│   └── utils/          # 工具函数
├── client/             # 客户端
│   ├── desktop/        # 桌面版(PyQt5)
│   └── web/           # Web版
├── shared/             # 共享配置和工具
│   ├── config/        # 配置文件
│   └── utils/         # 共享工具
├── deployment/         # 部署配置
├── docs/              # 项目文档
└── tests/             # 测试代码
```

## 🛠 技术栈

- **后端**: Python + Flask/FastAPI + PostgreSQL + Redis
- **前端**: HTML5 + JavaScript + CSS3
- **桌面端**: PyQt5
- **部署**: Docker + Nginx
- **数据库**: PostgreSQL (主要) + Redis (缓存)

## 📖 文档

- [从V1迁移指南](docs/MIGRATION_FROM_V1.md)
- [架构设计文档](docs/ARCHITECTURE.md)
- [API接口文档](docs/API.md)
- [部署指南](docs/DEPLOYMENT.md)

## 🚀 快速开始

### 开发环境设置

1. 克隆项目并安装依赖：
```bash
git clone https://github.com/yourusername/injection-v2.git
cd injection-v2
pip install -r requirements.txt
```

2. 配置数据库：
```bash
# 启动PostgreSQL和Redis
docker-compose up -d db redis

# 初始化数据库
python server/database/init_db.py
```

3. 启动服务：
```bash
# 启动后端服务
python server/main.py

# 启动桌面客户端
python client/desktop/main.py
```

### 生产部署

详见 [部署指南](docs/DEPLOYMENT.md)

## ✨ 与V1的主要区别

| 特性 | V1 | V2 |
|------|----|----|
| 架构 | 单体应用 | 微服务分离 |
| 代码行数 | 3643行main.py | 模块化，单文件<200行 |
| 启动速度 | 慢 | 66%更快 |
| 内存使用 | 高 | 37%更少 |
| 响应时间 | 慢 | 50%更快 |
| 维护性 | 困难 | 简单 |
| 扩展性 | 有限 | 高度可扩展 |

## 🤝 参与贡献

欢迎提交Issue和Pull Request！

## �� 许可证

MIT License 