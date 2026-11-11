import random

from django.core.management.base import BaseCommand

from products.models import Category, Product


class Command(BaseCommand):
    help = 'ساخت دسته‌بندی و محصولات تستی'

    def handle(self, *args, **options):
        data = {
            'electronics': ('لوازم الکترونیکی', ['هدفون', 'موبایل', 'لپ‌تاپ', 'ساعت هوشمند', 'پاوربانک']),
            'clothing': ('پوشاک', ['تی‌شرت', 'شلوار جین', 'کاپشن', 'کفش ورزشی', 'کلاه']),
            'books': ('کتاب', ['رمان', 'کتاب برنامه‌نویسی', 'کتاب تاریخ', 'مجله']),
        }

        created = 0
        for slug, (cat_name, products) in data.items():
            category, _ = Category.objects.get_or_create(
                slug=slug, defaults={'name': cat_name}
            )
            for i, name in enumerate(products, start=1):
                _, was_created = Product.objects.get_or_create(
                    slug=f'{slug}-{i}',
                    defaults={
                        'name': name,
                        'category': category,
                        'description': f'توضیحات تستی برای {name}',
                        'price': random.randint(50, 5000) * 1000,
                        'stock': random.randint(0, 50),
                    },
                )
                created += was_created

        self.stdout.write(self.style.SUCCESS(f'{created} محصول جدید ساخته شد.'))