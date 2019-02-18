# -*- coding: utf-8 -*-

from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'attributes', views.AttributeViewSet)
router.register(r'attribute-set', views.AttributeSetViewSet)
router.register(r'computers', views.ComputerViewSet)
router.register(
    r'computers',
    views.HardwareComputerViewSet,
    basename='computers-hardware'
)
router.register(r'deployments/internal-sources', views.InternalSourceViewSet)
router.register(r'deployments/external-sources', views.ExternalSourceViewSet)
router.register(r'domains', views.DomainViewSet)
router.register(r'errors', views.ErrorViewSet)
router.register(r'fault-definitions', views.FaultDefinitionViewSet)
router.register(r'faults', views.FaultViewSet)
router.register(r'hardware', views.HardwareViewSet)
router.register(r'migrations', views.MigrationViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'packages', views.PackageViewSet)
router.register(r'pms', views.PmsViewSet)
router.register(r'platforms', views.PlatformViewSet)
router.register(r'properties', views.PropertyViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'schedule-delays', views.ScheduleDelayViewSet)
router.register(r'scopes', views.ScopeViewSet)
router.register(r'status-logs', views.StatusLogViewSet)
router.register(r'stores', views.StoreViewSet)
router.register(r'syncs', views.SynchronizationViewSet)
router.register(r'users', views.UserViewSet)

device_router = routers.DefaultRouter()

device_router.register(r'connections', views.ConnectionViewSet)
device_router.register(r'devices', views.DeviceViewSet)
device_router.register(r'drivers', views.DriverViewSet)
device_router.register(r'features', views.FeatureViewSet)
device_router.register(r'logical', views.LogicalViewSet)
device_router.register(r'manufacturers', views.ManufacturerViewSet)
device_router.register(r'models', views.ModelViewSet)
device_router.register(r'types', views.TypeViewSet)
