from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import TaskList, TaskDetail
from django.urls import path, include
router = routers.DefaultRouter()

router.register('api/token/', TokenObtainPairView.as_view(), 'token_obtain_pair')
router.register('api/token/refresh/', TokenRefreshView.as_view(), 'token_refresh')
router.register('api/tasks/', TaskList.as_view(), 'task_list')
router.register('api/tasks/<int:pk>/', TaskDetail.as_view(), include('task_detail'))
urlpatterns = router.urls

