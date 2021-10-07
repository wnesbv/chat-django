

from django.views.static import serve
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static, settings
import notifications.urls


urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path('chat/', include('chat.urls')),
        path("", include("accounts.urls")),
        path("accounts/", include("django.contrib.auth.urls")),
        path("to-friends/", include("to_friends.urls")),

        path("inbox/notifications/", include(notifications.urls, namespace='notifications')),

    ]
    + static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)


urlpatterns += [
    path(
        "media/<path:path>",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
    path("static/<path:path>", serve, {"document_root": settings.STATIC_ROOT}),
]
