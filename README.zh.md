# Duel Master 项目

## 概述

本项目采用基于 `EventManager` 的可扩展事件驱动架构，并支持模块化开发。通过添加新模块，可以灵活扩展系统功能。

---

## EventManager 事件管理器

`EventManager` 是事件驱动系统的核心，主要功能包括：

- **注册新事件类型**：通过继承 `Event` 基类实现。
- **为事件类型绑定回调函数**：使用 `@subscribe` 装饰器实现。
- **触发事件**：通过 `emit` 方法激活所有已注册的回调。

这种设计实现了系统各部分的解耦，便于功能扩展和维护。

---

## 模块（Module）

模块是自包含的功能包，每个模块是 `modules` 目录下的一个文件夹。模块可以定义自己的事件和事件处理函数。

### 模块文件结构最佳实践

每个模块建议采用如下结构：

```
modules/
  your_module/
    __init__.py
    handlers.py    # 注册事件监听
    events.py      # （可选）定义事件类和事件处理函数
    models.py      # （可选）模块数据模型
    handlers.py    # （可选）模块业务逻辑
    ...
```

- **events.py**：  
  - 继承 `Event` 定义自定义事件。
  - 使用 `@subscribe` 装饰器注册事件处理函数。
- **models.py/handlers.py**：  
  - 根据需要组织模块的数据和逻辑。

### 示例：`events.py`

```python
from event_core import Event
from subscribe import subscribe

class MyCustomEvent(Event):
    def __init__(self, data):
        self.data = data

@subscribe(MyCustomEvent)
def handle_my_event(event):
    print(f"收到事件，数据为: {event.data}")
```

---

## 如何添加新模块

1. 在 `modules/` 下新建文件夹。
2. 添加 `events.py`，定义事件和处理函数。
3. （可选）根据需要添加其他文件。

---

## 快速开始

1. 确保所有模块都放在 `modules` 目录下。
2. 系统启动时会自动发现并注册所有事件和处理函数。
3. 使用 `event_manager.emit(Event实例)` 触发事件。

---

## 许可证

MIT License
