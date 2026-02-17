# Photo File Tagger & Organizer

一个面向摄影师的 Python 文件标签与整理工具。选择文件、添加标签，程序会自动将文件移动或复制到对应的标签文件夹中。

> **注意：** 本项目建议迁移到独立的私密仓库中使用。以下是完整的使用说明。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `photo_tagger.py` | 主程序，包含核心逻辑、GUI 界面和 CLI 界面 |
| `test_photo_tagger.py` | 单元测试（18 个测试用例） |

## 支持的文件格式

| 类别 | 扩展名 |
|------|--------|
| 图片 | jpg, jpeg, png, bmp, gif, tiff, tif, webp, heic, heif |
| RAW  | cr2, cr3, nef, arw, orf, rw2, dng, raf, pef, srw |
| 视频 | mp4, mov, avi, mkv, wmv |
| 其他 | psd, ai, svg, pdf |

## 环境要求

- Python 3.10 及以上
- 标准库即可运行，无需安装第三方依赖
- GUI 模式需要系统安装 tkinter（大多数 Python 发行版自带）

## 使用方法

### GUI 模式（默认）

```bash
python photo_tagger.py
```

启动后可通过图形界面：
1. 点击 **Browse Files…** 选择一个或多个文件
2. 在标签输入框中输入标签（多个标签用逗号分隔，如 `风景, 日落, 海边`）
3. 选择目标文件夹
4. 勾选「Copy files」可保留原文件
5. 点击 **Tag & Organize** 完成整理

### CLI 模式

```bash
python photo_tagger.py --cli
```

按照提示输入文件路径、标签和目标文件夹即可。

## 运行测试

```bash
cd photo_tagger
python -m unittest test_photo_tagger -v
```

## 迁移到独立仓库

建议将本目录下的所有文件复制到一个新的私密仓库中：

```bash
# 1. 在 GitHub 上创建一个新的私密仓库（例如 photo-tagger）
# 2. 克隆并复制文件
git clone https://github.com/<你的用户名>/photo-tagger.git
cp photo_tagger.py test_photo_tagger.py README.md photo-tagger/
cd photo-tagger
git add .
git commit -m "Initial commit: photo file tagger"
git push origin main
```
