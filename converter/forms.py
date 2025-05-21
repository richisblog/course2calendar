from django import forms

class HtmlUploadForm(forms.Form):
    html_file = forms.FileField(
        label='上传课表HTML文件',
        help_text='请上传从UC Davis课表系统导出的HTML文件',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    ) 