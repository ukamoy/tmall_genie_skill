# tmall_genie_skill
天猫精灵针对海外无法设置地址, 提供天气和时间查询, 可以扩展到其他查询需求, 比如新闻和金融


项目为fastApi, 本地启动命令:  
```uvicorn handlers.main:app --host 0.0.0.0 --port 8000```  

需要在weatherapi.com申请apikey, 加到环境变量WEATHER_API_KEY
