from django.contrib import admin
from openwatch.recordings.models import Recording, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]

admin.site.register(User, UserProfileAdmin)


class RecordingAdmin(admin.ModelAdmin):
    model = Recording
    list_display = ('name', 'email', 'date', 'location', 'rec_file', 'org_approved')  # Allow sorting by these fields
    list_filter = ('date', 'org_approved')  # Allow filtering by these fields
    list_editable = ('org_approved',)  # Allow bulk changes to these fields

    def queryset(self, request):
        """ This method defines the queryset used by the admin app for this model
            Limit Recordings to those that belong to the requesting user's org.
        """
        qs = super(RecordingAdmin, self).queryset(request)

        org_tag = request.user.get_profile().org_tag
        if org_tag != '':
            # If the user belongs to an org:
            return qs.filter(tags__contains=org_tag)
        else:
            # Return all Recordings
            return qs

        #print request.user.get_profile()
        return qs

    def get_readonly_fields(self, request, obj=None):
        ''' Define which fields are editable in the admin
            based on the user's tags. If a user has an
            org tag, we restrict editing on all fields
            except tags, and org_approved
        '''
        org_tag = request.user.get_profile().org_tag
        if org_tag != '':
            # If the user belongs to an org
            # Restrict editing of certain fields
            return ('name', 'email', 'date', 'location', 'approved', 'vimeo', 'vimeo_dl', 'liveleak', 'youtube', 'local', 'rec_file', 'file_loc', 'mimetype', 'featured', 'public_description', 'private_description')
        else:
            # Return all Recordings
            return ()




admin.site.register(Recording, RecordingAdmin)