from django.shortcuts import render

def request(home):
    return render(template/home.html)

def request(product_list):
    return render(template/product_list.html)

def request(product_detail):
    return render(template/product_detail.html)

def request(cart):
    return render(template/cart.html)

def request(checkout):
    return render(template/checkout.html)

def request(login):
    return render(template/login.html)



