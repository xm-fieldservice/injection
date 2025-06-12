# NodeMind 思维导图系统使用指南

**版本：2.0** | **更新日期：2025年01月21日**

---

## 📋 项目概述

NodeMind 是基于 **jsMind** 开源框架开发的思维导图可视化系统，专为知识管理和项目管理而设计。系统采用"万物皆节点"的核心理念，将笔记、任务、项目等各种信息统一为节点进行管理。

### 🎯 核心特性

- **纯前端实现**：基于 HTML5 Canvas 和 JavaScript，无需后端支持
- **可视化管理**：支持节点状态图标、彩色标签、双层显示
- **灵活拖拽**：完整的节点拖拽功能，支持结构重组
- **数据持久化**：本地存储和文件导入导出
- **多主题支持**：15种内置主题，支持实时切换
- **双层节点**：上半部分显示标题+图标，下半部分显示标签文字

---

## 🚀 快速开始

### 1. 文件结构

```
nodemind/
├── jsmind-local.html          # 主程序文件
├── jsmind-demo-visual.html    # 可视化演示（仅样式）
├── jsmind-demo-visual-mindmap.html # 完整脑图+可视化
├── node_modules/              # jsMind依赖库
├── backups/                   # 备份文件目录
├── 拖拽功能使用说明.md         # 拖拽功能详细说明
├── 基于Node脑图需求文档.md     # 项目需求文档
└── README.md                  # 项目介绍
```

### 2. 运行方式

#### 方式一：直接运行（推荐）
```bash
# 直接在浏览器中打开主文件
打开 jsmind-local.html
```

#### 方式二：本地服务器
```bash
# 安装依赖
npm install

# 启动本地服务器
npm start
# 或使用Python简单服务器
python -m http.server 8000
```

#### 方式三：CDN方式
使用在线CDN资源，无需本地安装依赖。

---

## 🎮 功能详解

### 1. 基础操作

#### 鼠标操作
| 操作 | 功能 | 说明 |
|-----|------|------|
| 单击节点 | 选中节点 | 节点高亮显示，详情面板更新 |
| 双击节点 | 编辑节点 | 直接修改节点标题内容 |
| 拖拽节点 | 移动节点 | 重新组织节点层次结构 |
| 拖拽背景 | 移动视图 | 平移整个思维导图 |
| 滚轮 | 缩放视图 | 放大/缩小思维导图 |

#### 快捷键操作
| 按键 | 功能 | 说明 |
|-----|------|------|
| Ctrl+Enter | 添加子节点 | 为选中节点添加子节点 |
| Enter | 添加兄弟节点 | 在同级添加新节点 |
| F2 | 编辑节点 | 编辑选中节点内容 |
| Delete | 删除节点 | 删除选中节点及其子树 |
| Space | 展开/收起 | 切换节点折叠状态 |
| 方向键 | 节点导航 | 选择相邻节点 |
| Ctrl+H | 显示帮助 | 打开帮助信息 |

### 2. 工具栏功能

#### 节点操作区
- **➕ 添加节点**：为选中节点添加子节点
- **✏️ 编辑节点**：修改选中节点内容
- **🗑️ 删除节点**：删除选中节点
- **📂 展开全部**：展开所有折叠节点
- **📁 收起全部**：折叠所有子节点

#### 视图控制区
- **🎨 切换主题**：循环切换15种内置主题
- **🔍 适应窗口**：重置视图到最佳显示状态
- **🔀 拖拽开关**：启用/禁用节点拖拽功能

#### 数据管理区
- **💾 保存脑图**：保存当前脑图为JSON文件
- **📁 加载脑图**：从JSON文件加载脑图
- **📤 导出数据**：查看思维导图JSON数据
- **✨ 新内容**：自动保存当前脑图并创建新的空白脑图

### 3. 节点可视化系统

#### 状态图标
- **📝 有详细内容**：节点包含详细描述信息
- **📎 有附件**：节点关联文件或链接
- **📁 是项目**：标识为项目类节点
- **⏳ 进行中**：任务正在执行
- **🔔 需要跟进**：需要后续关注
- **👀 正在跟进**：当前正在关注
- **⚙️ 工作进行中**：工作状态活跃

#### 双层节点结构
- **上半部分**：节点标题 + 状态图标
- **下半部分**：分类标签（字体较小，12px）
- **分层标识**：使用 `<br>` 标签实现真正的双行显示

#### 标签系统
```javascript
// 标签配置示例
const nodeLabels = {
    categories: ['工作', '学习', '生活'],     // 分类标签
    technical: ['前端', '后端', '设计'],     // 技术标签
    status: ['紧急', '重要', '延期'],        // 状态标签
    custom: ['个人', '团队', '客户']         // 自定义标签
};
```

### 4. 拖拽功能详解

#### 拖拽操作流程
1. **启用拖拽**：点击"🔀 启用拖拽"按钮
2. **选择节点**：将鼠标悬停在要移动的节点上
3. **开始拖拽**：按住鼠标左键开始拖拽
4. **移动到目标**：将节点拖拽到目标节点位置
5. **完成移动**：松开鼠标左键完成操作

#### 拖拽特性
- ✅ **跨分支支持**：支持左右分支间移动
- ✅ **多层嵌套**：支持复杂层级关系调整
- ✅ **实时反馈**：拖拽过程中提供视觉指导
- ✅ **自动布局**：完成后自动重新排列布局
- ❌ **根节点限制**：根节点不能被拖拽或作为拖拽目标的子节点

---

## 🎨 主题系统

### 内置主题列表

| 主题名称 | 色彩风格 | 适用场景 |
|---------|----------|----------|
| primary | 蓝色系 | 通用场景（默认） |
| success | 绿色系 | 项目成功、完成状态 |
| warning | 橙色系 | 警告、注意事项 |
| danger | 红色系 | 错误、紧急任务 |
| info | 青色系 | 信息展示、知识管理 |
| greensea | 海绿色 | 清新、自然主题 |
| nephritis | 翡翠绿 | 优雅、专业主题 |
| belizehole | 深蓝色 | 稳重、商务主题 |
| wisteria | 紫色系 | 创意、设计主题 |
| asphalt | 深灰色 | 简约、现代主题 |
| orange | 橙红色 | 活跃、热情主题 |
| pumpkin | 南瓜色 | 温暖、友好主题 |
| pomegranate | 石榴红 | 热烈、激情主题 |
| clouds | 浅灰色 | 清淡、简洁主题 |
| asbestos | 中灰色 | 中性、平衡主题 |

### 主题切换
- **手动切换**：点击"🎨 切换主题"按钮循环切换
- **状态显示**：状态栏实时显示当前使用的主题名称
- **即时生效**：切换后立即应用到整个思维导图

---

## 📊 数据格式规范

### 1. 基础数据结构

```javascript
// 思维导图整体数据格式
const mindMapData = {
    meta: {
        name: "思维导图名称",
        author: "创建者",
        version: "1.0",
        created: "2025-01-21T10:00:00",
        modified: "2025-01-21T15:30:00"
    },
    format: "node_tree",
    data: {
        id: "root",
        isroot: true,
        topic: "中心节点",
        children: [
            {
                id: "N001",
                topic: "子节点标题<br><small>标签文字</small>",
                direction: "right",
                children: [...],
                expanded: true
            }
        ]
    }
};
```

### 2. 节点数据库结构

```javascript
// 内存中的节点数据库
const nodeDatabase = {
    "N001": {
        id: "N001",
        title: "节点标题",
        content: "详细内容描述",
        relations: {
            parent: null,
            children: ["N002", "N003"]
        },
        tags: {
            categories: ["工作", "重要"],
            technical: ["前端"],
            status: ["进行中"],
            custom: []
        },
        metadata: {
            created: "2025-01-21T10:00:00",
            modified: "2025-01-21T15:30:00",
            author: "用户名"
        },
        visual: {
            icons: ["📝", "⚙️"],
            color: "#ffffff",
            bgColor: "#4a90e2"
        }
    }
};
```

### 3. 标签规范

#### 标签分类
- **categories**：业务分类标签（工作、学习、生活）
- **technical**：技术分类标签（前端、后端、设计）
- **status**：状态分类标签（紧急、重要、完成）
- **custom**：自定义标签（项目特定）

#### 标签层级关系
```javascript
const tagHierarchy = {
    "技术栈": {
        "前端": ["React", "Vue", "Angular"],
        "后端": ["Node.js", "Python", "Java"],
        "数据库": ["MySQL", "MongoDB", "Redis"]
    },
    "项目管理": {
        "状态": ["计划中", "进行中", "已完成"],
        "优先级": ["高", "中", "低"],
        "类型": ["功能", "优化", "修复"]
    }
};
```

---

## ⚙️ 高级配置

### 1. 系统配置选项

```javascript
const systemConfig = {
    // 视图配置
    view: {
        engine: 'canvas',           // 渲染引擎：canvas 或 svg
        hmargin: 100,              // 水平边距
        vmargin: 50,               // 垂直边距
        line_width: 2,             // 连线宽度
        line_color: '#558'         // 连线颜色
    },
    
    // 布局配置
    layout: {
        hspace: 30,                // 节点水平间距
        vspace: 20,                // 节点垂直间距
        pspace: 13                 // 节点与连线间距
    },
    
    // 编辑配置
    editable: true,                // 是否可编辑
    theme: 'primary',              // 默认主题
    
    // 快捷键配置
    shortcut: {
        enable: true,              // 启用快捷键
        handles: {...}             // 快捷键映射
    }
};
```

### 2. 节点可视化配置

```javascript
const visualConfig = {
    // 双层节点配置
    dualLayer: {
        enabled: true,             // 启用双层显示
        separator: '<br>',         // 分层分隔符
        topStyle: {
            fontSize: '14px',
            fontWeight: 'bold'
        },
        bottomStyle: {
            fontSize: '12px',
            color: '#666'
        }
    },
    
    // 图标配置
    icons: {
        hasContent: '📝',
        hasAttachment: '📎',
        isProject: '📁',
        inProgress: '⏳',
        needsFollowup: '🔔',
        watching: '👀',
        working: '⚙️'
    },
    
    // 标签配置
    labels: {
        maxVisible: 3,             // 最多显示标签数
        truncateLength: 8,         // 标签截断长度
        colors: {
            categories: '#007bff',
            technical: '#28a745',
            status: '#ffc107',
            custom: '#6c757d'
        }
    }
};
```

---

## 🔧 开发者指南

### 1. API 方法参考

#### 节点操作API
```javascript
// 获取节点
jm.get_root()                    // 获取根节点
jm.get_node(nodeId)             // 根据ID获取节点
jm.get_selected_node()          // 获取选中节点

// 操作节点
jm.select_node(node)            // 选中节点
jm.expand_node(node)            // 展开节点
jm.collapse_node(node)          // 收起节点
jm.expand_all()                 // 展开全部
jm.collapse_all()               // 收起全部

// 编辑节点
jm.add_node(parent, nodeId, topic)       // 添加节点
jm.insert_node_before(node, id, topic)   // 前插节点
jm.insert_node_after(node, id, topic)    // 后插节点
jm.remove_node(node)                     // 删除节点
jm.update_node(nodeId, topic)            // 更新节点

// 样式设置
jm.set_theme(theme)                      // 设置主题
jm.set_node_color(nodeId, bgcolor, fgcolor)  // 设置颜色
```

#### 数据操作API
```javascript
// 数据获取
jm.get_data(format)             // 获取数据
jm.get_meta()                   // 获取元数据

// 数据导入导出
exportMindMap()                 // 导出JSON数据
loadMindMapFromFile(file)       // 从文件加载
saveMindMapToFile(data)         // 保存到文件
```

### 2. 自定义扩展

#### 添加自定义图标
```javascript
function addCustomIcon(nodeId, iconType) {
    const node = jm.get_node(nodeId);
    if (node) {
        const currentTopic = node.topic;
        const iconMap = {
            'urgent': '🚨',
            'completed': '✅',
            'blocked': '🚫',
            'idea': '💡'
        };
        
        const newTopic = iconMap[iconType] + ' ' + currentTopic;
        jm.update_node(nodeId, newTopic);
    }
}
```

#### 批量操作节点
```javascript
function batchUpdateNodes(nodeIds, operation) {
    nodeIds.forEach(id => {
        const node = jm.get_node(id);
        if (node) {
            switch(operation.type) {
                case 'setColor':
                    jm.set_node_color(id, operation.bgColor, operation.fgColor);
                    break;
                case 'addTag':
                    addTagToNode(id, operation.tag);
                    break;
                case 'updateTopic':
                    jm.update_node(id, operation.newTopic);
                    break;
            }
        }
    });
}
```

---

## 🚨 故障排除

### 常见问题与解决方案

#### 1. 拖拽功能不工作
**问题**：节点无法拖拽或拖拽后没有效果

**解决方案**：
- 检查是否已点击"🔀 启用拖拽"按钮
- 确认浏览器支持HTML5拖拽API
- 刷新页面重新加载脚本

#### 2. 节点双层显示异常
**问题**：节点内容显示为一行或格式错乱

**解决方案**：
```javascript
// 确保节点内容包含<br>标签
const nodeContent = "上半部分内容<br><small>下半部分标签</small>";
jm.update_node(nodeId, nodeContent);
```

#### 3. 主题切换无效
**问题**：点击主题切换按钮后样式没有改变

**解决方案**：
- 检查CSS文件是否正确加载
- 清除浏览器缓存
- 确认主题名称是否正确

#### 4. 数据保存失败
**问题**：导出或保存功能无响应

**解决方案**：
- 检查浏览器是否支持文件下载API
- 确认没有被弹窗拦截器阻止
- 检查数据格式是否正确

### 性能优化建议

#### 1. 大型思维导图优化
```javascript
// 延迟加载大量节点
function loadNodesLazy(parentId, children) {
    const batchSize = 50;
    let index = 0;
    
    function loadBatch() {
        const batch = children.slice(index, index + batchSize);
        batch.forEach(child => {
            jm.add_node(parentId, child.id, child.topic);
        });
        
        index += batchSize;
        if (index < children.length) {
            setTimeout(loadBatch, 100);
        }
    }
    
    loadBatch();
}
```

#### 2. 内存管理
```javascript
// 定期清理未使用的节点数据
function cleanupNodeDatabase() {
    const activeNodes = new Set();
    jm.get_data().forEach(node => {
        activeNodes.add(node.id);
    });
    
    Object.keys(nodeDatabase).forEach(id => {
        if (!activeNodes.has(id)) {
            delete nodeDatabase[id];
        }
    });
}
```

---

## 📱 移动端适配

### 触摸操作支持

| 手势 | 功能 | 说明 |
|-----|------|------|
| 单击 | 选中节点 | 等同于鼠标单击 |
| 双击 | 编辑节点 | 等同于鼠标双击 |
| 长按 | 显示菜单 | 显示操作选项 |
| 拖拽 | 移动节点 | 支持触摸拖拽 |
| 双指缩放 | 缩放视图 | 放大缩小思维导图 |
| 双指拖拽 | 平移视图 | 移动整个视图 |

### 响应式设计
- **小屏适配**：工具栏自动调整布局
- **触摸优化**：按钮尺寸适合触摸操作
- **手势识别**：支持常用触摸手势

---

## 🌐 浏览器兼容性

### 支持的浏览器

| 浏览器 | 最低版本 | 推荐版本 | 备注 |
|--------|----------|----------|------|
| Chrome | 60+ | 最新版 | 推荐使用 |
| Firefox | 55+ | 最新版 | 完整支持 |
| Safari | 12+ | 最新版 | 基本支持 |
| Edge | 79+ | 最新版 | 完整支持 |
| IE | ❌ | - | 不支持 |

### 功能兼容性

| 功能 | Chrome | Firefox | Safari | Edge |
|------|--------|---------|--------|------|
| 基础操作 | ✅ | ✅ | ✅ | ✅ |
| 拖拽功能 | ✅ | ✅ | ⚠️ | ✅ |
| 文件导入导出 | ✅ | ✅ | ⚠️ | ✅ |
| 触摸支持 | ✅ | ✅ | ✅ | ✅ |

注：⚠️ 表示部分支持或需要额外配置

---

## 📞 技术支持

### 获取帮助

1. **查看日志**：按F12打开开发者工具查看控制台信息
2. **检查文件**：确保所有依赖文件路径正确
3. **浏览器测试**：尝试使用不同浏览器测试
4. **版本检查**：确认使用的是最新版本

### 常用调试命令

```javascript
// 在浏览器控制台中执行
console.log(jm.get_data());           // 查看当前数据
console.log(nodeDatabase);            // 查看节点数据库
console.log(jm.get_selected_node());  // 查看选中节点
```

### 问题反馈

如遇到问题，请提供以下信息：
- 浏览器版本和操作系统
- 具体错误信息或现象描述
- 重现问题的操作步骤
- 相关的控制台日志信息

---

## 📈 未来规划

### 短期计划（1-3个月）
- ✅ 完善双层节点显示系统
- ✅ 优化拖拽功能体验
- 🔄 增强标签管理功能
- 🔄 添加节点搜索功能

### 中期计划（3-6个月）
- 📋 数据持久化存储
- 📋 多用户协作支持
- 📋 插件系统架构
- 📋 更多导入导出格式

### 长期规划（6个月以上）
- 📋 AI智能助手集成
- 📋 云端同步功能
- 📋 移动端专用应用
- 📋 企业版功能扩展

---

## 📝 更新日志

### v2.0 (2025-01-21)
- ✅ 新增双层节点显示功能
- ✅ 完善节点可视化系统
- ✅ 优化拖拽操作体验
- ✅ 增加"新内容"一键功能
- ✅ 改进状态栏信息显示

### v1.5 (2025-01-20)
- ✅ 添加节点拖拽功能
- ✅ 新增15种主题支持
- ✅ 优化工具栏界面设计
- ✅ 增强数据导入导出功能

### v1.0 (2025-01-15)
- ✅ 基础思维导图功能
- ✅ 节点增删改查操作
- ✅ 本地数据存储
- ✅ 响应式界面设计

---

**© 2025 NodeMind Project. 基于 jsMind 开源框架开发。**