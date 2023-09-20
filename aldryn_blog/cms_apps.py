# -*- coding: utf-8 -*-
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _
from aldryn_blog.cms_menus import BlogCategoryMenu


class BlogApp(CMSApp):
    name = _('Blog')
    app_name = 'aldryn_blog'
    menus = [BlogCategoryMenu]

    def get_urls(self, page=None, language=None, **kwargs):
        return ['aldryn_blog.urls']


apphook_pool.register(BlogApp)
