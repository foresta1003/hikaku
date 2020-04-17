from django.db import models
from accounts.models import CustomUser

# Create your models here.

class ItemFavorite(models.Model):
    class Meta:
        verbose_name_plural = "お気に入り商品"

    #ユーザー名を使用してユーザーが登録しているお気に入り商品を取り出す
    username = models.CharField(verbose_name="ユーザー名", max_length=50)
    item_id = models.CharField(verbose_name='商品のインデックス', max_length=100) #商品を検索するためのインデックス   
    item_name = models.CharField(verbose_name='商品名', max_length=200)
    item_image_path = models.CharField(verbose_name='商品画像の保存パス', max_length=100)
    item_link_url = models.CharField(verbose_name='商品リンク先', max_length=200)
    item_value = models.CharField(verbose_name='商品価格[ポイント適用後]', max_length=20)

    def __str__(self):
        return self.username
