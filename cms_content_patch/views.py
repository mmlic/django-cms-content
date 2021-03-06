# -*- coding: utf-8 -*-
from datetime import datetime
from django.http import HttpResponseRedirect
from django.db.models import F
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import get_list_or_404
from django.template.context import RequestContext
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from django.core.paginator import EmptyPage
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext_lazy as _
from cms_content.models import *
from cms_content.utils.render import render_to
#from cms_content.utils.cache import cache_nodes
#from cms_content.menu_nodes import cache_nodes
from cms_content.forms import CMSArticleFrontendForm
from cms_content.settings import ROOT_URL
from cms_content.settings import ARTICLE_PERPAGE


#@cache_page(60*30)
@render_to('cms_content/content_index.html')
def content_index(request):
    articles = list(CMSArticle.pub_manager.all()[:10])
    return {
        'articles': articles,
    }

@cache_page(24*60*60)
@render_to('cms_content/section_list.html')
def section_list(request):
    sections = list(CMSSection.objects.all())
    return {
        'sections': sections,
    }

@cache_page(24*60*60)
@render_to('cms_content/section_detail.html')
def section_detail(request, slug):
    section = CMSSection.objects.get(slug=slug)
    categories = CMSCategory.objects.select_related(depth=1).filter(section=section)
    return {
        'section': section,
        'categories': categories,
    }

#@cache_page(60*30)
@render_to('cms_content/article_list.html')
def category_detail(request, slug):
    """View of list articles of category with name slug
    
    """
    category = CMSCategory.objects.select_related(depth=1).get(slug=slug)
    articles = CMSArticle.pub_manager.select_related(depth=1).filter(category=category)
    paginator = Paginator(articles, ARTICLE_PERPAGE)
    try:
        request_page = int(request.GET.get('page', 1))
    except ValueError:
        request_page = 1
    try:
        article_page = paginator.page(request_page)
        queryset = articles[(request_page-1)*ARTICLE_PERPAGE:request_page*ARTICLE_PERPAGE]
    except (EmptyPage, InvalidPage):
        article_page = paginator.page(paginator.num_pages)
        queryset = articles[(paginator.num_pages-1)*ARTICLE_PERPAGE:paginator.num_pages*ARTICLE_PERPAGE]
    #cache_nodes(request, queryset)
    return {
        'pages': article_page,
        #'paginator': paginator,
        #'request_page': request_page,
        'section': category.section,
        'category': category,
        'articles': queryset,
    }
    
#@cache_page(60*30)
@render_to('cms_content/article_list.html')
def article_list(request, slug):
    """Display articles in a named slug's category. 
    
    """
    category = CMSCategory.objects.select_related(depth=1).get(slug=slug)
    articles = CMSArticle.pub_manager.select_related(depth=1).filter(category=category)
    return {
        'category': category,
        'articles': articles,
        'per_page': ARTICLE_PERPAGE,
    }

@render_to('cms_content/article_detail.html')
def article_detail(request, year, month, day, slug):
    article = CMSArticle.pub_manager.select_related(depth=2).get(slug=slug)
    article.hits += 1
    article.save()
    article_tags = article.tags.select_related().all()
    #cache_nodes(request, article.slug)
    return {
        'section': article.category.section,
        'category': article.category,
        'article': article,
        'article_tags': article_tags,
        'hits': article.hits,
    }

@login_required
@render_to('cms_content/article_add.html')
def article_add(request):
    if request.method=="POST":
        form = CMSArticleFrontendForm(request.POST)
        if form.is_valid():
            menu_count = CMSMenuID.objects.count() + 1
            category = form.cleaned_data['category']
            cate = CMSCategory.objects.get(name=category)
            menu = CMSMenuID.objects.create(menuid=menu_count, parent=cate.menu.menuid)
            article = CMSArticle.objects.create(
                title = form.cleaned_data['title'],
                content = form.cleaned_data['content'], 
                slug = form.cleaned_data['slug'], 
                category = category,
                created_by = request.user,
                created_date = datetime.now(),
                last_modified_by = request.user,
                last_modified_date = datetime.now(),
                pub_status = 'pub',
                menu = menu,
            )
            article.save()
        else:
            from django.core.exceptions import ValidationError
            raise ValidationError('Error')
        return HttpResponseRedirect(ROOT_URL)
    else:
        article_form = CMSArticleFrontendForm(
            initial={'title':'your article title'},
        )
        return {
            'form': article_form,
            'request': request,
        }

def article_del(request, slug, path, name):
    if request.user.is_superuser:
        article = CMSArticle.objects.get(slug=name)
        article.delete()
        return HttpResponseRedirect(ROOT_URL)

@render_to('cms_content/article_by_tag.html')
def article_by_tag(request, tag):
    articles = CMSArticle.pub_manager.filter(tags__in=[tag])
    return {
        'articles': articles,
        'tag': tag,
    }
