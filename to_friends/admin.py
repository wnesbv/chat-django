

from __future__ import absolute_import
from django.contrib.admin import ModelAdmin, site
from .models import FriendshipRequest, Friend


class FriendAdmin(ModelAdmin):
    model = Friend
    readonly_fields = ('created',)
    search_fields = ('id', 'from_user', 'to_user',)
    list_display = ('id', 'from_user', 'to_user', 'created')
    list_display_links = ('id',)
    list_filter = ('from_user', 'to_user')
    date_hierarchy = 'created'

class FriendshipRequestAdmin(ModelAdmin):
    model = FriendshipRequest
    readonly_fields = ('created',)
    search_fields = ('id', 'from_user', 'to_user',)
    list_display = ('id', 'from_user', 'to_user', 'created')
    list_display_links = ('id',)
    list_filter = ('from_user', 'to_user')
    date_hierarchy = 'created'


site.register(Friend, FriendAdmin)
site.register(FriendshipRequest, FriendshipRequestAdmin)
