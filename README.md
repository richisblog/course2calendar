# UC Davis课表导出工具

这是一个基于Django的Web应用，帮助UC Davis学生将课表导出为ICS日历格式，方便导入到各种日历应用。

## 功能

- 上传UC Davis Schedule Builder的HTML文件
- 自动提取课程信息并生成ICS日历文件
- 支持导出课程时间、地点、期末考试和退课日期

## 安装

1. 安装Python 3.6+
2. 安装Django
   ```
   pip install django
   ```
3. 克隆或下载代码

## 运行

1. 创建媒体目录
   ```
   mkdir -p media/temp
   ```

2. 运行服务器
   ```
   python manage.py runserver
   ```

3. 访问 http://127.0.0.1:8000/ 使用工具

## 使用方法

1. 访问UC Davis Schedule Builder网站
2. 保存完整网页为HTML文件
3. 在本工具中上传HTML文件
4. 下载生成的ICS文件
5. 导入到您喜欢的日历应用

## 注意事项

- 本工具不会存储您的课表数据
- 处理完成后临时文件会被自动删除
- 建议在导入日历前检查ICS文件内容是否正确

## 开发者

本项目基于原始Python脚本开发，将其转换为Web应用以方便更多学生使用。 