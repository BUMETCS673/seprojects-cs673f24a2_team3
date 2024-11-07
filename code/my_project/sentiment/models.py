from django.db import models

class UserText(models.Model):
    content = models.TextField()  # 存储用户输入的文本
    created_at = models.DateTimeField(auto_now_add=True)  # 自动记录创建时间

    def __str__(self):
        return self.content[:50]  # 显示前50个字符
