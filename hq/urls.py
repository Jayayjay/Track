from django.urls import path
from . import views

urlpatterns = [
    path('', views.hq_index, name='hq'),

    # Auth
    path('api/signup/',  views.HQSignupView.as_view(),  name='hq-signup'),
    path('api/login/',   views.HQLoginView.as_view(),   name='hq-login'),

    # Public
    path('api/programs/', views.HQProgramsView.as_view(), name='hq-programs'),

    # Member
    path('api/me/',                          views.HQMeView.as_view(),                  name='hq-me'),
    path('api/register/',                    views.HQRegisterView.as_view(),             name='hq-register'),
    path('api/member/dashboard/',            views.HQMemberDashboardView.as_view(),      name='hq-member-dashboard'),
    path('api/member/pay/<int:pk>/',         views.HQMemberPayView.as_view(),            name='hq-member-pay'),
    path('api/webhooks/stripe/',             views.HQStripeWebhookView.as_view(),        name='hq-stripe-webhook'),

    # Admin
    path('api/admin/stats/',                      views.HQAdminStatsView.as_view(),              name='hq-admin-stats'),
    path('api/admin/registrations/',              views.HQAdminRegistrationsView.as_view(),       name='hq-admin-regs'),
    path('api/admin/registrations/<int:pk>/',     views.HQAdminRegistrationDetailView.as_view(),  name='hq-admin-reg-detail'),
    path('api/admin/programs/',                   views.HQAdminProgramsView.as_view(),            name='hq-admin-programs'),
    path('api/admin/programs/<int:pk>/',          views.HQAdminProgramDetailView.as_view(),       name='hq-admin-program-detail'),
    path('api/admin/athlete-records/',            views.HQAdminAthleteRecordsView.as_view(),      name='hq-admin-athlete-records'),
    path('api/admin/users/',                      views.HQAdminUsersView.as_view(),               name='hq-admin-users'),
    path('api/admin/contact/',                    views.HQAdminContactView.as_view(),             name='hq-admin-contact'),

    # FK options for select fields
    path('api/admin/opts/<str:model>/',       views.HQAdminOptsView.as_view(),                name='hq-admin-opts'),

    # Full model endpoints (list + create)
    path('api/admin/athletes/',               views.HQAdminAthletesView.as_view(),            name='hq-admin-athletes'),
    path('api/admin/athletes/<int:pk>/',      views.HQAdminAthleteDetailView.as_view(),        name='hq-admin-athlete-detail'),
    path('api/admin/teams/',                  views.HQAdminTeamsView.as_view(),               name='hq-admin-teams'),
    path('api/admin/teams/<int:pk>/',         views.HQAdminTeamDetailView.as_view(),           name='hq-admin-team-detail'),
    path('api/admin/events/',                 views.HQAdminEventsView.as_view(),              name='hq-admin-events'),
    path('api/admin/events/<int:pk>/',        views.HQAdminEventDetailView.as_view(),          name='hq-admin-event-detail'),
    path('api/admin/payments/',               views.HQAdminPaymentsView.as_view(),            name='hq-admin-payments'),
    path('api/admin/payments/<int:pk>/',      views.HQAdminPaymentDetailView.as_view(),        name='hq-admin-payment-detail'),
    path('api/admin/announcements/',          views.HQAdminAnnouncementsView.as_view(),       name='hq-admin-announcements'),
    path('api/admin/announcements/<int:pk>/', views.HQAdminAnnouncementDetailView.as_view(),   name='hq-admin-announcement-detail'),
    path('api/admin/compliance/',             views.HQAdminComplianceView.as_view(),          name='hq-admin-compliance'),
    path('api/admin/compliance/<int:pk>/',    views.HQAdminComplianceDetailView.as_view(),     name='hq-admin-compliance-detail'),
    path('api/admin/incidents/',              views.HQAdminIncidentsView.as_view(),           name='hq-admin-incidents'),
    path('api/admin/incidents/<int:pk>/',     views.HQAdminIncidentDetailView.as_view(),       name='hq-admin-incident-detail'),
    path('api/admin/transfers/',              views.HQAdminTransfersView.as_view(),           name='hq-admin-transfers'),
    path('api/admin/transfers/<int:pk>/',     views.HQAdminTransferDetailView.as_view(),       name='hq-admin-transfer-detail'),
    path('api/admin/leagues/',                views.HQAdminLeaguesView.as_view(),             name='hq-admin-leagues'),
    path('api/admin/leagues/<int:pk>/',       views.HQAdminLeagueDetailView.as_view(),         name='hq-admin-league-detail'),
    path('api/admin/fixtures/',               views.HQAdminFixturesView.as_view(),            name='hq-admin-fixtures'),
    path('api/admin/organizations/',          views.HQAdminOrganizationsView.as_view(),       name='hq-admin-organizations'),
    path('api/admin/organizations/<int:pk>/', views.HQAdminOrgDetailView.as_view(),            name='hq-admin-org-detail'),
    path('api/admin/registration-orders/',    views.HQAdminRegistrationOrdersView.as_view(),  name='hq-admin-reg-orders'),
    path('api/admin/audit-log/',              views.HQAdminAuditLogView.as_view(),            name='hq-admin-audit'),
    path('api/admin/analytics/',              views.HQAdminAnalyticsView.as_view(),           name='hq-admin-analytics'),
]
