from django.contrib import admin
from django.contrib import messages
from .models import (
    Product,
    FavoriteProduct,
    ListOfFavorites,
    Group,
    Category,
    SubCategory,
    ClassProduct,
    TypeInCategory,
    ProductType,
    PickUpAddressForProduct,
    TagsForProduct,
    BestProduct,
    ImgProduct)


class ProductTypeInline(admin.TabularInline):
    model = ProductType


class TagsForProductInline(admin.TabularInline):
    model = TagsForProduct


class PickUpAddressForProductInline(admin.TabularInline):
    model = PickUpAddressForProduct


class ClassProductInline(admin.TabularInline):
    model = ClassProduct


class ImgProductInline(admin.TabularInline):
    model = ImgProduct


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'created_at', 'mark_deleted', 'owner', 'number_of_packages', 'weight_of_pack', 'subcat', 'cat', 'gr']
    inlines = [ProductTypeInline, ClassProductInline, TagsForProductInline, PickUpAddressForProductInline, ImgProductInline]
    description = "DESCRIPTION!!1!"

    def owner(self, obj):
        return obj.profile_business.profile
    def subcat(self, obj):
        return obj.category.id
    def cat(self, obj):
        return obj.category.parent.id
    def gr(self, obj):
        return obj.category.parent.parent.id


@admin.register(ImgProduct)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'avatar']


@admin.register(PickUpAddressForProduct)
class PickUpAddressForProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_id', 'address_id']


@admin.register(FavoriteProduct)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'created']


@admin.register(ListOfFavorites)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created']


class SubCategoryInline(admin.TabularInline):
    model = SubCategory


class CategoryInline(admin.TabularInline):
    model = Category


class TypeInCategoryInline(admin.TabularInline):
    model = TypeInCategory


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = [CategoryInline, ]
    list_display = ['id', 'slug', 'name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubCategoryInline, TypeInCategoryInline, ]
    list_display = ['id', 'slug', 'category', 'group']

    def category(self, obj):
        return obj

    def group(self, obj):
        return obj.parent

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug', 'subcategory', 'category', 'group']

    def subcategory(self, obj):
        return obj.name

    def category(self, obj):
        return obj.parent

    def group(self, obj):
        return obj.parent.parent


@admin.register(TypeInCategory)
class TypeInCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category']


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(BestProduct)
class BestProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller', 'product']









