# API 文档

## HttpClient 类

### 构造函数

```python
HttpClient(config: Optional[ClientConfig] = None)
```

创建HTTP客户端实例。

**参数:**
- `config`: 客户端配置对象，可选

### 同步方法

#### request(method, url, **kwargs)

发送HTTP请求的通用方法。

**参数:**
- `method`: HTTP方法（GET, POST, PUT, DELETE等）
- `url`: 请求URL
- `**kwargs`: 其他请求参数

**返回:** `Response` 对象

#### get(url, **kwargs)

发送GET请求。

#### post(url, **kwargs)

发送POST请求。

#### put(url, **kwargs)

发送PUT请求。

#### delete(url, **kwargs)

发送DELETE请求。

#### patch(url, **kwargs)

发送PATCH请求。

#### head(url, **kwargs)

发送HEAD请求。

#### options(url, **kwargs)

发送OPTIONS请求。

### 异步方法

#### arequest(method, url, **kwargs)

发送异步HTTP请求的通用方法。

#### aget(url, **kwargs)

发送异步GET请求。

#### apost(url, **kwargs)

发送异步POST请求。

#### aput(url, **kwargs)

发送异步PUT请求。

#### adelete(url, **kwargs)

发送异步DELETE请求。

#### apatch(url, **kwargs)

发送异步PATCH请求。

#### ahead(url, **kwargs)

发送异步HEAD请求。

#### aoptions(url, **kwargs)

发送异步OPTIONS请求。

### 上下文管理

```python
# 同步上下文管理器
with HttpClient() as client:
    response = client.get("https://example.com")

# 异步上下文管理器
async with HttpClient() as client:
    response = await client.aget("https://example.com")
```

## ClientConfig 类

### 配置参数

```python
class ClientConfig(BaseModel):
    timeout: float = 30.0                    # 总超时时间
    connect_timeout: float = 10.0            # 连接超时
    read_timeout: float = 30.0               # 读取超时
    max_retries: int = 3                     # 最大重试次数
    retry_delay: float = 1.0                 # 重试基础延迟
    retry_backoff_factor: float = 2.0        # 重试退避因子
    log_level: str = "INFO"                  # 日志级别
    log_requests: bool = True                # 记录请求日志
    log_responses: bool = True               # 记录响应日志
    log_file_path: Optional[str] = None      # 日志文件路径（持久化）
    log_file_max_size: int = 10*1024*1024    # 日志文件最大大小（10MB）
    log_file_backup_count: int = 5           # 日志文件备份数量
    log_file_rotation_enabled: bool = True   # 是否启用日志文件轮转
    headers: Dict[str, str] = {}             # 默认请求头
    user_agent: str = "HttpClient/0.1.0"     # 用户代理
    follow_redirects: bool = True            # 跟随重定向
    verify_ssl: bool = True                  # 验证SSL证书
```

### 方法

#### get_timeout_config()

获取超时配置字典。

#### get_retry_config()

获取重试配置字典。

## Response 类

### 属性

```python
class Response(BaseModel):
    status_code: int                         # HTTP状态码
    headers: Dict[str, str]                  # 响应头
    content: bytes                           # 响应内容（字节）
    text: str                                # 响应内容（文本）
    json_data: Optional[Dict[str, Any]]      # JSON数据
    elapsed: float                           # 请求耗时
    url: str                                 # 最终URL
    encoding: Optional[str]                  # 响应编码
```

### 方法

#### is_success() -> bool

判断请求是否成功（状态码2xx）。

#### is_client_error() -> bool

判断是否为客户端错误（状态码4xx）。

#### is_server_error() -> bool

判断是否为服务器错误（状态码5xx）。

#### json() -> Optional[Dict[str, Any]]

获取JSON数据（等同于json_data属性）。

#### raise_for_status() -> None

如果状态码表示错误则抛出HttpStatusError异常。

#### from_httpx_response(response, elapsed) -> Response

从httpx响应对象创建Response实例（类方法）。

## 异常类

### HttpClientError

基础异常类，所有客户端异常的父类。

### TimeoutError

超时异常，继承自HttpClientError。

### ConnectionError

连接异常，继承自HttpClientError。

### RetryExhaustedError

重试次数耗尽异常，继承自HttpClientError。

### ValidationError

数据校验异常，继承自HttpClientError。

### HttpStatusError

HTTP状态码异常，继承自HttpClientError。

**属性:**
- `status_code`: HTTP状态码

## 请求参数

### 通用参数

所有HTTP方法都支持以下参数：

- `headers`: 请求头字典
- `params`: 查询参数字典
- `timeout`: 请求超时时间
- `cookies`: Cookie字典
- `auth`: 认证信息

### POST/PUT/PATCH 特有参数

- `json`: JSON数据（自动设置Content-Type为application/json）
- `data`: 表单数据或原始数据
- `files`: 文件上传字典
- `content`: 原始内容（字节或字符串）

## 使用示例

### 基本请求

```python
from client_core import HttpClient

with HttpClient() as client:
    # GET请求
    response = client.get("https://api.example.com/users")
    
    # POST JSON数据
    response = client.post(
        "https://api.example.com/users",
        json={"name": "张三", "age": 25}
    )
    
    # 带查询参数的GET请求
    response = client.get(
        "https://api.example.com/users",
        params={"page": 1, "size": 10}
    )
    
    # 自定义请求头
    response = client.get(
        "https://api.example.com/users",
        headers={"Authorization": "Bearer token"}
    )
```

### 异步请求

```python
import asyncio
from client_core import HttpClient

async def main():
    async with HttpClient() as client:
        # 异步GET请求
        response = await client.aget("https://api.example.com/users")
        
        # 并发请求
        tasks = [
            client.aget("https://api.example.com/users/1"),
            client.aget("https://api.example.com/users/2")
        ]
        responses = await asyncio.gather(*tasks)

asyncio.run(main())
```

### 错误处理

```python
from client_core import HttpClient
from client_core.exceptions import (
    TimeoutError,
    ConnectionError,
    HttpStatusError
)

with HttpClient() as client:
    try:
        response = client.get("https://api.example.com/users")
        response.raise_for_status()
        data = response.json()
    except TimeoutError:
        print("请求超时")
    except ConnectionError:
        print("连接失败")
    except HttpStatusError as e:
        print(f"HTTP错误: {e.status_code}")
```

### 自定义配置

```python
from client_core import HttpClient, ClientConfig

config = ClientConfig(
    timeout=60.0,
    max_retries=5,
    retry_delay=2.0,
    log_level="DEBUG",
    headers={"User-Agent": "MyApp/1.0"}
)

with HttpClient(config) as client:
    response = client.get("https://api.example.com/users")
```

### 日志持久化配置

```python
from client_core import HttpClient, ClientConfig

# 配置日志持久化到文件（启用轮转）
config = ClientConfig(
    log_level="DEBUG",
    log_file_path="logs/http_client.log",  # 日志文件路径
    log_file_max_size=5*1024*1024,         # 5MB文件大小限制
    log_file_backup_count=3,               # 保留3个备份文件
    log_file_rotation_enabled=True,        # 启用日志轮转（默认值）
    log_requests=True,                     # 记录请求日志
    log_responses=True                     # 记录响应日志
)

# 配置共享日志文件（禁用轮转）
shared_config = ClientConfig(
    log_level="INFO",
    log_file_path="logs/shared_app.log",   # 与其他组件共享的日志文件
    log_file_rotation_enabled=False,       # 禁用轮转，由外部系统管理
    log_requests=True,
    log_responses=True
)

with HttpClient(config) as client:
    # 请求日志会同时输出到控制台和文件
    response = client.get("https://api.example.com/users")
    
    # 日志文件会自动轮转，当达到最大大小时创建新文件
    # 文件命名格式: http_client.log, http_client.log.1, http_client.log.2, ...
```

**日志持久化特性:**
- 自动创建日志目录
- 支持日志文件轮转（RotatingFileHandler）
- 可配置是否启用轮转（适用于共享日志文件场景）
- 同时输出到控制台和文件
- 自动过滤敏感信息（如Authorization头）
- UTF-8编码支持

**轮转控制说明:**
- `log_file_rotation_enabled=True`：使用RotatingFileHandler，自动轮转日志文件
- `log_file_rotation_enabled=False`：使用普通FileHandler，适用于多组件共享日志文件的场景