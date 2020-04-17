from django.shortcuts import render, redirect
from django.views import generic
from .models import ItemFavorite
from accounts.models import CustomUser
from scraping.models import ItemFavorite
import os
import requests
import lxml.html
import lxml
import shutil
import time



# Create your views here.

class IndexView(generic.TemplateView):
    template_name = "index.html"

    def __init__(self):
        self.site_url_yahoo = "https://shopping.yahoo.co.jp/search" #yahoo shoppingサイトの検索(searchを付けること)
        self.site_url_rekuten = "https://search.rakuten.co.jp/search/mall/"

        self.item_name = ""
        self.item_status = "0"  # 0=指定なし 1=新品　2=中古
        self.item_order = "0"  # 0=指定なし　1=安い順

    #メイン処理　クラスビューで呼び出された場合はget()が呼び出される　→　get()をオーバーライドすること
    def get(self, request, *args, **kwargs):
        
        #サイトへの1回目の訪問時に商品名の入力がないとプログラムが動かないためtry文で処理する
        try:
            self.item_name = request.GET.get("item_name")
        except:
            pass
        #ユーザーがログインしていない場合はログイン画面にリダイレクトさせる
        if request.user.is_authenticated:
            user_id = request.user.id
            pass
        else:
            return redirect("home")

        if self.item_name:
            self.item_name = request.GET.get("item_name")  # 検索窓に入力された商品名を取り出す
            self.item_status = request.GET.get("status")  # ラジオボタンから選択肢を取得
            self.item_order = request.GET.get("order")
            if self.item_status == None:
                self.item_status = "0"
            if self.item_order == None:
                self.item_order = "0"
            
            # リストの形式で返されるので下記のように値を取り出す

            yahoo_list = self.search_yahoo_item_and_create_list(self.item_name, user_id)  # 商品を検索及び商品リストを作成(yahoo)
            rakuten_list = self.search_rakuten_item_and_create_list(self.item_name, user_id)  # 商品検索及び商品のリストを作成(楽天)
            yahoo_and_rakuten_item_list = []
            for i in range(5):
                tmp_yahoo_and_rakuten_list = []
                tmp_yahoo_and_rakuten_list.append(yahoo_list[i])
                tmp_yahoo_and_rakuten_list.append(rakuten_list[i])
                yahoo_and_rakuten_item_list.append(tmp_yahoo_and_rakuten_list)
        
            context = {
                'yahoo_item_list': yahoo_list,
                'rakuten_item_list': rakuten_list,
                'yahoo_and_rakuten_item_list': yahoo_and_rakuten_item_list,
                'item_name': self.item_name,
            }
        
        else:
            context = {
                'item_name': self.item_name,
                'yahoo_item_list': None,
                'rakuten_item_list': None,
            }
        return render(request, 'scraping/index.html', context)

    #user_idは商品をデータベースに保存する際に一意にするためのもの　同時刻に他のユーザー同士で検索をかけてしまうとIDが被る可能性あり
    def search_yahoo_item_and_create_list(self, item_name, user_id):
        """商品検索及びリスト作成"""
        if self.item_status == "1":  # 新品ならば
            yahoo_item_status = "2"
        elif self.item_status == "2":  # 中古ならば
            yahoo_item_status = "1"
        else:
            yahoo_item_status = "0"

        req = requests.get(self.site_url_yahoo, params={'p': item_name, 'used': yahoo_item_status})
        html_yahoo = lxml.html.fromstring(req.text)
        
        tmp_item_name_object_list = html_yahoo.xpath("//a[@class='_2EW-04-9Eayr']/span")  # 商品名
        tmp_item_value_object_list = html_yahoo.xpath("//span[@class='_3-CgJZLU91dR']")  # 値段
        tmp_item_point_percentage_object_list = html_yahoo.xpath("//span[@class='VppfHNxe1EAG']")  # ポイント「値引き率(文字列)」 値のみ取り出される
        tmp_item_img_src_object_list = html_yahoo.xpath("//img[@class='_2j-qvZxp4nZn']")  # 写真のソースURLリスト
        # 商品の詳細リンク先のリスト
        tmp_item_details_link_object_list = html_yahoo.xpath("//a[@class='_2EW-04-9Eayr']")
        
        yahoo_img_src_list = [tmp_item_img_src_object_list[n].attrib["src"] for n in range(5)] #５つ分の画像のソースURLを取り出す

        #商品名を取得する際のタグが<span>が二つに分かれている場合があるためもう一度取得しておく
        #通常の場合は<span>商品名</span>
        #この場合があるため→<span></span><span>商品名</span>
        try:
            tmp_item_name_object_list_2 = html_yahoo.xpath("//a[@class='_2EW-04-9Eayr']/span[2]")  # 商品名
        except:
            pass


        # 商品の画像URLリストを渡して、画像を保存する処理
        item_img_path_list = self.download_item_image_and_create_path_list("yahoo", yahoo_img_src_list)

        #ポイント適用後の価格を計算する処理を記述すること

        yahoo_item_list = [] #[index, ,商品名, 価格, ポイント, ポイント適用後の価格, 商品画像, 商品詳細ページへのリンクURL])
        now = str(time.time()).replace(".","") #indexを作成するため　現在時刻と商品名からindexを作成する
        count = 1
        item_name_offset = 0 #商品名が取得できていない場合にもう一方のリストより取得するためのもの
        for n in range(5): #
            tmp_item_list = []
            index = now + "_yahoo_" + str(count)
            tmp_item_list.append(index) #index
            if tmp_item_name_object_list[n].text == None: #←←←ここ少しぎっくりした
                tmp_item_list.append(tmp_item_name_object_list_2[item_name_offset].text)
                item_name_offset += 1
            else:
                tmp_item_list.append(tmp_item_name_object_list[n].text) #商品名
            
            value = int(tmp_item_value_object_list[n].text.replace(",", "")) #価格
            point_percentage  = int(tmp_item_point_percentage_object_list[n].text) #ポイントのパーセンテージ
            point = value * point_percentage // 100 #ポイント
            value_after_discount = value - point #割引き後価格(値段からパーセンテージを差し引いた価格)
            value_after_discount = "{:,}".format(value_after_discount)
            tmp_item_list.append(tmp_item_value_object_list[n].text)
            tmp_item_list.append(point)
            tmp_item_list.append(value_after_discount) 
            tmp_item_list.append(item_img_path_list[n]) #商品画像(ローカルのパス)
            tmp_item_list.append(tmp_item_details_link_object_list[n].attrib["href"]) #商品詳細ページ
            #tmp_item_list.append(tmp_item_details_link_object_list[n]["href"]) #商品詳細ページ
            yahoo_item_list.append(tmp_item_list)

            count += 1


        
        return yahoo_item_list

    #user_idは商品をデータベースに保存する際に一意にするためのもの　同時刻に他のユーザー同士で検索をかけてしまうとIDが被る可能性あり
    def search_rakuten_item_and_create_list(self, item_name, user_id):
        """商品検索及びリスト作成"""
        if self.item_status == "1":  # 新品ならば
            rakuten_item_status = "0"
        elif self.item_status == "2":  # 中古ならば
            rakuten_item_status = "1"
        else:
            rakuten_item_status = "0"

        req = requests.get(self.site_url_rekuten + item_name , params={'used': rakuten_item_status})
        html_rakuten = lxml.html.fromstring(req.text)

        tmp_item_name_and_link_object_list = html_rakuten.xpath("//div[@class='dui-card searchresultitem']/div[@class='content title']/h2/a") #商品名及び、商品詳細リンク先
        tmp_item_img_src_object_list = html_rakuten.xpath("//div[@class='dui-card searchresultitem']/div[@class='image']/a/img")              #商品画像
        tmp_item_value_object_list = html_rakuten.xpath("//div[@class='content description price']/span[@class='important']")                 #商品価格
        tmp_item_point_object_list = html_rakuten.xpath("//div[@class='dui-card searchresultitem']/div[@class='content points']/span")        #ポイント()

        tmp_item_img_src_list = [] #商品の画像URLのリスト
        for i in range(5):
            tmp_item_img_src_list.append(tmp_item_img_src_object_list[i].attrib['src']) #調整

        rakuten_img_path_list = self.download_item_image_and_create_path_list('rakuten', tmp_item_img_src_list) #楽天のimgの保管場所(ローカル) ローカルに保存後アプリで表示させる

        rakuten_item_list = [] #index, 商品名, 価格, ポイント, ポイント適用後の価格, 商品画像, 商品詳細ページへのリンクURL)

        now = str(time.time()).replace(".", "")
        count = 1

        for n in range(5):
            tmp_item_list = [] 
            tmp_item_list.append(n+1)
            tmp_item_list.append(tmp_item_name_and_link_object_list[n].text)  #商品名
            value = int(tmp_item_value_object_list[n].text.replace(",", ""))
            point = int(tmp_item_point_object_list[n].text.split('ポイント')[0].replace(",",""))
            discount_value = value - point
            discount_value = "{:,}".format(discount_value)
            tmp_item_list.append(tmp_item_value_object_list[n].text)                                                # 価格
            tmp_item_list.append(point)                                                # ポイント
            tmp_item_list.append(discount_value) #割引き後価格
            tmp_item_list.append(rakuten_img_path_list[n])                                #商品画像 () 
            tmp_item_list.append(tmp_item_name_and_link_object_list[n].attrib['href']) #商品詳細リンク
            rakuten_item_list.append(tmp_item_list)
            print(discount_value)
        
        return rakuten_item_list


    #商品画像をダウンロード、及び、保存先のローカルのパスのリストを作成(サイトには一旦ローカルに保存して表示させる)
    def download_item_image_and_create_path_list(self, site_name, img_src_url_list):
        count = 0
        img_path_list = []
        for img_src_url in img_src_url_list:
            res = requests.get(img_src_url, stream=True)
            count += 1
            now = str(time.time()).replace('.', '')
            item_path = "media/tmp_images/" + site_name + "_" + now + "_" + "{}.png".format(count) #ローカル環境の保存先のpath
            img_path_list.append(item_path)
            with open(item_path, "wb") as f:
                shutil.copyfileobj(res.raw, f)
            if count == 5:
                break
        return img_path_list

    
#商品のお気に入り登録
def favorite_item_register(request):
    try:
        if request.method == "GET":
            return redirect("home")

        favorite_item_id = request.POST.get("favorite_item_id")
        favorite_item_name = request.POST.get("favorite_item_name")
        favorite_item_link = request.POST.get("favorite_item_link")
        favorite_item_image_url = request.POST.get("favorite_item_image")
        new_favorite_item_image_directory_path = "media/favorite_images/" #実際のデータを取り出してデータベースに格納するには？
        favorite_item_value = request.POST.get("favorite_item_value")
        

        #永続的に保存するディレクトリにコピーする(データベースから参照するために保存するためのディレクトリ)　※tmp_imageディレクトリ内は一定時間後に削除する　
        
        #ユーザーのIDをデータベースから引っ張ってくる　※名前で登録しても良いのだ 
        if request.user != "AnonymousUser":
            user_object = CustomUser.objects.get(username=request.user)

        #print(type(user_object), type(user_name), type(request.user))　←ハマったところ

        image_file_name = favorite_item_image_url.replace('media/tmp_images/','') #画像ファイルの名前をパスから取り出す
        #もし同じ商品をお気に入りに登録していた場合は警告を出して登録できないようにする
        


        #データベースへお気に入り商品のデータを登録(画像はパスを保存する)
        favorite_item = ItemFavorite(
            item_id = image_file_name, #画像を検索するためのインデックス
            username = user_object.username, #CustomUserのインスタンスを与えないといけない　ユーザー名をデータベースから取り出していれる
            item_name = favorite_item_name,
            item_image_path = new_favorite_item_image_directory_path + image_file_name, #永続的な保存先のパス
            item_link_url = favorite_item_link,
            item_value = favorite_item_value
        )
        registered_item_list = ItemFavorite.objects.filter(username=user_object.username) #request.user等では型が違うためフィルターにかからないため気を付ける
        try:
            registered_item_list = ItemFavorite.objects.filter(username=user_object.username) #request.user等では型が違うためフィルターにかからないため気を付ける
        except:
            registered_item_list = None

        #商品が既にお気に入りに登録されているかを確かめる処理　
        
        try:
            item_objects = ItemFavorite.objects.get(item_id=image_file_name)        
            item_exist_flag = 1
            
        except:
            item_exist_flag = 0

        #既にお気に入りに登録されている場合の処理
        if item_exist_flag == 1:
            warning_sentence = "既にお気に入りに登録されています"
            context = {
                "warning_sentence": warning_sentence,
                "registered_item_list": registered_item_list,
            }
            return render(request, 'account/home.html', context)

        #新規でお気に入りに登録する
        else:
            #画層ファイルを保存するためのフォルダにコピーする処理　一定時間後に元の一時的に保存するためのフォルダ内の画像ファイルを削除するため
            shutil.copy(favorite_item_image_url, new_favorite_item_image_directory_path)
            image_file_name = favorite_item_image_url.replace('media/tmp_images/','') #画像ファイルの名前をパスから取り出す

            favorite_item.save()
            
            context = {
                "favorite_item_name" : favorite_item_name, #登録をしようとしている商品名
                "registered_item_list" : registered_item_list, #お気に入りに登録している商品一覧
            }
            
            return render(request, 'account/home.html', context)
    except:
        return redirect("home")

#商品お気に入り削除　(アカウントのviewに書くべきか悩む)
def favorite_item_delete(request):
    try:
        #単にアクセスしてきたならリダイレクトさせる
        if request.method == 'GET':
            return redirect("home")
        username = request.user

        delete_item_id = request.POST.get("item_id") #リクエストの中から対象のIDを取得する　データベースから削除する際に使用
        delete_item_name = request.POST.get("item_name") #サーバーから削除する際に使用　使用しなくても良いか

        #関連される画像を削除する処理 (実際の保存場所から)
        delete_item_object = ItemFavorite.objects.get(item_id=delete_item_id)
        delete_item_image_path = delete_item_object.item_image_path #サーバーでの画像ファイルの保存先パス
        delete_item_name = delete_item_object.item_name #削除する商品名　javascriptでポップアップでも出そうか

        #削除したい商品を商品IDを元にデータベースから削除する処理
        ItemFavorite.objects.filter(item_id=delete_item_id).delete() 
        

        os.remove(delete_item_image_path)
        
        #ユーザーのお気に入り登録済みの商品一覧を取得　空ならばNoneを返す
        try:
            registered_item_list = ItemFavorite.objects.filter(username=username)
        except:
            registered_item_list = None
        
        context = {
            "registered_item_list" : registered_item_list,
        }
        

        return render(request, 'account/home.html', context)
    except:
        return redirect("home")

