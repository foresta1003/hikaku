from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    """拡張ユーザーモデル"""
    #verbose_name_pluralは管理サイトの画面でわかりやすく表示させるためのもの、指定した名前でモデルを表示する
    class Meta:
        verbose_name_plural = "CustomUser"
    
    user_name = models.CharField(verbose_name='ユーザー名', max_length=30)
    full_name = models.CharField('指名', max_length=20, blank=True)
    email = models.EmailField(verbose_name='email_address')
    department = models.CharField(verbose_name='所属', max_length=30)
    update_time = models.DateField(verbose_name='更新日時', auto_now=True)
    create_time = models.DateField(verbose_name='作成日時', auto_now_add=True)

    def __str__(self):
        return self.user_name

#検索履歴の保存機能
