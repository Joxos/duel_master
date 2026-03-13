#### 类型注解

- 使用内置类型写法，减少对`typing`的依赖（PEP 585）
  - 这意味着对于可选类型，使用`X | None`而不是`typing.Optional[X]`

#### 代码注释

- 完整句子需要单独成行，首字母大写。
- 不完整句子采用行尾注释，首字母小写。
- MVP前阶段可以不编写模块的docstring，但是要编写类和函数的docstring
- 类和函数的docstring采用`Google Style`
  - 不提供任何额外信息的docstring不应被编写，如：`"""Tests for foo.bar."""`

#### 当前阶段执行策略

- 先不写文档页，优先写`examples/`下的示例对局。
- `examples/`示例必须可执行，并且可被冒烟测试直接调用。
