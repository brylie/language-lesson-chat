from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django_registration.backends.one_step.views import RegistrationView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from accounts.forms import CustomRegistrationForm
from search import views as search_views
from lessons import urls as lessons_urls

urlpatterns = [
    path('accounts/register/',
         RegistrationView.as_view(
             form_class=CustomRegistrationForm,
             success_url="/",
         ),
         name='django_registration_register',
         ),
    path('accounts/login/', auth_views.LoginView.as_view(
        next_page="/",
    ), name='login'),

    path('accounts/logout/',
         # Redirect to home page after logout
         auth_views.LogoutView.as_view(next_page="/"),
         name='logout'
         ),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("lessons/", include(lessons_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
