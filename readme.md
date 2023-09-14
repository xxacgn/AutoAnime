# Monica动漫站的脚本仓库
文件结构如下
```shell
after-bt-download.py : bt文件下载完成后运行的脚本
└── updateList.py : 更新新番列表markdown文件，提供直达链接

├── body.html : 网站前端的修改内容，应填写在alist后台的body部分
└── head.html : 网站前端的修改内容，应填写在alist后台的head部分

cp.py : 定时移动文件的脚本，用来同步服务器端文件，从而跨越长城订阅番剧

rssGen_rssUp.py : 处理生成rss订阅文件并发布，但是灵车
```

动漫网站：[anime-web](https://hackermonica.me)

网站搭建指北：[blog](https://blog.hackermonica.me/2023/09/08/anime-web-build/)