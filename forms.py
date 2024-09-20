from django import forms

from .models import Song


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = "__all__"


class SearchForm(forms.Form):
    search = forms.CharField(required=False)
    search_in = forms.ChoiceField(required=False,
                                  choices=(
                                      ("name", "Name"),
                                      ("singer", "Singer")
                                  ))

    def clean_search_in(self):
        return self.cleaned_data["search_in"] or "name"