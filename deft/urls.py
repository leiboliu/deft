"""deft URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from frontend.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('frontend.urls')),
    path('backend/', include('backend.urls')),
    path('login/', LoginView.as_view(), name="frontend_login_view"),
    path('', LoginView.as_view(), name="frontend_view"),

    path('logout/', LogoutView.as_view(), name='frontend_logout_view')

]

admin.site.site_header = "DEFT Admin"
admin.site.site_title  =  "DEFT admin site"
admin.site.index_title  =  "Data Management"
