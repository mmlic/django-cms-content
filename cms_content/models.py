# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.signals import comment_was_posted
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from cms_content.settings import ROOT_URL
from cms_content.settings import UPLOAD_TO
from cms_content.manager import CMSArticlePubManager


__all__ = [
    'CMSMenuID',
    'CMSSection',
    'CMSCategory',
    'CMSArticle',
]

class CMSMenuID(models.Model):
    """All CMS_Content object's menu id for django-cms get_nodes"""
    menuid = models.IntegerField(blank=False, null=False)
    parent = models.IntegerField(blank=True, null=True)
    type = models.CharField(blank=False, null=False, max_length=20)
    
    class Meta:
        verbose_name = _(u'Menu ID')
        verbose_name_plural = _(u'Menu ID')

    def menu_entry(self):
        """show the entry of the menu's url"""
        if self.parent is None:
            return "<a href='%s'>%s</a>" % (self.cmssection.url, self.cmssection)
        if self.type == 'cmscategory':
            return self.cmscategory.url
        return self.cmsarticle.url


class CMSSection(models.Model):
    """Models For Django CMS Sections:

    Section is the top level to contruct cms's content. Create a section before 
    adding your categories.
    """

    name = models.CharField(
        _(u"Section Name"),
        max_length=255,
        blank=False,
        help_text=_(u"Section's Name"),
    )
    slug = models.SlugField(
        _(u"Slug"),
        max_length=255,
        blank=False,
        unique=True,
        help_text=_(u"Section's Slug"),
    )
    description = models.TextField(
        _(u"Section Description"),
        blank=False,
        help_text=_(u"Your Section's Description"),
    )
    image = models.ImageField(
        _(u"Image"),
        upload_to=UPLOAD_TO,
        blank=True,
        help_text=_(u"Section Image Displayed In Pages"),
    )
    created_date = models.DateTimeField(
        _(u"Create Time"),
        auto_now_add=True,
    )
    menu = models.OneToOneField(CMSMenuID)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-created_date']
        verbose_name = _(u'Section')
        verbose_name_plural = _(u'Section')

    @property
    def url(self):
        return "%s%s/%s/" % (ROOT_URL, 'section', self.slug)
    
    @models.permalink
    def get_absolute_url(self):
        return ('cms_content_section_detail', (self.slug,))


class CMSCategory(models.Model):
    """Models for CMS's Categories:

    Category is the second level of cms_content structure. Before publish any
    articles, you should create a category.
    """

    name = models.CharField(
        _(u"Category Name"),
        max_length=255,
        blank=False,
        help_text=_(u"Category's Name"),
    )
    slug = models.SlugField(
        _(u"Slug"),
        max_length=255,
        blank=False,
        unique=True,
        help_text=_(u"Category's Slug"),
    )
    section = models.ForeignKey(
        CMSSection,
        verbose_name=_(u"Section"),
        related_name="category_of_section",
        blank=False,
        help_text=_(u"Pick a Section Used as the Category's Parent Level"),
    )
    description = models.TextField(
        _(u"Category Description"),
        blank=False,
        help_text=_(u"Your Category Description")
    )
    image = models.ImageField(
        _(u"Image"),
        upload_to=UPLOAD_TO,
        blank=True,
        help_text=_(u"Category Image Display in Pages"),
    )
    created_date = models.DateTimeField(
        _(u"Create Time"),
        auto_now_add=True,
    )
    menu = models.OneToOneField(CMSMenuID)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-created_date']
        verbose_name = _(u'Category')
        verbose_name_plural = _(u'Category')

    @property
    def url(self):
        return "%s%s/%s/" % (ROOT_URL, 'category', self.slug)
    
    @models.permalink
    def get_absolute_url(self):
        return ("cms_content_category_detail", (self.slug,))


class CMSArticle(models.Model):
    """Models for CMS's Articles:

    Article is the third level of cms_content structure. Every article contains
    the content you write.
    """

    PUB_STATUS = (
        ('pub', _(u'published')),
        ('hid', _(u'hidden')),
        ('dra', _(u'draft')),
        ('del', _(u'deleted')),
    )
    
    title = models.CharField(
        _(u"Article Title"),
        max_length=255,
        blank=False,
        help_text=_(u"Article's Title"),
    )
    slug = models.SlugField(
        _(u"Slug"),
        max_length=255,
        blank=False,
        unique=True,
        help_text=_(u"Article's Slug"),
    )
    content = models.TextField(
        _(u"Article Content"),
        blank=False,
        help_text=_(u"Article's Content"),
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_(u"Author Name"),
        related_name="cms_article_author",
        blank=False,
    )
    created_date = models.DateTimeField(
        _(u"Created Date"),
        auto_now_add=True,
    )
    last_modified_by = models.ForeignKey(
        User,
        verbose_name=_(u"Last Modified By"),
        related_name="cms_article_revisor",
    )
    last_modified_date = models.DateTimeField(
        _(u"Last Modified Date"),
        auto_now=False,
    )
    category = models.ForeignKey(
        CMSCategory,
        verbose_name=_(u"Category"),
        related_name="article_of_category",
        help_text=_(u"Pick a Category as the Article's Parent Level"),
    )
    pub_status = models.CharField(
        _(u"Article Status"),
        max_length=3,
        choices=PUB_STATUS,
        default='pub',
    )
    hits = models.IntegerField(
        _(u"Article His Number"),
        default=1,
    )
    pub_start_date = models.DateTimeField(
        _(u"Article Publish Start Date"),
        blank=False,
        null=False,
        default=datetime.now,
    )
    pub_end_date = models.DateTimeField(
        _(u"Article Publish End Date"),
        blank=False,
        null=False,
        default=datetime(2030,12,31)
    )
    menu = models.OneToOneField(CMSMenuID)
    tags = TaggableManager()
    objects = models.Manager()
    pub_manager = CMSArticlePubManager()
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = _(u'Article')
        verbose_name_plural = _(u'Article')

    def __unicode__(self):
        return u'%s - %s' % (self.created_by.username, self.title)

    def get_parent_node(self, nodes):
        """Get a category node which including queryset's articles
    
        Example:
        parent_node = category_node(article, nodes)
    
        """
        for node in nodes:
            if node.title == self.category.name:
                return node
        return None

    @property
    def previous_article(self):
        """Return the previous article"""
        articles = CMSArticle.pub_manager.select_related().filter(created_date__lt=self.created_date)
        if articles:
            return articles[0]
        else:
            return
    
    @property
    def next_article(self):
        """Return the next article"""
        articles = CMSArticle.pub_manager.select_related().filter(created_date__gt=self.created_date)
        if articles:
            return articles[0]
        else:
            return
    
    @property
    def url(self):
        return ROOT_URL + 'article/' + "%s/%s/%s/%s/" % (
            self.created_date.strftime('%Y'),
            self.created_date.strftime('%m'),
            self.created_date.strftime('%d'),
            self.slug,
            )

    @models.permalink
    def get_absolute_url(self):
        return ('cms_content_article_detail', None, {
            "year":  self.created_date.strftime('%Y'),
            "month": self.created_date.strftime('%m'),
            "day":   self.created_date.strftime('%d'),
            "slug":  self.slug,
            }
        )


def on_comment_was_posted(sender, comment, request, *args, **kwargs):
    """Spam checking can be enabled/disabled per the comment's target Model

    Usage:
    if comment.content_type.model_class() != CMSArticle:
        return
    """

    try:
        from akismet import Akismet
    except:
        return

    ak = Akismet(
        key=settings.AKISMET_API_KEY,
        blog_url='http://%s/' % Site.objects.get(pk=settings.SITE_ID).domain
    )
    if ak.verify_key():
        data = {
            'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referrer': request.META.get('HTTP_REFERER', ''),
            'comment_type': 'comment',
            'comment_author': comment.user_name.encode('utf-8'),
        }

    if ak.comment_check(comment.comment.encode('utf-8'), data=data, build_data=True):
        comment.flags.create(
            user=comment.content_object.author,
            flag='spam'
        )
        comment.is_public = False
        comment.save()
comment_was_posted.connect(on_comment_was_posted)
