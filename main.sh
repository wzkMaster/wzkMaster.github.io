#!/bin/bash  
  
# 遍历./content/post文件夹下的所有子文件夹  
for dir in ./content/post/*/; do  
  # 提取文件夹名称  
  dir_name=$(basename "$dir")  
    
  # 执行"python3 script.py"命令，将文件夹名称作为参数传递  
  python3 script.py "$dir_name"  

  # 暂停1秒钟  
  sleep 1 
done