import requests
import aiohttp
import asyncio
import json
from loguru import logger

def banner():
  print("""
   ______  ______   ______  ______     ______   ______  _____  _____    ______  ______  
| |     / |  | \ | |     | |  | |   / |      | |  | \  | |  | | \ \  | |     | |  | \ 
| |---- | |  | | | |---- | |__| |   '------. | |__|_/  | |  | |  | | | |---- | |__| | 
|_|     \_|__|_/ |_|     |_|  |_|    ____|_/ |_|      _|_|_ |_|_/_/  |_|____ |_|  \_\ 
                                                                                      
        """)

def get_fofa(api_url):
  """请求FofaAPI获取结果

  Args:
      api_url: api url地址

  Returns:
      返回一个url列表
  """
  try:
    res = requests.get(url = api_url).text
    results = json.loads(res)['results']  # json结果转换为字典
    results = ['http://' + url[0] if not url[0].startswith('http') else url[0] for url in results]  # url中没有协议则默认添加http协议
    print("[*]成功获取结果%d条..." % len(results))
    print("[+]正在进行存活检查...")
    return results  
  except Exception as e:
    print(e)

async def check_url(url, output_format):
  """检查url是否存活（可访问）

  Args:
      url: url

  Returns:
      pass
  """
  async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
    try:
      async with session.get(url = url, timeout=5) as resp:
        text = await resp.text()
        logger.info(url)
        if output_format == 'y' or output_format == 'N':
          with open('result', 'a+') as f:
            f.write(url+'\n')
    except Exception as e:
      logger.info(url)
      if output_format == 'N':
        with open('result', 'a+') as f:
          f.write(url+'\n')


if __name__ == '__main__':
  banner()
  api_url = input(">API：")
  output = input("请选择是否只输出存活url[y/N导出全部] ")
  results = get_fofa(api_url)
  loop = asyncio.get_event_loop()  # 获取当前事件循环, 如果没有则创建并将其设为当前时间循环
  try:
    if results: # 判断是否有url
      tasks = [asyncio.ensure_future(check_url(url, output)) for url in results]  # ensure_future(obj), 如果obj是一个协程则加入执行计划
      loop.run_until_complete(asyncio.wait(tasks))  # wait(aws) aws需是可迭代且不为空对象, 返回done和panding集合. run_until_complete(future)运行和停止事件循环, 返回 Future 的结果 或者引发相关异常.
    else:
      print("Error:没有搜索到结果!")
  except Exception as e:
    print(e)