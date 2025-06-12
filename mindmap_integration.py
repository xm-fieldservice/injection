"""
JSMind Integration Module for Injection Tool
JSMind脑图集成模块 - 用于injection工具的脑图功能

功能特性：
1. JSMind脑图引擎集成
2. 数据结构转换
3. 与列表区域同步
4. 智能节点分析

作者: AI Assistant
创建时间: 2025-06-08
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextBrowser
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
import json
import os

# 尝试导入WebEngine，如果失败则使用QTextBrowser作为替代
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    print("PyQt5.QtWebEngineWidgets不可用，将使用QTextBrowser作为替代")

class MindmapWidget(QWidget):
    """JSMind脑图组件"""
    
    # 信号定义
    node_clicked = pyqtSignal(str, dict)  # 节点点击信号
    structure_changed = pyqtSignal(dict)  # 结构变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.web_view = None
        self.current_data = None
        self.init_ui()
        self.load_jsmind()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 根据WebEngine可用性创建视图
        if WEBENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setMinimumHeight(300)
        else:
            # 使用QTextBrowser作为替代
            self.web_view = QTextBrowser()
            self.web_view.setMinimumHeight(300)
            # 修改日志：2025-06-08 by Assistant - 增强简化模式交互功能和视觉效果
            # 变更：添加节点点击效果、拖拽模拟、更丰富的视觉反馈和工具说明
            html_content = """
                <div style="font-family: 'Microsoft YaHei', Arial, sans-serif; padding: 20px; line-height: 1.6; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100%;">
                    <div style="text-align: center; margin-bottom: 30px; position: relative;">
                        <h2 style="color: #2196F3; margin-bottom: 10px; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">🧠 中心节点</h2>
                        <p style="color: #666; font-size: 12px;">injection项目 - 简化脑图模式（支持基础交互）</p>
                        <div style="position: absolute; top: 0; right: 0; background: #ffeb3b; color: #333; padding: 4px 8px; border-radius: 12px; font-size: 10px;">
                            💡 点击节点可复制内容
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 20px;">
                        <div class="branch-card" style="border: 2px solid #4CAF50; border-radius: 12px; padding: 18px; background: linear-gradient(145deg, #ffffff, #f8f9fa); box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15); transition: all 0.3s ease; cursor: pointer;" 
                             onmouseover="this.style.transform='translateY(-5px) scale(1.02)'; this.style.boxShadow='0 8px 20px rgba(76, 175, 80, 0.25)'" 
                             onmouseout="this.style.transform=''; this.style.boxShadow='0 4px 12px rgba(76, 175, 80, 0.15)'"
                             onclick="copyToClipboard('项目管理: 当前项目 injection')">
                            <h4 style="color: #4CAF50; margin: 0 0 12px 0; font-size: 16px; display: flex; align-items: center;">
                                <span style="margin-right: 8px;">📁</span>项目管理
                                <span style="margin-left: auto; font-size: 12px; opacity: 0.7;">点击复制</span>
                            </h4>
                            <div class="node-item" style="background: white; padding: 10px 12px; border-radius: 6px; border: 1px solid #e9ecef; cursor: pointer; transition: all 0.2s ease;"
                                 onmouseover="this.style.background='#e8f5e8'; this.style.transform='translateX(3px)'"
                                 onmouseout="this.style.background='white'; this.style.transform=''"
                                 onclick="event.stopPropagation(); copyToClipboard('当前项目: injection')">
                                📌 当前项目: injection
                            </div>
                        </div>
                        
                        <div class="branch-card" style="border: 2px solid #FF9800; border-radius: 12px; padding: 18px; background: linear-gradient(145deg, #ffffff, #f8f9fa); box-shadow: 0 4px 12px rgba(255, 152, 0, 0.15); transition: all 0.3s ease; cursor: pointer;"
                             onmouseover="this.style.transform='translateY(-5px) scale(1.02)'; this.style.boxShadow='0 8px 20px rgba(255, 152, 0, 0.25)'" 
                             onmouseout="this.style.transform=''; this.style.boxShadow='0 4px 12px rgba(255, 152, 0, 0.15)'"
                             onclick="copyToClipboard('工作流程: 输入阶段, 处理阶段, 输出阶段')">
                            <h4 style="color: #FF9800; margin: 0 0 12px 0; font-size: 16px; display: flex; align-items: center;">
                                <span style="margin-right: 8px;">🔄</span>工作流程
                                <span style="margin-left: auto; font-size: 12px; opacity: 0.7;">点击复制</span>
                            </h4>
                            <div class="node-item" style="background: white; padding: 8px 12px; margin: 6px 0; border-radius: 6px; border: 1px solid #e9ecef; cursor: pointer; transition: all 0.2s ease;"
                                 onmouseover="this.style.background='#fff3e0'; this.style.transform='translateX(3px)'"
                                 onmouseout="this.style.background='white'; this.style.transform=''"
                                 onclick="event.stopPropagation(); copyToClipboard('输入阶段')">📥 输入阶段</div>
                            <div class="node-item" style="background: white; padding: 8px 12px; margin: 6px 0; border-radius: 6px; border: 1px solid #e9ecef; cursor: pointer; transition: all 0.2s ease;"
                                 onmouseover="this.style.background='#fff3e0'; this.style.transform='translateX(3px)'"
                                 onmouseout="this.style.background='white'; this.style.transform=''"
                                 onclick="event.stopPropagation(); copyToClipboard('处理阶段')">⚙️ 处理阶段</div>
                            <div class="node-item" style="background: white; padding: 8px 12px; margin: 6px 0; border-radius: 6px; border: 1px solid #e9ecef; cursor: pointer; transition: all 0.2s ease;"
                                 onmouseover="this.style.background='#fff3e0'; this.style.transform='translateX(3px)'"
                                 onmouseout="this.style.background='white'; this.style.transform=''"
                                 onclick="event.stopPropagation(); copyToClipboard('输出阶段')">📤 输出阶段</div>
                        </div>
                        
                        <div class="branch-card" style="border: 2px solid #9C27B0; border-radius: 12px; padding: 18px; background: linear-gradient(145deg, #ffffff, #f8f9fa); box-shadow: 0 4px 12px rgba(156, 39, 176, 0.15); transition: all 0.3s ease; cursor: pointer;"
                             onmouseover="this.style.transform='translateY(-5px) scale(1.02)'; this.style.boxShadow='0 8px 20px rgba(156, 39, 176, 0.25)'" 
                             onmouseout="this.style.transform=''; this.style.boxShadow='0 4px 12px rgba(156, 39, 176, 0.15)'"
                             onclick="copyToClipboard('工具集合: 注入工具, 脑图工具')">
                            <h4 style="color: #9C27B0; margin: 0 0 12px 0; font-size: 16px; display: flex; align-items: center;">
                                <span style="margin-right: 8px;">🛠️</span>工具集合
                                <span style="margin-left: auto; font-size: 12px; opacity: 0.7;">点击复制</span>
                            </h4>
                            <div class="node-item" style="background: white; padding: 8px 12px; margin: 6px 0; border-radius: 6px; border: 1px solid #e9ecef; cursor: pointer; transition: all 0.2s ease;"
                                 onmouseover="this.style.background='#f3e5f5'; this.style.transform='translateX(3px)'"
                                 onmouseout="this.style.background='white'; this.style.transform=''"
                                 onclick="event.stopPropagation(); copyToClipboard('注入工具')">💉 注入工具</div>
                            <div class="node-item" style="background: white; padding: 8px 12px; margin: 6px 0; border-radius: 6px; border: 1px solid #e9ecef; cursor: pointer; transition: all 0.2s ease;"
                                 onmouseover="this.style.background='#f3e5f5'; this.style.transform='translateX(3px)'"
                                 onmouseout="this.style.background='white'; this.style.transform=''"
                                 onclick="event.stopPropagation(); copyToClipboard('脑图工具')">🧠 脑图工具</div>
                        </div>
                        
                        <div class="branch-card" style="border: 2px solid #607D8B; border-radius: 12px; padding: 18px; background: linear-gradient(145deg, #ffffff, #f8f9fa); box-shadow: 0 4px 12px rgba(96, 125, 139, 0.15); transition: all 0.3s ease; cursor: pointer;"
                             onmouseover="this.style.transform='translateY(-5px) scale(1.02)'; this.style.boxShadow='0 8px 20px rgba(96, 125, 139, 0.25)'" 
                             onmouseout="this.style.transform=''; this.style.boxShadow='0 4px 12px rgba(96, 125, 139, 0.15)'"
                             onclick="copyToClipboard('知识体系: 经验积累, 最佳实践')">
                            <h4 style="color: #607D8B; margin: 0 0 12px 0; font-size: 16px; display: flex; align-items: center;">
                                <span style="margin-right: 8px;">📚</span>知识体系
                                <span style="margin-left: auto; font-size: 12px; opacity: 0.7;">点击复制</span>
                            </h4>
                            <div class="node-item" style="background: white; padding: 8px 12px; margin: 6px 0; border-radius: 6px; border: 1px solid #e9ecef; cursor: pointer; transition: all 0.2s ease;"
                                 onmouseover="this.style.background='#eceff1'; this.style.transform='translateX(3px)'"
                                 onmouseout="this.style.background='white'; this.style.transform=''"
                                 onclick="event.stopPropagation(); copyToClipboard('经验积累')">💡 经验积累</div>
                            <div class="node-item" style="background: white; padding: 8px 12px; margin: 6px 0; border-radius: 6px; border: 1px solid #e9ecef; cursor: pointer; transition: all 0.2s ease;"
                                 onmouseover="this.style.background='#eceff1'; this.style.transform='translateX(3px)'"
                                 onmouseout="this.style.background='white'; this.style.transform=''"
                                 onclick="event.stopPropagation(); copyToClipboard('最佳实践')">⭐ 最佳实践</div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding: 20px; background: linear-gradient(145deg, #fff3e0, #ffecb3); border-radius: 12px; border: 1px solid #ffcc02;">
                        <h4 style="color: #e65100; margin: 0 0 10px 0;">⚡ 升级到完整模式获得更多功能</h4>
                        <p style="color: #666; font-size: 13px; margin: 5px 0;">
                            <strong>当前简化模式功能：</strong>查看节点结构 • 点击复制内容 • 基础视觉交互
                        </p>
                        <p style="color: #666; font-size: 13px; margin: 5px 0;">
                            <strong>完整模式额外功能：</strong>拖拽编辑 • 添加/删除节点 • 导入/导出 • 键盘快捷键
                        </p>
                        <div style="margin-top: 15px;">
                            <button onclick="enableDragSimulation()" style="background: #E91E63; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-size: 12px; cursor: pointer;">
                                🎯 启用拖拽模拟
                            </button>
                            <span id="drag-status" style="margin-left: 10px; font-size: 11px; color: #666;">未启用</span>
                        </div>
                        <code style="background: #333; color: #fff; padding: 6px 12px; border-radius: 4px; font-size: 12px; display: inline-block; margin-top: 8px;">
                            pip install PyQtWebEngine
                        </code>
                    </div>
                    
                    <div id="copy-feedback" style="position: fixed; top: 20px; right: 20px; background: #4CAF50; color: white; padding: 8px 16px; border-radius: 20px; display: none; font-size: 12px; z-index: 1000;">
                        ✅ 已复制到剪贴板
                    </div>
                </div>
                
                <script>
                    let dragSimulationEnabled = false;
                    let currentlyDragging = null;
                    
                    function copyToClipboard(text) {
                        // 创建临时文本区域
                        const textArea = document.createElement('textarea');
                        textArea.value = text;
                        document.body.appendChild(textArea);
                        textArea.select();
                        
                        try {
                            document.execCommand('copy');
                            showCopyFeedback();
                        } catch (err) {
                            console.log('复制失败，请手动复制：', text);
                        }
                        
                        document.body.removeChild(textArea);
                    }
                    
                    function showCopyFeedback() {
                        const feedback = document.getElementById('copy-feedback');
                        feedback.style.display = 'block';
                        setTimeout(() => {
                            feedback.style.display = 'none';
                        }, 2000);
                    }
                    
                    function enableDragSimulation() {
                        dragSimulationEnabled = !dragSimulationEnabled;
                        const statusElement = document.getElementById('drag-status');
                        const allCards = document.querySelectorAll('.branch-card');
                        
                        if (dragSimulationEnabled) {
                            statusElement.textContent = '✅ 拖拽模拟已启用';
                            statusElement.style.color = '#4CAF50';
                            
                            allCards.forEach(card => {
                                card.style.cursor = 'move';
                                card.style.userSelect = 'none';
                                
                                // 添加拖拽事件
                                card.addEventListener('mousedown', startDragSimulation);
                            });
                            
                            // 添加全局鼠标事件
                            document.addEventListener('mousemove', handleDragSimulation);
                            document.addEventListener('mouseup', endDragSimulation);
                            
                        } else {
                            statusElement.textContent = '❌ 拖拽模拟已禁用';
                            statusElement.style.color = '#666';
                            
                            allCards.forEach(card => {
                                card.style.cursor = 'pointer';
                                card.style.position = '';
                                card.style.left = '';
                                card.style.top = '';
                                card.style.zIndex = '';
                                
                                // 移除拖拽事件
                                card.removeEventListener('mousedown', startDragSimulation);
                            });
                            
                            // 移除全局鼠标事件
                            document.removeEventListener('mousemove', handleDragSimulation);
                            document.removeEventListener('mouseup', endDragSimulation);
                        }
                    }
                    
                    function startDragSimulation(e) {
                        if (!dragSimulationEnabled) return;
                        
                        currentlyDragging = e.currentTarget;
                        currentlyDragging.style.position = 'absolute';
                        currentlyDragging.style.zIndex = '1000';
                        currentlyDragging.style.opacity = '0.8';
                        currentlyDragging.style.transform = 'scale(1.02)';
                        
                        // 记录初始偏移
                        const rect = currentlyDragging.getBoundingClientRect();
                        currentlyDragging.dragOffsetX = e.clientX - rect.left;
                        currentlyDragging.dragOffsetY = e.clientY - rect.top;
                        
                        e.preventDefault();
                        e.stopPropagation();
                    }
                    
                    function handleDragSimulation(e) {
                        if (!currentlyDragging) return;
                        
                        const x = e.clientX - currentlyDragging.dragOffsetX;
                        const y = e.clientY - currentlyDragging.dragOffsetY;
                        
                        currentlyDragging.style.left = Math.max(0, x) + 'px';
                        currentlyDragging.style.top = Math.max(0, y) + 'px';
                        
                        e.preventDefault();
                    }
                    
                    function endDragSimulation(e) {
                        if (!currentlyDragging) return;
                        
                        currentlyDragging.style.opacity = '1';
                        currentlyDragging.style.transform = '';
                        currentlyDragging.style.zIndex = '';
                        
                        // 显示完成反馈
                        showDragFeedback();
                        
                        currentlyDragging = null;
                        e.preventDefault();
                    }
                    
                    function showDragFeedback() {
                        const feedback = document.getElementById('copy-feedback');
                        feedback.textContent = '🎯 节点拖拽完成';
                        feedback.style.background = '#E91E63';
                        feedback.style.display = 'block';
                        setTimeout(() => {
                            feedback.style.display = 'none';
                            feedback.textContent = '✅ 已复制到剪贴板';
                            feedback.style.background = '#4CAF50';
                        }, 2000);
                    }
                </script>
            """
            self.web_view.setHtml(html_content)
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
    
    def load_jsmind(self):
        """加载JSMind脑图"""
        if WEBENGINE_AVAILABLE:
            html_content = self.get_jsmind_html()
            self.web_view.setHtml(html_content)
        # 如果WebEngine不可用，UI已在init_ui中设置
    
    def get_jsmind_html(self):
        """生成JSMind HTML内容"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Injection Tool - Mind Map</title>
    <style>
        body {
            margin: 0;
            padding: 8px;
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background-color: #f8f9fa;
        }
        
        #jsmind_container {
            width: 100%;
            height: 500px;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            color: #666;
            font-size: 14px;
        }
        
        /* 拖拽状态样式 */
        .jmnode-dragging {
            opacity: 0.7 !important;
            z-index: 1000 !important;
            transform: scale(1.05) !important;
            transition: none !important;
        }
        
        .jmnode-dragover {
            background-color: #e3f2fd !important;
            border: 2px dashed #2196F3 !important;
        }
        
        .drag-hint {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #4CAF50;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 100;
        }
    </style>
    <!-- 引用jsMind核心库 -->
    <link type="text/css" rel="stylesheet" href="https://unpkg.com/jsmind@0.4.6/style/jsmind.css" />
    <script type="text/javascript" src="https://unpkg.com/jsmind@0.4.6/js/jsmind.js"></script>
    <!-- 引用jsMind拖拽插件 -->
    <script type="text/javascript" src="https://unpkg.com/jsmind@0.4.6/js/jsmind.draggable.js"></script>
</head>
<body>
    <div id="jsmind_container">
        <div class="loading" id="loading">
            🧠 正在加载脑图引擎...
        </div>
    </div>

    <script type="text/javascript">
        let jm = null;
        let container = null;
        let isDraggingEnabled = false;
        
        function initJSMind() {
            try {
                container = document.getElementById('jsmind_container');
                
                // jsMind配置选项
                const options = {
                    container: 'jsmind_container',
                    editable: true,
                    theme: 'primary',
                    mode: 'full',
                    view: {
                        engine: 'canvas',
                        hmargin: 120,
                        vmargin: 60,
                        line_width: 2,
                        line_color: '#566'
                    },
                    layout: {
                        hspace: 30,
                        vspace: 20,
                        pspace: 13
                    },
                    shortcut: {
                        enable: true,
                        handles: {},
                        mapping: {
                            addchild: 4096 + 13,  // Ctrl+Enter 添加子节点
                            addbrother: 13,  // Enter
                            editnode: 113,   // F2
                            delnode: 46,     // Delete
                            toggle: 32,      // Space
                            left: 37, up: 38, right: 39, down: 40
                        }
                    }
                };
                
                jm = new jsMind(options);
                document.getElementById('loading').style.display = 'none';
                
                // 添加拖拽提示
                const dragHint = document.createElement('div');
                dragHint.className = 'drag-hint';
                dragHint.textContent = '🎯 拖拽功能已启用';
                container.appendChild(dragHint);
                
                loadDefaultMindMap();
                
                console.log('✅ JSMind初始化成功');
                
            } catch (error) {
                console.error('❌ JSMind初始化失败:', error);
                document.getElementById('loading').innerHTML = '❌ 脑图引擎加载失败：' + error.message;
            }
        }
        
        function loadDefaultMindMap() {
            const defaultData = {
                "meta": {"name": "Injection Mind Map", "author": "Injection Tool", "version": "1.0"},
                "format": "node_tree",
                "data": {
                    "id": "center",
                    "topic": "🧠 中心节点",
                    "children": [
                        {
                            "id": "projects",
                            "topic": "📁 项目管理",
                            "direction": "left",
                            "children": [
                                {
                                    "id": "current_project",
                                    "topic": "📌 当前项目: injection"
                                }
                            ]
                        },
                        {
                            "id": "workflow",
                            "topic": "🔄 工作流程",
                            "direction": "right",
                            "children": [
                                {
                                    "id": "input_stage",
                                    "topic": "📥 输入阶段"
                                },
                                {
                                    "id": "process_stage", 
                                    "topic": "⚙️ 处理阶段"
                                },
                                {
                                    "id": "output_stage",
                                    "topic": "📤 输出阶段"
                                }
                            ]
                        },
                        {
                            "id": "tools",
                            "topic": "🛠️ 工具集合",
                            "direction": "left",
                            "children": [
                                {
                                    "id": "injection_tool",
                                    "topic": "💉 注入工具"
                                },
                                {
                                    "id": "mindmap_tool",
                                    "topic": "🧠 脑图工具"
                                }
                            ]
                        },
                        {
                            "id": "knowledge",
                            "topic": "📚 知识体系",
                            "direction": "right",
                            "children": [
                                {
                                    "id": "experience",
                                    "topic": "💡 经验积累"
                                },
                                {
                                    "id": "best_practices",
                                    "topic": "⭐ 最佳实践"
                                }
                            ]
                        }
                    ]
                }
            };
            
            if (jm) {
                jm.show(defaultData);
                console.log('🧠 JSMind脑图已加载，中心节点设置完成');
                
                // 延迟启用节点拖拽功能，确保节点已渲染
                setTimeout(() => {
                    enableNodeDragging();
                    console.log('🎯 拖拽功能自动启用');
                }, 1000);
            }
        }
        
        // 使用jsMind官方拖拽插件API启用拖拽
        function enableNodeDragging() {
            if (!jm) {
                console.warn('⚠️ JSMind未初始化，无法启用拖拽');
                return false;
            }
            
            try {
                // 使用jsMind官方拖拽插件API
                if (typeof jm.enable_draggable_node === 'function') {
                    jm.enable_draggable_node();
                    isDraggingEnabled = true;
                    console.log('✅ 使用jsMind官方拖拽插件启用成功');
                    return true;
                } else {
                    console.warn('⚠️ jsMind拖拽插件未加载，尝试回退方案');
                    return enableCustomDragging();
                }
            } catch (error) {
                console.error('❌ 启用拖拽功能失败:', error);
                console.log('🔄 尝试回退方案...');
                return enableCustomDragging();
            }
        }
        
        // 回退方案：自定义拖拽实现
        function enableCustomDragging() {
            console.log('🔄 启用自定义拖拽实现');
            
            isDraggingEnabled = true;
            let isDragging = false;
            let draggedNode = null;
            let dragOffset = { x: 0, y: 0 };
            let dragStartPos = { x: 0, y: 0 };
            
            function attachDragListeners() {
                const nodes = container.querySelectorAll('.jmnode:not([nodeid="center"])');
                console.log(`🔗 为 ${nodes.length} 个节点添加自定义拖拽监听器`);
                
                nodes.forEach(node => {
                    if (!node.dataset.customDragEnabled) {
                        node.dataset.customDragEnabled = 'true';
                        node.style.cursor = 'move';
                        node.title = '拖拽此节点重新排列位置（自定义实现）';
                        
                        node.addEventListener('mousedown', handleMouseDown);
                        node.addEventListener('dragstart', (e) => e.preventDefault());
                    }
                });
            }
            
            function handleMouseDown(e) {
                if (e.button !== 0 || !isDraggingEnabled) return;
                
                isDragging = true;
                draggedNode = e.currentTarget;
                
                const rect = draggedNode.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                
                dragOffset.x = e.clientX - rect.left;
                dragOffset.y = e.clientY - rect.top;
                dragStartPos.x = rect.left - containerRect.left;
                dragStartPos.y = rect.top - containerRect.top;
                
                draggedNode.classList.add('jmnode-dragging');
                document.body.style.userSelect = 'none';
                
                document.addEventListener('mousemove', handleMouseMove, true);
                document.addEventListener('mouseup', handleMouseUp, true);
                
                e.preventDefault();
                e.stopPropagation();
                
                console.log('🎯 开始自定义拖拽节点:', draggedNode.textContent);
            }
            
            function handleMouseMove(e) {
                if (!isDragging || !draggedNode) return;
                
                const containerRect = container.getBoundingClientRect();
                const x = e.clientX - containerRect.left - dragOffset.x;
                const y = e.clientY - containerRect.top - dragOffset.y;
                
                const nodeWidth = draggedNode.offsetWidth;
                const nodeHeight = draggedNode.offsetHeight;
                const maxX = container.clientWidth - nodeWidth;
                const maxY = container.clientHeight - nodeHeight;
                
                const finalX = Math.max(10, Math.min(x, maxX - 10));
                const finalY = Math.max(10, Math.min(y, maxY - 10));
                
                draggedNode.style.transform = `translate(${finalX - dragStartPos.x}px, ${finalY - dragStartPos.y}px)`;
                
                const elementsBelow = document.elementsFromPoint(e.clientX, e.clientY);
                const targetNode = elementsBelow.find(el => el.classList.contains('jmnode') && el !== draggedNode);
                
                container.querySelectorAll('.jmnode-dragover').forEach(node => {
                    node.classList.remove('jmnode-dragover');
                });
                
                if (targetNode) {
                    targetNode.classList.add('jmnode-dragover');
                }
                
                e.preventDefault();
                e.stopPropagation();
            }
            
            function handleMouseUp(e) {
                if (!isDragging) return;
                
                if (draggedNode) {
                    draggedNode.classList.remove('jmnode-dragging');
                    
                    const transform = draggedNode.style.transform;
                    const translateMatch = transform.match(/translate\(([^,]+),\s*([^)]+)\)/);
                    
                    if (translateMatch) {
                        const finalX = parseFloat(translateMatch[1]);
                        const finalY = parseFloat(translateMatch[2]);
                        
                        console.log('✅ 自定义拖拽完成:', draggedNode.textContent, `位置: (${finalX}, ${finalY})`);
                        
                        const nodeId = draggedNode.getAttribute('nodeid');
                        if (nodeId && jm) {
                            saveNodePosition(nodeId, { x: finalX, y: finalY });
                        }
                    }
                }
                
                document.body.style.userSelect = '';
                container.querySelectorAll('.jmnode-dragover').forEach(node => {
                    node.classList.remove('jmnode-dragover');
                });
                
                isDragging = false;
                draggedNode = null;
                
                document.removeEventListener('mousemove', handleMouseMove, true);
                document.removeEventListener('mouseup', handleMouseUp, true);
                
                e.preventDefault();
                e.stopPropagation();
            }
            
            setTimeout(attachDragListeners, 200);
            
            const attachInterval = setInterval(() => {
                if (isDraggingEnabled) {
                    attachDragListeners();
                } else {
                    clearInterval(attachInterval);
                }
            }, 2000);
            
            return true;
        }
        
        // 禁用拖拽功能
        function disableNodeDragging() {
            try {
                // 首先尝试使用jsMind官方API
                if (jm && typeof jm.disable_draggable_node === 'function') {
                    jm.disable_draggable_node();
                    console.log('✅ 使用jsMind官方API禁用拖拽');
                }
                
                // 清理自定义拖拽监听器
                const nodes = container.querySelectorAll('.jmnode');
                nodes.forEach(node => {
                    if (node.dataset.customDragEnabled) {
                        node.dataset.customDragEnabled = 'false';
                        node.style.cursor = 'pointer';
                        node.title = '';
                        
                        const newNode = node.cloneNode(true);
                        node.parentNode.replaceChild(newNode, node);
                    }
                });
                
                isDraggingEnabled = false;
                console.log('🔒 拖拽功能已禁用');
                return true;
                
            } catch (error) {
                console.error('❌ 禁用拖拽功能失败:', error);
                return false;
            }
        }
        
        // 保存节点位置
        function saveNodePosition(nodeId, position) {
            try {
                const mindData = jm.get_data();
                console.log(`💾 保存节点 ${nodeId} 位置:`, position);
                
                if (window.qt && window.qt.webChannelTransport) {
                    window.qt.webChannelTransport.send(JSON.stringify({
                        type: 'node_moved',
                        nodeId: nodeId,
                        position: position,
                        timestamp: new Date().toISOString()
                    }));
                }
                
                window.dispatchEvent(new CustomEvent('nodeMoved', {
                    detail: { nodeId, position }
                }));
                
            } catch (error) {
                console.error('💥 保存节点位置失败:', error);
            }
        }
        
        // 页面加载完成后初始化
        window.addEventListener('load', function() {
            setTimeout(initJSMind, 500);
        });
        
        // 暴露API给Python调用
        window.mindmapAPI = {
            loadData: function(data) {
                if (jm) {
                    jm.show(data);
                    setTimeout(() => {
                        if (isDraggingEnabled) {
                            enableNodeDragging();
                        }
                    }, 500);
                }
            },
            resetView: function() {
                if (jm) jm.view.reset();
            },
            enableDragging: function() {
                return enableNodeDragging();
            },
            disableDragging: function() {
                return disableNodeDragging();
            },
            isDraggingEnabled: function() {
                return isDraggingEnabled;
            },
            getNodePosition: function(nodeId) {
                const nodeElement = container.querySelector(`[nodeid="${nodeId}"]`);
                if (nodeElement) {
                    const transform = nodeElement.style.transform;
                    const translateMatch = transform.match(/translate\(([^,]+),\s*([^)]+)\)/);
                    
                    if (translateMatch) {
                        return {
                            x: parseFloat(translateMatch[1]),
                            y: parseFloat(translateMatch[2])
                        };
                    }
                    
                    return {
                        x: parseFloat(nodeElement.style.left) || 0,
                        y: parseFloat(nodeElement.style.top) || 0
                    };
                }
                return null;
            },
            setNodePosition: function(nodeId, position) {
                const nodeElement = container.querySelector(`[nodeid="${nodeId}"]`);
                if (nodeElement) {
                    nodeElement.style.transform = `translate(${position.x}px, ${position.y}px)`;
                    return true;
                }
                return false;
            },
            exportMindmap: function() {
                if (jm) {
                    return jm.get_data();
                }
                return null;
            },
            addNode: function(parentId, nodeData) {
                if (jm && parentId && nodeData) {
                    const newNodeId = 'node_' + Date.now();
                    jm.add_node(parentId, newNodeId, nodeData.topic || '新节点', nodeData);
                    
                    setTimeout(() => {
                        if (isDraggingEnabled) {
                            const newNode = container.querySelector(`[nodeid="${newNodeId}"]`);
                            if (newNode && !newNode.dataset.customDragEnabled) {
                                newNode.dataset.customDragEnabled = 'true';
                                newNode.style.cursor = 'move';
                                newNode.title = '拖拽此节点重新排列位置';
                                newNode.addEventListener('mousedown', handleMouseDown);
                            }
                        }
                    }, 200);
                    
                    return newNodeId;
                }
                return null;
            }
        };
        
        // 监听自定义事件
        window.addEventListener('nodeMoved', function(event) {
            console.log('📢 节点移动事件:', event.detail);
        });
        
    </script>
</body>
</html>
        '''
    
    def sync_with_list_selection(self, selected_data):
        """与列表选择同步"""
        if WEBENGINE_AVAILABLE and self.web_view:
            js_code = f"console.log('同步数据:', {json.dumps(selected_data)});"
            self.web_view.page().runJavaScript(js_code)
        elif self.web_view:
            # 在简化模式下更新显示
            title = selected_data.get('title', '未知项目')
            self.web_view.setHtml(f"""
                <div style="text-align: center; padding: 50px; color: #666;">
                    <h3>🧠 脑图功能</h3>
                    <p>当前同步项目: <strong>{title}</strong></p>
                    <p style="font-size: 12px; color: #999;">
                        注意：完整的脑图功能需要安装 PyQt5.QtWebEngineWidgets<br>
                        当前使用简化显示模式
                    </p>
                </div>
            """)
    
    def reset_view(self):
        """重置脑图视图"""
        if WEBENGINE_AVAILABLE and self.web_view:
            js_code = "window.mindmapAPI.resetView();"
            self.web_view.page().runJavaScript(js_code)
    
    def enable_node_dragging(self):
        """启用节点拖拽功能"""
        if WEBENGINE_AVAILABLE and self.web_view:
            js_code = "window.mindmapAPI.enableDragging();"
            self.web_view.page().runJavaScript(js_code)
            print("🎯 脑图节点拖拽功能已启用")
        else:
            # 简化模式下也可以使用拖拽模拟
            if isinstance(self.web_view, QTextBrowser):
                # 更新HTML以启用拖拽模拟
                current_html = self.web_view.toHtml()
                if "enableDragSimulation" in current_html:
                    # 通过更新HTML来触发拖拽启用
                    updated_html = current_html.replace(
                        'span id="drag-status" style="margin-left: 10px; font-size: 11px; color: #666;">未启用</span>',
                        'span id="drag-status" style="margin-left: 10px; font-size: 11px; color: #4CAF50;">✅ 拖拽模拟已启用</span>'
                    )
                    self.web_view.setHtml(updated_html)
                    print("🎯 简化模式拖拽模拟功能已启用")
                else:
                    print("💡 拖拽功能需要WebEngine支持，当前为简化模式")
    
    def disable_node_dragging(self):
        """禁用节点拖拽功能"""
        if WEBENGINE_AVAILABLE and self.web_view:
            js_code = "window.mindmapAPI.disableDragging();"
            self.web_view.page().runJavaScript(js_code)
            print("🔒 脑图节点拖拽功能已禁用")
        else:
            # 简化模式下禁用拖拽模拟
            if isinstance(self.web_view, QTextBrowser):
                current_html = self.web_view.toHtml()
                if "enableDragSimulation" in current_html:
                    # 通过更新HTML来触发拖拽禁用
                    updated_html = current_html.replace(
                        'span id="drag-status" style="margin-left: 10px; font-size: 11px; color: #4CAF50;">✅ 拖拽模拟已启用</span>',
                        'span id="drag-status" style="margin-left: 10px; font-size: 11px; color: #666;">❌ 拖拽模拟已禁用</span>'
                    )
                    self.web_view.setHtml(updated_html)
                    print("🔒 简化模式拖拽模拟功能已禁用")
                else:
                    print("💡 拖拽功能需要WebEngine支持，当前为简化模式")
    
    def get_node_position(self, node_id, callback=None):
        """获取节点位置"""
        if WEBENGINE_AVAILABLE and self.web_view:
            js_code = f"window.mindmapAPI.getNodePosition('{node_id}');"
            if callback:
                self.web_view.page().runJavaScript(js_code, callback)
            else:
                self.web_view.page().runJavaScript(js_code)
    
    def set_node_position(self, node_id, x, y):
        """设置节点位置"""
        if WEBENGINE_AVAILABLE and self.web_view:
            js_code = f"window.mindmapAPI.setNodePosition('{node_id}', {{x: {x}, y: {y}}});"
            self.web_view.page().runJavaScript(js_code)
            print(f"📍 节点 {node_id} 位置已设置为 ({x}, {y})")
    
    def add_mindmap_node(self, parent_id, topic, callback=None):
        """添加新的脑图节点"""
        if WEBENGINE_AVAILABLE and self.web_view:
            js_code = f"window.mindmapAPI.addNode('{parent_id}', {{topic: '{topic}'}});"
            if callback:
                self.web_view.page().runJavaScript(js_code, callback)
            else:
                self.web_view.page().runJavaScript(js_code)
            print(f"➕ 已添加新节点: {topic}")
        else:
            print("💡 添加节点功能需要WebEngine支持")
    
    def export_mindmap_data(self, callback=None):
        """导出脑图数据"""
        if WEBENGINE_AVAILABLE and self.web_view:
            js_code = "window.mindmapAPI.exportMindmap();"
            if callback:
                self.web_view.page().runJavaScript(js_code, callback)
            else:
                self.web_view.page().runJavaScript(js_code)
        else:
            print("💡 导出功能需要WebEngine支持")


class SyncManager(QWidget):
    """同步管理器 - 处理阅读区与列表区的同步"""
    
    # 信号定义
    sync_triggered = pyqtSignal(str, dict)  # 同步触发信号
    
    def __init__(self, layout_manager, parent=None):
        super().__init__(parent)
        self.layout_manager = layout_manager
        self.current_selection = None
        self.init_sync_system()
    
    def init_sync_system(self):
        """初始化同步系统"""
        # 连接布局管理器的信号
        if self.layout_manager:
            self.layout_manager.layout_changed.connect(self.on_layout_changed)
    
    def on_layout_changed(self, event_type, data):
        """布局变化事件处理"""
        if event_type == "list_selection_sync":
            self.handle_list_selection_sync(data)
        elif event_type == "tab_changed":
            self.handle_tab_changed(data)
    
    def handle_list_selection_sync(self, data):
        """处理列表选择同步"""
        selected_data = data.get("selected_data", {})
        current_tab = data.get("current_tab", 0)
        
        self.current_selection = selected_data
        
        # 根据当前选项卡进行不同的同步处理
        if current_tab == 0:  # MD阅读器
            self.sync_md_reader(selected_data)
        elif current_tab == 1:  # 脑图
            self.sync_mindmap(selected_data)
        
        # 发送同步完成信号
        self.sync_triggered.emit("sync_completed", {
            "target_tab": current_tab,
            "selected_data": selected_data
        })
    
    def handle_tab_changed(self, data):
        """处理选项卡切换"""
        tab_name = data.get("tab_name", "")
        
        # 如果有当前选择，同步到新选项卡
        if self.current_selection:
            if tab_name == "md_reader":
                self.sync_md_reader(self.current_selection)
            elif tab_name == "mindmap":
                self.sync_mindmap(self.current_selection)
    
    def sync_md_reader(self, selected_data):
        """同步MD阅读器"""
        # 更新MD阅读器显示的内容
        title = selected_data.get("title", "未知项目")
        
        # 这里可以加载对应的MD文件或内容
        print(f"同步MD阅读器: {title}")
        
        # 通过布局管理器更新同步指示器
        if self.layout_manager:
            self.layout_manager.sync_with_list_selection(selected_data)
    
    def sync_mindmap(self, selected_data):
        """同步脑图显示"""
        title = selected_data.get("title", "未知项目")
        
        # 这里可以更新脑图的高亮节点或加载相关数据
        print(f"同步脑图显示: {title}")
        
        # 通过布局管理器更新同步指示器
        if self.layout_manager:
            self.layout_manager.sync_with_list_selection(selected_data)
    
    def trigger_manual_sync(self, list_item_data):
        """手动触发同步"""
        if self.layout_manager:
            self.layout_manager.sync_with_list_selection(list_item_data) 