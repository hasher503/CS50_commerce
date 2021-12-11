"""all forms for auction app"""
from django.forms import ModelForm, Textarea, TextInput, NumberInput

from .models import Listing, Bid, Comment


class NewListingForm(ModelForm):
    """create a new auction item"""
    class Meta:
        model = Listing
        fields = ('title', 'price', 'description', 'img_url', 'category')
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'price': NumberInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
            'img_url': TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
        'price': 'Minimum Initial Bid',
        'img_url': 'Image URL (optional)',
        'category': 'Category (optional)'
    }

class BidForm(ModelForm):
    """post a new bid"""
    class Meta:
        model = Bid
        fields = ('bid_price',)
        widgets = {'bid_price': NumberInput(attrs={'class': 'form-control',})}
        labels = {'bid_price': ''}

class CommentForm(ModelForm):
    """comment on a listing"""
    class Meta:
        model = Comment
        fields = {'comment',}
        widgets = {'comment': Textarea(attrs={'class': 'form-control'})}
