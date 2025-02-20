from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from .forms import RegisterForm, ProductForm
from .models import Product, Order
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required
from .forms import OrderForm


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, product__merchant=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, "订单状态已更新")
        return redirect('profile')

    return render(request, 'order_status_modal.html', {'order': order})


@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.buyer = request.user

            # 检查是否是商家购买自己的商品
            if order.buyer == product.merchant:
                messages.error(request, "不能购买自己发布的商品")
            else:
                order.save()
                messages.success(request, "订单提交成功！商家将尽快处理")

                # 重定向到商城主页
                return redirect('home')
    else:
        form = OrderForm(initial={'quantity': 1})

    return render(request, 'product_detail.html', {
        'product': product,
        'form': form
    })



@login_required
@require_POST
def toggle_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        # 验证当前用户是商品所有者
        if product.merchant == request.user:
            product.is_active = not product.is_active
            product.save()
            return JsonResponse({'status': 'success', 'is_active': product.is_active})
        return JsonResponse({'status': 'error', 'message': '权限不足'}, status=403)
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '商品不存在'}, status=404)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_merchant = form.cleaned_data.get('is_merchant')
            user.save()
            return redirect('login')
        else:
            # 表单验证失败，将错误信息传递给模板
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
    else:
        form = RegisterForm()
        error_messages = None  # 初始化错误信息为 None

    return render(request, 'register.html', {'form': form, 'error_messages': error_messages})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')


def home_view(request):
    products = Product.objects.filter(is_active=True)  # 只显示上架商品
    return render(request, 'home.html', {'products': products})


@login_required
@require_POST
def toggle_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        # 验证当前用户是商品所有者
        if product.merchant == request.user:
            product.is_active = not product.is_active
            product.save()
            return JsonResponse({'status': 'success', 'is_active': product.is_active})
        return JsonResponse({'status': 'error', 'message': '权限不足'}, status=403)
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '商品不存在'}, status=404)


@require_POST
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.merchant != request.user:
        return JsonResponse({'status': 'error'}, status=403)

    product.delete()
    return JsonResponse({'status': 'success'})


# views.py
@require_POST
@login_required
def delete_product(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        if product.merchant != request.user:
            return JsonResponse({'status': 'error', 'message': '权限不足'}, status=403)

        product.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def profile_view(request):
    if request.user.is_merchant:
        products = Product.objects.filter(merchant=request.user)
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.merchant = request.user
                product.save()
                return redirect('profile')
        else:
            form = ProductForm()
    else:
        products = None
        form = None

    return render(request, 'profile.html', {
        'form': form,
        'products': products
    })


def logout_view(request):
    logout(request)
    return redirect('login')

# 假设商家个人主页的视图函数
@login_required
def merchant_profile(request):
    if request.user.is_merchant:
        orders = Order.objects.filter(product__merchant=request.user)
        # 预先计算每个订单的总金额
        for order in orders:
            order.total_price = order.product.price * order.quantity

        if request.method == 'POST':
            product_form = ProductForm(request.POST, request.FILES)
            if product_form.is_valid():
                product = product_form.save(commit=False)
                product.merchant = request.user
                product.save()
                messages.success(request, "商品发布成功！")
                return redirect('merchant_profile')
        else:
            product_form = ProductForm()

        products = Product.objects.filter(merchant=request.user)
        return render(request, 'profile.html', {
            'orders': orders,
            'product_form': product_form,
            'products': products
        })
    else:
        messages.error(request, "你不是商家，无法访问此页面")
        return redirect('home')


@login_required
def order_list(request):
    if request.user.is_merchant:
        # 商家可以看到需要发货的订单
        orders = Order.objects.filter(status='pending', product__merchant=request.user)
    else:
        # 用户可以看到自己已经购买的订单
        orders = Order.objects.filter(buyer=request.user)

    return render(request, 'order_list.html', {'orders': orders})
