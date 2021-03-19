#
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('accounts/', include('accounts.urls'),
#     path('art-fairs/', include('art_fairs.urls'),
#     path('core/', include('core.urls'),
#     path('datasets/', include('datasets.urls'),
#     path('demands/', include('demands.urls'),
#     path('galleries/', include('galleries.urls'),
#     path('inventories/', include('inventories.urls'),
#     path('social/', include('allauth.socialaccount.urls')),
#     path('statistics/', include('analytics.urls'),
# ]
#
# # Add swagger documentation only for dev/local
# if is_dev_mode():
#     urlpatterns += [
#         path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#         path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
#         re_path(r'^silk/', include('silk.urls', namespace='silk')),
#         re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
#     ]
#
