# Generated by Django 3.2.6 on 2021-11-06 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0002_remove_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientsTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('price', models.IntegerField(blank=True, null=True)),
                ('sold', models.IntegerField(blank=True, default=0, null=True)),
                ('instruction', models.TextField(blank=True, null=True)),
                ('origin', models.CharField(blank=True, max_length=50, null=True)),
                ('IsActive', models.BooleanField(default=True)),
                ('IsFlashsale', models.BooleanField(default=False)),
                ('priceSale', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(default=None, upload_to='media')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='avt',
            field=models.ImageField(default='logo-uit.png', upload_to='avt'),
        ),
        migrations.AddField(
            model_name='user',
            name='dateofbirth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='orders',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='sex',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dayandtime', models.DateTimeField(auto_now_add=True)),
                ('ratingpoint', models.IntegerField(blank=True, null=True)),
                ('ratingcomment', models.TextField(blank=True, null=True)),
                ('img', models.ImageField(default=None, upload_to='static')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ecommerce.productcategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(blank=True, to='ecommerce.ProductImage'),
        ),
        migrations.CreateModel(
            name='LoveList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.product')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('levelOfSave', models.IntegerField(blank=True, null=True)),
                ('Description', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('Tag', models.ManyToManyField(blank=True, to='ecommerce.IngredientsTag')),
            ],
        ),
    ]
