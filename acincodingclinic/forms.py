from django import forms
from django.forms import formset_factory
from django_summernote.widgets import SummernoteWidget
from django_summernote import fields as summer_fields
from .models import CDC_Board, CDC_Comment, CDC_Error, CoachingFileMa, CDC_Notice

class PostForm(forms.ModelForm):
    class Meta:
           model = CDC_Board
           fields = ('Board_Files',)
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['Board_Files'].required = False

class CommentForm(forms.ModelForm):
    class Meta:
        model = CDC_Comment
        fields = ['comment']
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].label = "댓글"

class ErrorForm(forms.ModelForm):
    class Meta:
           model = CDC_Error
           fields = ('Error_Files',)
    def __init__(self, *args, **kwargs):
        super(ErrorForm, self).__init__(*args, **kwargs)
        self.fields['Error_Files'].required = False

class CoachingFileForm(forms.ModelForm):
    class Meta:
        model = CoachingFileMa
        fields = ('Coaching_Files',)
    def __init__(self, *args, **kwargs):
        super(CoachingFileForm, self).__init__(*args, **kwargs)
        self.fields['Coaching_Files'].required = False

class NoticeForm(forms.ModelForm):
    class Meta:
           model = CDC_Notice
           fields = ('Notice_Files',)
    def __init__(self, *args, **kwargs):
        super(NoticeForm, self).__init__(*args, **kwargs)
        self.fields['Notice_Files'].required = False
