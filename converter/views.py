import os
import sys
import tempfile
import re
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.conf import settings
from .forms import HtmlUploadForm
import shutil
from bs4 import BeautifulSoup

def extract_term_code_from_input(html_content):
    """
    从 HTML 中提取 <input name="termCode" value="..."> 的值
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    tag = soup.find('input', {'name': 'termCode'})
    if tag and tag.has_attr('value'):
        return tag['value']
    return "UNKNOWN"

def extract_student_info(content):
    """
    从 HTML 中提取学生姓名和学号
    """
    soup = BeautifulSoup(content, 'html.parser')
    # 查找包含学生信息的div标签
    student_info_div = soup.find('div', id='student_name_id')
    if student_info_div:
        # 获取div标签内的文本内容
        student_info_text = student_info_div.get_text(strip=True)

        # 使用正则表达式提取姓名和学号
        # 这个正则表达式假设姓名和学号由 " - " 分隔
        match = re.match(r'^(.*?) - (\d+)$', student_info_text)
        if match:
            name = match.group(1).strip()
            student_id = match.group(2).strip()
            return name, student_id
    
    # 如果无法提取，返回默认值
    return "Unknown", "000000"

def is_valid_html_file(file_obj):
    """
    验证上传的文件是否为有效的HTML文件
    """
    # 检查文件扩展名
    filename = file_obj.name.lower()
    if not filename.endswith('.html'):
        return False, "上传的文件必须是HTML文件(.html扩展名)"
    
    # 读取文件前5KB内容以检查是否为HTML格式
    file_head = file_obj.read(5120)
    file_obj.seek(0)  # 重置文件指针
    
    try:
        # 尝试解析HTML，看是否能创建DOM
        content = file_head.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(content, 'html.parser')
        
        # 检查基本HTML结构
        if not soup.find('html'):
            return False, "上传的文件不是有效的HTML文件"
            
        # 检查是否含有Schedule Builder相关内容
        if not any(keyword in content for keyword in ['UC Davis', 'Schedule Builder', 'CourseDetails']):
            return False, "上传的HTML文件不是UC Davis课表页面"
            
        return True, ""
    except Exception as e:
        return False, f"文件格式错误: {str(e)}"

def remove_temp_directory(directory):
    """直接删除整个临时目录"""
    try:
        # 切换回原始目录以避免删除正在使用的目录
        original_dir = os.getcwd()
        os.chdir(settings.BASE_DIR)
        
        # 直接删除整个目录
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"已删除临时目录: {directory}")
        
        return True
    except Exception as e:
        print(f"删除临时目录时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 确保切回原始目录
        os.chdir(original_dir)

def index(request):
    if request.method == 'POST':
        form = HtmlUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # 获取上传的文件
            html_file = request.FILES['html_file']
            
            # 验证是否为HTML文件
            is_valid, error_message = is_valid_html_file(html_file)
            if not is_valid:
                return render(request, 'converter/error.html', {'error': error_message})
            
            # 创建临时目录，不使用子目录结构
            temp_dir = tempfile.mkdtemp(dir=settings.TEMP_DIR)
            
            # 存储原始工作目录
            current_dir = os.getcwd()
            
            try:
                # 创建uploaded文件夹在main.py同目录
                uploaded_dir = os.path.join(settings.BASE_DIR, 'uploaded')
                os.makedirs(uploaded_dir, exist_ok=True)
                
                # 保存原始HTML文件到临时目录(二进制模式)
                temp_file_path = os.path.join(temp_dir, 'original.html')
                
                with open(temp_file_path, 'wb') as destination:
                    for chunk in html_file.chunks():
                        destination.write(chunk)
                
                # 读取HTML内容为二进制数据
                with open(temp_file_path, 'rb') as f:
                    html_content_bytes = f.read()
                
                # 使用BeautifulSoup解析二进制HTML内容
                soup = BeautifulSoup(html_content_bytes, 'html.parser')
                html_content = str(soup)
                
                # 使用提供的函数提取信息
                term_code = extract_term_code_from_input(html_content)
                name, student_id = extract_student_info(html_content)
                
                # 验证提取的信息是否有效
                if name == "Unknown" or student_id == "000000" or term_code == "UNKNOWN":
                    # 删除临时目录
                    remove_temp_directory(temp_dir)
                    error_details = []
                    if name == "Unknown":
                        error_details.append("学生姓名")
                    if student_id == "000000":
                        error_details.append("学生学号")
                    if term_code == "UNKNOWN":
                        error_details.append("学期代码")
                    
                    error_message = f"无法从上传的HTML文件中提取必要信息: {', '.join(error_details)}"
                    error_message += "。请确认上传的是正确的UC Davis Schedule Builder页面。"
                    return render(request, 'converter/error.html', {'error': error_message})
                
                # 替换文件名中的非法字符
                safe_name = re.sub(r'[\\/*?:"<>|]', "_", name)
                
                # 在控制台明显输出
                print("\n" + "="*50)
                print(f"提取的信息:")
                print(f"学生姓名: {name} (安全文件名: {safe_name})")
                print(f"学生学号: {student_id}")
                print(f"学期代码: {term_code}")
                print(f"临时目录: {temp_dir}")
                print("="*50 + "\n")
                
                # 构建新文件名
                custom_filename = f"{safe_name}_{student_id}_{term_code}.html"
                custom_file_path = os.path.join(temp_dir, custom_filename)
                
                # 复制并重命名文件
                shutil.copy2(temp_file_path, custom_file_path)
                
                # 保存HTML文件到uploaded文件夹
                uploaded_file_path = os.path.join(uploaded_dir, custom_filename)
                shutil.copy2(custom_file_path, uploaded_file_path)
                print(f"已保存HTML文件: {uploaded_file_path}")
                
                # 创建TMP.html用于main.py处理
                tmp_path = os.path.join(temp_dir, 'TMP.html')
                shutil.copy2(custom_file_path, tmp_path)
                
                # 复制main.py到临时目录
                main_py_path = os.path.join(settings.BASE_DIR, 'main.py')
                temp_main_py_path = os.path.join(temp_dir, 'main.py')
                shutil.copy2(main_py_path, temp_main_py_path)
                
                # 切换目录并执行main.py
                os.chdir(temp_dir)
                
                # 执行main.py (使用单独的进程而不是exec)
                # 这样可以避免命名空间冲突和缺少函数的问题
                import subprocess
                result = subprocess.run([sys.executable, temp_main_py_path], 
                                       capture_output=True, 
                                       text=True, 
                                       encoding='utf-8', 
                                       errors='ignore')
                
                # 打印输出以便调试
                print("Main.py 标准输出:")
                print(result.stdout)
                if result.stderr:
                    print("Main.py 错误输出:")
                    print(result.stderr)
                
                # 检查生成的ICS文件
                ics_file_path = os.path.join(temp_dir, 'TMP.html.ics')
                if os.path.exists(ics_file_path):
                    # 重命名ICS文件用于下载，但不保存到uploaded文件夹
                    custom_ics_filename = f"{safe_name}_{student_id}_{term_code}.ics"
                    custom_ics_path = os.path.join(temp_dir, custom_ics_filename)
                    shutil.copy2(ics_file_path, custom_ics_path)
                    
                    # 再次输出信息
                    print("\n" + "="*50)
                    print(f"生成ICS文件成功!")
                    print(f"学生姓名: {name}")
                    print(f"学生学号: {student_id}")
                    print(f"学期代码: {term_code}")
                    print("="*50 + "\n")
                    
                    # 准备文件响应
                    os.chdir(current_dir)
                    
                    # 从临时文件创建响应对象
                    with open(custom_ics_path, 'rb') as ics_file:
                        ics_content = ics_file.read()
                    
                    # 删除整个临时目录
                    remove_temp_directory(temp_dir)
                    
                    # 创建并返回响应
                    response = HttpResponse(ics_content, content_type='text/calendar')
                    response['Content-Disposition'] = f'attachment; filename="{custom_ics_filename}"'
                    return response
                else:
                    os.chdir(current_dir)
                    print("未找到生成的ICS文件")
                    error_message = "未能成功生成ICS文件。"
                    if result.stderr:
                        error_message += f"错误详情: {result.stderr}"
                    
                    # 删除整个临时目录
                    remove_temp_directory(temp_dir)
                    
                    return render(request, 'converter/error.html', {'error': error_message})
            
            except Exception as e:
                print(f"处理过程中出错: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # 确保返回原始目录
                if 'current_dir' in locals():
                    os.chdir(current_dir)
                
                # 删除整个临时目录
                if 'temp_dir' in locals():
                    remove_temp_directory(temp_dir)
                
                return render(request, 'converter/error.html', {'error': f'处理过程中出错: {str(e)}'})
    
    else:
        form = HtmlUploadForm()
        
        # 在GET请求时删除整个temp目录并重新创建
        if os.path.exists(settings.TEMP_DIR):
            remove_temp_directory(settings.TEMP_DIR)
            os.makedirs(settings.TEMP_DIR, exist_ok=True)
    
    return render(request, 'converter/index.html', {'form': form})