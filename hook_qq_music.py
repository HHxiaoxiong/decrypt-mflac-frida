import frida
import shutil
import hashlib
import os
from pathlib import Path

# 挂钩 QQ 音乐进程
session = frida.attach("QQMusic.exe")

# 加载并执行 JavaScript 脚本
script = session.create_script(open("hook_qq_music.js", "r", encoding="utf-8").read())
script.load()

# 创建输出目录
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
output_dir = os.path.abspath(output_dir)
# 获取用户音乐目录路径
# home = str(Path.home()) + "\\Music\\VipSongsDownload"
home = "F:\\music\\VipSongsDownload"
home = os.path.abspath(home)

# 遍历目录下的所有文件
for root, dirs, files in os.walk(home):
    for file in files:
        file_path = os.path.splitext(file)

        # 获取子目录名并创建目录
        authdir = os.path.basename(root)
        outdir = os.path.join(output_dir, authdir)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        # 只处理 .mflac 和 .mgg 文件
        if file_path[-1] in [".mflac", ".mgg"]:
            print("Decrypting", file)

            # 修改文件扩展名
            file_path = list(file_path)
            file_path[-1] = file_path[-1].replace("mflac", "flac").replace("mgg", "ogg")
            file_path_str = "".join(file_path)

            print(file_path_str)
            # 检查解密文件是否已经存在
            output_file_path = os.path.join(outdir, file_path_str)
            if os.path.exists(output_file_path):
                print(f"File {output_file_path} 已存在，跳过.")
                continue
            
            tmp_file_path = hashlib.md5(file.encode()).hexdigest()
            tmp_file_path = os.path.join(output_dir, tmp_file_path)
            
            # 调用脚本中的 decrypt 方法解密文件
            data = script.exports_sync.decrypt(os.path.join(root, file), tmp_file_path)

            # 移动临时文件
            shutil.move(tmp_file_path, output_file_path)
            
        elif file_path[-1] in [".lrc"]:
            file_path_str = "".join(os.path.join(root, file))
            mbfile_path_str = "".join(
                os.path.join(outdir, os.path.basename(file_path_str))
            )
            if os.path.exists(mbfile_path_str):
                continue
            shutil.copyfile(file_path_str, mbfile_path_str)

# 清理不存在的lrc文件
for root, dirs, files in os.walk(output_dir):
    # 判断是否为空目录
    if not os.listdir(root):
      os.rmdir(root)
    for file in files:
        file_path = os.path.splitext(file)
        # 只处理 .lrc 文件
        if file_path[-1] in [".lrc"]:
            # 修改文件扩展名
            file_path = list(file_path)
            lrcfile = "".join(file_path)
            file_path[-1] = file_path[-1].replace("lrc", "flac")
            file_path_str = "".join(file_path)
            yyfile_path_str = os.path.join(root, file_path_str)
            if os.path.exists(yyfile_path_str):
                continue
            os.remove(os.path.join(root, lrcfile))
            if not os.listdir(root):
                os.rmdir(root)

# 分离会话
session.detach()
