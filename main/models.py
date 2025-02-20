from django.core.validators import FileExtensionValidator
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    is_merchant = models.BooleanField(default=False)
    email = models.EmailField(unique=True)


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to='products/',
        default='products/default_product.png',  # 添加默认值
        verbose_name='商品图片'
    )
    merchant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=100, verbose_name="姓名")  # 确保这里的 name 字段存在
    phone = models.CharField(max_length=20, verbose_name="联系电话")
    address = models.TextField(verbose_name="收货地址")
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.product.name} - {self.buyer.username}"
