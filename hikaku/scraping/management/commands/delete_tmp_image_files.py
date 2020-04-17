from django.core.management.base import BaseCommand
import shutil
import os


class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'This is Batch that delete image files'

    # コマンドが実行された際に呼ばれるメソッド handleメソッドが呼び出される
    def handle(self, *args, **options):
        shutil.rmtree('media/tmp_images')
        os.mkdir('media/tmp_images')