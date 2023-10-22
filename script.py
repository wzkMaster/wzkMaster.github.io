import re
import requests
import os
import sys

# 获取markdown文件路径和图片保存目录
prefix = "content/post"
dest_dir = os.path.join(prefix, sys.argv[1])
markdown_file = os.path.join(dest_dir, 'index.md')

# 读取markdown文件内容
with open(markdown_file) as f:
    text = f.read()

# 用正则匹配图片链接    
matches = re.findall(r'!\[[^\]]*\]\((https?:\/\/[^)]+)', text)
idx = 0
for match in matches:
    # 提取图片链接
    img_src = match[match.find("(")+1:-1]  

    # 下载图片
    response = requests.get(img_src)
    img_name = str(idx) + '.jpg'
    with open(os.path.join(dest_dir, img_name), 'wb') as f:
        f.write(response.content)
        
    # 替换为本地链接
    text = text.replace(match, img_name)
    text = re.sub(r"!\[.+\]", "![]", text)
    idx += 1
    
# 写回文件
with open(markdown_file, 'w') as f:
    f.write(text)