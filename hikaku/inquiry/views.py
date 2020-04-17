from django.shortcuts import render

# Create your views here.

#自己紹介のページを作成
def self_introduction(request):
    context ={}
    return render(request, 'inquiry/self_introduction.html', context)