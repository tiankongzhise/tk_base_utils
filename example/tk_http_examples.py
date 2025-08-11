"""HTTP客户端库使用示例"""

import asyncio
from src.tk_base_utils.tk_http import HttpClient, ClientConfig


def sync_examples():
    """同步调用示例"""
    print("=== 同步调用示例 ===")
    
    # 1. 基本使用
    print("\n1. 基本GET请求:")
    client = HttpClient()
    try:
        response = client.get("https://httpbin.org/get")
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {response.elapsed:.3f}s")
        print(f"响应内容: {response.json_data}")
    except Exception as e:
        print(f"请求失败: {e}")
    finally:
        client.close()
    
    # 2. 自定义配置
    print("\n2. 自定义配置:")
    config = ClientConfig(
        timeout=10.0,
        max_retries=2,
        log_level="DEBUG",
        headers={"User-Agent": "MyApp/1.0"}
    )
    
    with HttpClient(config) as client:
        try:
            response = client.post(
                "https://httpbin.org/post",
                json={"name": "测试", "value": 123},
                headers={"Content-Type": "application/json"}
            )
            print(f"POST响应: {response.status_code}")
            if response.json_data:
                print(f"服务器收到的数据: {response.json_data.get('json')}")
        except Exception as e:
            print(f"POST请求失败: {e}")
    
    # 3. 错误处理
    print("\n3. 错误处理示例:")
    with HttpClient() as client:
        try:
            # 故意请求一个不存在的域名来触发重试
            response = client.get("https://nonexistent-domain-12345.com")
        except Exception as e:
            print(f"预期的错误: {type(e).__name__}: {e}")


async def async_examples():
    """异步调用示例"""
    print("\n=== 异步调用示例 ===")
    
    # 1. 基本异步请求
    print("\n1. 基本异步GET请求:")
    async with HttpClient() as client:
        try:
            response = await client.aget("https://httpbin.org/get")
            print(f"异步状态码: {response.status_code}")
            print(f"异步响应时间: {response.elapsed:.3f}s")
        except Exception as e:
            print(f"异步请求失败: {e}")
    
    # 2. 并发请求
    print("\n2. 并发请求示例:")
    async with HttpClient() as client:
        urls = [
            "https://httpbin.org/delay/1",
            "https://httpbin.org/delay/2", 
            "https://httpbin.org/delay/1"
        ]
        
        tasks = [client.aget(url) for url in urls]
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"请求 {i+1} 失败: {response}")
                else:
                    print(f"请求 {i+1} 成功: {response.status_code}, 耗时: {response.elapsed:.3f}s")
        except Exception as e:
            print(f"并发请求失败: {e}")


def log_persistence_examples():
    """日志持久化示例"""
    print("\n=== 日志持久化示例 ===")
    
    # 配置日志持久化到文件
    config = ClientConfig(
        log_level="DEBUG",
        log_file_path="logs/http_client.log",  # 日志文件路径
        log_file_max_size=5*1024*1024,  # 5MB
        log_file_backup_count=3,  # 保留3个备份文件
        log_requests=True,
        log_responses=True
    )
    
    print("配置了日志持久化到 logs/http_client.log")
    print("日志文件最大大小: 5MB，备份文件数: 3")
    
    with HttpClient(config) as client:
        try:
            # 执行一些请求，日志会同时输出到控制台和文件
            response = client.get("https://httpbin.org/get", params={"test": "log_persistence"})
            print(f"请求成功: {response.status_code}")
            
            response = client.post("https://httpbin.org/post", json={"message": "测试日志持久化"})
            print(f"POST请求成功: {response.status_code}")
            
            print("\n日志已记录到文件和控制台")
            print("可以查看 logs/http_client.log 文件查看详细日志")
            
        except Exception as e:
            print(f"请求失败: {e}")
    
    # 演示禁用日志轮转的配置（适用于共享日志文件的场景）
    print("\n--- 共享日志文件配置示例 ---")
    shared_config = ClientConfig(
        log_level="INFO",
        log_file_path="logs/shared_app.log",  # 与其他组件共享的日志文件
        log_file_rotation_enabled=False,  # 禁用轮转，由外部日志管理系统控制
        log_requests=True,
        log_responses=True
    )
    
    print("配置了共享日志文件模式（禁用轮转）")
    print("适用于多个组件共享同一日志文件的场景")
    
    with HttpClient(shared_config) as client:
        try:
            response = client.get("https://httpbin.org/get", params={"mode": "shared_log"})
            print(f"共享日志模式请求成功: {response.status_code}")
            print("日志已追加到共享文件，不会进行轮转")
            
        except Exception as e:
            print(f"共享日志模式请求失败: {e}")


def advanced_examples():
    """高级功能示例"""
    print("\n=== 高级功能示例 ===")
    
    # 1. 自定义重试配置
    print("\n1. 自定义重试配置:")
    config = ClientConfig(
        max_retries=5,
        retry_delay=0.5,
        retry_backoff_factor=1.5,
        log_level="INFO"
    )
    
    with HttpClient(config) as client:
        try:
            # 模拟超时场景
            response = client.get(
                "https://httpbin.org/delay/10",  # 10秒延迟
                timeout=2.0  # 2秒超时
            )
        except Exception as e:
            print(f"超时重试示例: {type(e).__name__}: {e}")
    
    # 2. 请求参数示例
    print("\n2. 各种请求参数:")
    with HttpClient() as client:
        try:
            # GET with params
            response = client.get(
                "https://httpbin.org/get",
                params={"key1": "value1", "key2": "value2"}
            )
            print(f"GET with params: {response.status_code}")
            
            # POST with form data
            response = client.post(
                "https://httpbin.org/post",
                data={"form_field": "form_value"}
            )
            print(f"POST with form data: {response.status_code}")
            
            # PUT with JSON
            response = client.put(
                "https://httpbin.org/put",
                json={"update": "data"}
            )
            print(f"PUT with JSON: {response.status_code}")
            
        except Exception as e:
            print(f"请求参数示例失败: {e}")


def response_handling_examples():
    """响应处理示例"""
    print("\n=== 响应处理示例 ===")
    
    with HttpClient() as client:
        try:
            response = client.get("https://httpbin.org/json")
            
            print(f"\n响应详情:")
            print(f"状态码: {response.status_code}")
            print(f"是否成功: {response.is_success()}")
            print(f"响应头数量: {len(response.headers)}")
            print(f"内容长度: {len(response.content)} bytes")
            print(f"文本长度: {len(response.text)} chars")
            print(f"编码: {response.encoding}")
            print(f"最终URL: {response.url}")
            
            if response.json_data:
                print(f"JSON数据: {response.json_data}")
            
            # 检查状态码
            if response.is_success():
                print("请求成功!")
            elif response.is_client_error():
                print("客户端错误")
            elif response.is_server_error():
                print("服务器错误")
                
        except Exception as e:
            print(f"响应处理示例失败: {e}")


if __name__ == "__main__":
    print("HTTP客户端库使用示例")
    print("=" * 50)
    
    # 运行同步示例
    sync_examples()
    
    # 运行异步示例
    asyncio.run(async_examples())
    
    # 运行日志持久化示例
    log_persistence_examples()
    
    # 运行高级示例
    advanced_examples()
    
    # 运行响应处理示例
    response_handling_examples()

    print("\n示例运行完成!")
