from django.shortcuts import render
from django.views import generic
import requests
import lxml
import lxml


# Create your views here.

class IndexView(generic, TemplateView):
    template_name = "index.html"

    def __init__(self):
        self.site_url_yahoo = "https://shopping.yahoo.co.jp/search" #yahoo shoppingサイトの検索(searchを付けること)
        self.site_url_rekuten = "https://search.rakuten.co.jp/search/mall/"

        self.item_name = ""
        self.item_status = "0"  # 0=指定なし 1=新品　2=中古
        self.item_order = "0"  # 0=指定なし　1=安い順

    def get(self, request, *args, **kwargs):
        #メイン処理
        #サイトへの1回目の訪問時に商品名の入力がないとプログラムが動かないためtry文で処理する
        try:
            self.item_name = request.GET.get("item_name")
        except:
            pass

        if self.item_name:
            self.item_name = request.GET.get("item_name")  # 検索窓に入力された商品名を取り出す
            self.item_status = request.GET.get("status")  # ラジオボタンから選択肢を取得
            self.item_order = request.GET.get("order")

            # リストの形式で返されるので下記のように値を取り出す

            self.search_yahoo_item_and_create_list(self.item_name)  # 商品を検索及び商品リストを作成(yahoo)
            self.search_rakuten_item_and_create_list(self.item_name)  # 商品検索及び商品のリストを作成(楽天)



    def search_yahoo_item_and_create_list(self, item_name):
        """商品検索及びリスト作成"""
        if self.item_status = "1":  # 新品ならば
            yahoo_item_status = "2"
        elif self.item_order = "2":  # 中古ならば
            yahoo_item_status = "1"

        req = requests.get(self.site_url_yahoo, params={'p': item_name, 'used': yahoo_item_status})
        html_yahoo = lxml.html.fromstring(req.text)

        tmp_item_name_object_list = html_yahoo.xpath("//a[@class='_2EW-04-9Eayr']/span")  # 商品名
        tmp_item_value_object_list = html_yahoo.xpath("//span[@class='_3-CgJZLU91dR']")  # 値段
        tmp_item_point_percentage_object_list = html_yahoo.xpath("//span[@class='VppfHNxe1EAG']")  # ポイント「値引き率(文字列)」 値のみ取り出される
        tmp_item_img_src_object_list = html_yahoo.xpath("//img[@class='_2j-qvZxp4nZn']")  # 写真のソースURLリスト
        # 商品の詳細リンク先のリスト
        tmp_item_details_link_object_list = html_yahoo.xpath("//a[@class='_2EW-04-9Eayr']")
        
        yahoo_img_src_list = [tmp_item_img_src_object_list[n].attrib["src"] for n in range(5)] #５つ分の画像のソースURLを取り出す

        # 商品の画像URLリストを渡して、画像を保存する処理
        item_img_path_list = download_item_image_and_create_path_list("yahoo", yahoo_img_src_list)

        #ポイント適用後の価格を計算する処理を記述すること

        yahoo_item_list = [] #index, ,商品名, 価格, ポイント, ポイント適用後の価格, 商品画像, 商品詳細ページへのリンクURL)
        index = 1
        for n in range(5): #
            tmp_item_list = []
            tmp_item_list.append(index) #index
            tmp_item_list.append(tmp_item_name_object_list[n].text) #商品名
            value = int(tmp_item_value_object_list[n].text.replace(",", "")) #価格
            point_percentage  = int(tmp_item_point_percentage_object_list[n].text) #ポイント
            value_after_discount = value * (100 - point_percentage) #割引き後価格
            
            tmp_item_list.append(value)
            tmp_item_list.append(point_percentage)
            tmp_item_list.append(value_after_discount) 
            tmp_item_list.append(item_img_path_list[n]) #商品画像(ローカルのパス)
            tmp_item_list.append(tmp_item_details_link_object_list[n]["href"]) #商品詳細ページ
            yahoo_item_list.append(tmp_item_list)
        
        return yahoo_item_list


    def search_rakuten_item_and_create_list(self, item_name):
        """商品検索及びリスト作成"""
        if self.item_status = "1":  # 新品ならば
            rakuten_item_status = "0"
        elif self.item_order = "2":  # 中古ならば
            rakuten_item_status = "1"

        req = requests.get(self.site_url_rekuten + item_name , params={'used': rakuten_item_status})
        html_rakuten = lxml.html.fromstring(req.text)

        tmp_item_name_and_link_object_list = html_rakuten.xpath("//div[@class='dui-card searchresultitem']/div[@class='content title']/h2/a") #商品名及び、商品詳細リンク先
        tmp_item_img_src_object_list = html_raluten.xpath("//div[@class='dui-card searchresultitem']/div[@class='image']/a/img")              #商品画像
        tmp_item_value_object_list = html_rakuten.xpath("//div[@class='content description price']/span[@class='important']")                 #商品価格
        tmp_item_point_object_list = html_rakuten.xpath("//div[@class='dui-card searchresultitem']/div[@class='content points']/span")        #ポイント()

        tmp_item_img_src_list = [] #商品の画像URLのリスト
        for i in range(5):
            tmp_item_img_src_list.append(tmp_item_img_src_object_list[i].attrib['src'])　#調整

        rakuten_img_path_list = download_item_image_and_create_path_list('rakuten', tmp_item_img_src_list) #楽天のimgの保管場所(ローカル) ローカルに保存後アプリで表示させる

        rakuten_item_list = [] #index, 商品名, 価格, ポイント, ポイント適用後の価格, 商品画像, 商品詳細ページへのリンクURL)

        for n in range(5):
            tmp_item_list = [] 
            tmp_item_list.append(n+1)
            tmp_item_list.append(tmp_item_name_and_link_list[n].text)  #商品名
            value = int(tmp_item_value_object_list[0].text.replace(",", ""))
            point = int(tmp_item_point_object_list[0].text.split('ポイント')[0])
            discount_value = value - point
            tmp_item_list.append(value)                                                # 価格
            tmp_item_list.append(point)                                                # ポイント
            tmp_item_list.append(discount_value) #割引き後価格
            tmp_item_list.append(rakuten_img_path_list)                                #商品画像 () 
            tmp_item_list.append(tmp_item_name_and_link_object_list[n].attrib['href']) #商品詳細リンク
            rakuten_item_list.append(tmp_item_list)


    #商品画像をダウンロード、及び、保存先のローカルのパスのリストを作成(サイトには一旦ローカルに保存して表示させる)
    def download_item_image_and_create_path_list(self, site_name, item_src_url_list):
        count = 0
        img_path_list = []
        for img_src_url in img_src_url_list:
            res = requests.get(img_src_url, stream=True)
            count += 1
            item_path = "media/tmp_images/" + site_name + "_" + "{}.png".format(count) #ローカル環境の保存先のpath
            img_path_list.append(item_path)
            with open(item_url, "wb") as f:
                shutil.copyfileobj(res.raw, f)
            if count == 5:
                break
        return img_path_list

    
