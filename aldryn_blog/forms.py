# -*- coding: utf-8 -*-
from app_data.forms import multiform_factory
from django import forms
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, gettext
from django_select2.forms import Select2MultipleWidget
from hvad.forms import TranslatableModelForm
from unidecode import unidecode

from .models import Post


class LatestEntriesForm(forms.ModelForm):

    class Meta:

        widgets = {
            'tags': Select2MultipleWidget
        }
        fields = '__all__'


class PostForm(forms.ModelForm):

    class Meta:
        fields = '__all__'


class AutoSlugForm(TranslatableModelForm):

    slug_field = 'slug'
    slugified_field = None

    def clean(self):
        super(AutoSlugForm, self).clean()

        self.data = self.data.copy()

        if not self.fields.get(self.slug_field):
            return self.cleaned_data

        if not self.data.get(self.slug_field):
            slug = self.generate_slug()
            # add to self.data in order to show generated slug in the form in case of an error
            self.data[self.slug_field] = self.cleaned_data[self.slug_field] = slug
        else:
            if self._errors.get(self.slug_field):
                return self.cleaned_data
            slug = self.cleaned_data[self.slug_field]

        # validate uniqueness
        conflict = self.get_slug_conflict(slug=slug)
        if conflict:
            self.report_error(conflict=conflict)

        return self.cleaned_data

    def generate_slug(self):
        content_to_slugify = self.cleaned_data.get(self.slugified_field, '')
        return slugify(unidecode(content_to_slugify))

    def get_slug_conflict(self, slug):
        translations_model = self.instance._meta.translations_model

        try:
            language_code = self.instance.language_code
        except translations_model.DoesNotExist:
            language_code = get_language()

        conflicts = translations_model.objects.filter(slug=slug, language_code=language_code)
        if self.is_edit_action():
            conflicts = conflicts.exclude(master=self.instance)

        try:
            return conflicts.get()
        except translations_model.DoesNotExist:
            return None

    def report_error(self, conflict):
        address = '<a href="%(url)s" target="_blank">%(label)s</a>' % {
            'url': conflict.master.get_absolute_url(),
            'label': gettext('the conflicting object')}
        error_message = gettext('Conflicting slug. See %(address)s.') % {'address': address}
        self.append_to_errors(field='slug', message=mark_safe(error_message))

    def append_to_errors(self, field, message):
        try:
            self._errors[field].append(message)
        except KeyError:
            self._errors[field] = self.error_class([message])

    def is_edit_action(self):
        return self.instance.pk is not None


class CategoryForm(AutoSlugForm):

    slugified_field = 'name'

    class Meta:
        fields = ['name', 'slug']


# Used by app data
BlogPostMultiForm = multiform_factory(Post, form=PostForm)
