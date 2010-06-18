# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe


class WYMEditor(forms.Textarea):
    class Media:
        js = (
            'admin/js/jquery.min.js',
            'cms_content/js/wymeditor/jquery.wymeditor.pack.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        self.attrs = {'class': 'wymeditor'}
        if attrs:
            self.attrs.update(attrs)
        super(WYMEditor, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rendered = super(WYMEditor, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            jQuery('#id_%s').wymeditor({
                updateSelector: '.submit-row input[type=submit]',
                updateEvent: 'click',
                skin: 'default',
                lang: '%s',
                postInitDialog: function (wym, wdw) {
                    wymeditor_filebrowser(wym, wdw);
                }
            });
            </script>''' % (name, self.language))
