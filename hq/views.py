from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import SeasonProgram, HQRegistration
from athlete_records.models import AthleteRecords
from contact.models import ContactMessage
from organizations.models import Organization, OrganizationMember
from athletes.models import Athlete, Guardian, EmergencyContact
from teams.models import Team, TrainingSession, TransferRequest, PracticeAttendance
from events.models import Event, EventRegistration
from finance.models import SeasonConfig, Payment, PaymentReminder, StripeTransaction
from communications.models import Announcement, EmailLog, Notification, Conversation, Message, EmailAutomation
from registration.models import RegistrationSubmission, RegistrationOrder, Waiver, BulkImportLog
from compliance.models import ComplianceRecord, BackgroundCheck, IncidentReport, AuditLog
from leagues.models import League, Division, LeagueSeason, Fixture, Match, Standing, Venue, Bracket
from analytics.models import AnalyticsSnapshot
import stripe
import datetime

stripe.api_key = django_settings.STRIPE_SECRET_KEY


def hq_index(request):
    return render(request, 'hq/index.html')


# ── Auth ──────────────────────────────────────────────────────

class HQSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        d          = request.data
        email      = d.get('email', '').strip().lower()
        password   = d.get('password', '')
        first_name = d.get('first_name', '').strip()
        last_name  = d.get('last_name', '').strip()

        if not all([email, password, first_name, last_name]):
            return Response({'error': 'All fields are required.'}, status=400)
        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters.'}, status=400)
        if User.objects.filter(username=email).exists():
            return Response({'error': 'An account with this email already exists.'}, status=400)

        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name,
        )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token':    token.key,
            'user':     _user_payload(user),
        })


class HQLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        user     = authenticate(username=email, password=password)
        if not user:
            return Response({'error': 'Invalid email or password.'}, status=400)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user':  _user_payload(user),
        })


def _user_payload(user):
    return {
        'id':          user.id,
        'name':        user.get_full_name() or user.username,
        'email':       user.email,
        'is_staff':    user.is_staff,
        'is_superuser':user.is_superuser,
    }


# ── Public ────────────────────────────────────────────────────

class HQProgramsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        programs = SeasonProgram.objects.filter(is_active=True)
        return Response([_program_payload(p) for p in programs])


def _program_payload(p):
    today    = datetime.date.today()
    is_early = bool(p.early_bird_fee and p.early_bird_deadline and today <= p.early_bird_deadline)
    return {
        'id':                  p.id,
        'name':                p.name,
        'season':              p.season,
        'standard_fee':        str(p.fee),
        'current_fee':         str(p.current_fee()),
        'current_fee_label':   p.current_fee_label(),
        'early_bird_fee':      str(p.early_bird_fee) if p.early_bird_fee else None,
        'early_bird_deadline': str(p.early_bird_deadline) if p.early_bird_deadline else None,
        'registration_open':   str(p.registration_open),
        'registration_close':  str(p.registration_close),
        'is_active':           p.is_active,
    }


def _reg_payload(r):
    return {
        'id':           r.id,
        'athlete_name': f"{r.athlete_first_name} {r.athlete_last_name}",
        'athlete_dob':  str(r.athlete_dob),
        'athlete_gender': r.get_athlete_gender_display(),
        'program':      r.program.name,
        'season':       r.program.season,
        'program_id':   r.program_id,
        'user_name':    r.user.get_full_name() or r.user.username,
        'user_email':   r.user.email,
        'status':       r.status,
        'fee':          str(r.program.current_fee()),
        'fee_label':    r.program.current_fee_label(),
        'created_at':   r.created_at.strftime('%b %d, %Y'),
        'address':      ', '.join(filter(None, [r.address, r.city, r.state, r.zip_code])),
        'guardian_name':  r.guardian_name,
        'guardian_phone': r.guardian_phone,
        'guardian_email': r.guardian_email,
        'medical_notes':  r.medical_notes,
        'has_allergies':  r.has_allergies,
        'allergies':      r.allergies,
        'waiver_accepted':r.waiver_accepted,
        'payment_status': r.payment_status,
        'paid_at':        r.paid_at.strftime('%b %d, %Y') if r.paid_at else None,
    }


# ── Registration (member) ─────────────────────────────────────

class HQRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        d          = request.data
        program_id = d.get('program_id')

        try:
            program = SeasonProgram.objects.get(id=program_id, is_active=True)
        except SeasonProgram.DoesNotExist:
            return Response({'error': 'Program not found.'}, status=400)

        if not d.get('waiver_accepted'):
            return Response({'error': 'You must accept the liability waiver.'}, status=400)

        if not all([d.get('athlete_first_name'), d.get('athlete_last_name'),
                    d.get('athlete_dob'), d.get('athlete_gender')]):
            return Response({'error': 'Athlete name, date of birth, and gender are required.'}, status=400)

        reg = HQRegistration.objects.create(
            user                 = request.user,
            program              = program,
            athlete_first_name   = d.get('athlete_first_name', ''),
            athlete_last_name    = d.get('athlete_last_name', ''),
            athlete_dob          = d.get('athlete_dob'),
            athlete_gender       = d.get('athlete_gender', ''),
            address              = d.get('address', ''),
            city                 = d.get('city', ''),
            state                = d.get('state', ''),
            zip_code             = d.get('zip_code', ''),
            guardian_name        = d.get('guardian_name', ''),
            guardian_relationship= d.get('guardian_relationship', ''),
            guardian_phone       = d.get('guardian_phone', ''),
            guardian_email       = d.get('guardian_email', ''),
            medical_notes        = d.get('medical_notes', ''),
            has_allergies        = bool(d.get('has_allergies', False)),
            allergies            = d.get('allergies', ''),
            waiver_accepted      = True,
            photo_consent        = bool(d.get('photo_consent', False)),
        )

        return Response({
            'id':           reg.id,
            'athlete_name': f"{reg.athlete_first_name} {reg.athlete_last_name}",
            'program':      program.name,
            'season':       program.season,
            'fee':          str(program.current_fee()),
            'status':       reg.status,
        })


# ── Member dashboard ──────────────────────────────────────────

class HQMemberDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        regs = HQRegistration.objects.filter(
            user=request.user
        ).select_related('program').order_by('-created_at')
        return Response({
            'registrations': [_reg_payload(r) for r in regs],
        })


# ── Me (token validation + user info) ─────────────────────────

class HQMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_user_payload(request.user))


# ── Member: pay (Stripe Checkout — card never touches our server) ─

class HQMemberPayView(APIView):
    """
    Creates a Stripe Checkout Session and returns the hosted URL.
    The member is redirected to Stripe's page; no card data passes through this server.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not django_settings.STRIPE_SECRET_KEY:
            return Response(
                {'error': 'Online payments are not configured. Please contact us to arrange payment.'},
                status=503,
            )

        try:
            reg = request.user.hq_registrations.select_related('program').get(pk=pk)
        except HQRegistration.DoesNotExist:
            return Response({'error': 'Registration not found.'}, status=404)

        if reg.payment_status == 'paid':
            return Response({'error': 'This registration has already been paid.'}, status=400)

        if reg.status != 'approved':
            return Response({'error': 'Registration must be approved before payment can be made.'}, status=400)

        amount_cents = int(reg.program.current_fee() * 100)

        # Build absolute return URLs
        base = request.build_absolute_uri('/hq/')
        success_url = f"{base}?payment=success&reg={reg.id}"
        cancel_url  = f"{base}?payment=cancelled&reg={reg.id}"

        session = stripe.checkout.Session.create(
            mode                 = 'payment',
            customer_email       = request.user.email,
            client_reference_id  = str(reg.id),
            success_url          = success_url,
            cancel_url           = cancel_url,
            line_items           = [{
                'quantity': 1,
                'price_data': {
                    'currency':     'usd',
                    'unit_amount':  amount_cents,
                    'product_data': {
                        'name': f"HVTF Registration — {reg.program.name} ({reg.program.season})",
                        'description': f"Athlete: {reg.athlete_first_name} {reg.athlete_last_name}",
                    },
                },
            }],
            metadata = {
                'registration_id': str(reg.id),
                'user_id':         str(request.user.id),
                'athlete_name':    f"{reg.athlete_first_name} {reg.athlete_last_name}",
                'program':         reg.program.name,
                'season':          reg.program.season,
            },
            payment_intent_data = {
                'description':  f"HVTF Reg #{reg.id} — {reg.athlete_first_name} {reg.athlete_last_name}",
                'receipt_email': request.user.email,
                'metadata': {
                    'registration_id': str(reg.id),
                },
            },
        )

        # Track that a checkout was initiated
        reg.stripe_payment_intent_id = session.id  # store session ID for reference
        reg.payment_status = 'pending'
        reg.save(update_fields=['stripe_payment_intent_id', 'payment_status'])

        return Response({'checkout_url': session.url})


@method_decorator(csrf_exempt, name='dispatch')
class HQStripeWebhookView(APIView):
    """
    Stripe webhook — CSRF-exempt, raw body required for signature verification.
    Handles:
      checkout.session.completed       → mark registration paid, update analytics
      checkout.session.expired         → reset payment_status to unpaid
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        from django.utils import timezone
        import logging
        log = logging.getLogger(__name__)

        payload        = request.body
        sig_header     = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        webhook_secret = django_settings.STRIPE_WEBHOOK_SECRET

        if not webhook_secret:
            log.error('Stripe webhook: STRIPE_WEBHOOK_SECRET not configured')
            return Response({'error': 'Webhook secret not configured.'}, status=500)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except stripe.error.SignatureVerificationError as e:
            log.error('Stripe webhook signature failed: %s', e)
            return Response({'error': 'Invalid signature.'}, status=400)
        except ValueError as e:
            log.error('Stripe webhook bad payload: %s', e)
            return Response({'error': 'Invalid payload.'}, status=400)

        event_type = event['type']
        obj        = event['data']['object']

        # Extract registration ID — try metadata first, then client_reference_id
        metadata = obj.get('metadata') or {}
        reg_id   = metadata.get('registration_id') or obj.get('client_reference_id')

        log.info('Stripe webhook received: %s  reg_id=%s', event_type, reg_id)

        if not reg_id:
            return Response({'received': True})

        try:
            reg_pk = int(reg_id)
        except (ValueError, TypeError):
            log.error('Stripe webhook: could not parse reg_id=%s', reg_id)
            return Response({'received': True})

        if event_type == 'checkout.session.completed':
            # payment_status='paid' for card/immediate; 'no_payment_required' for free
            # Accept either — a completed session with a successful payment is enough
            pay_status = obj.get('payment_status', '')
            if pay_status in ('paid', 'no_payment_required'):
                try:
                    reg = HQRegistration.objects.select_related('program').get(pk=reg_pk)
                    if reg.payment_status != 'paid':
                        _mark_registration_paid(reg, timezone.now())
                        log.info('Stripe webhook: marked reg %s as paid', reg_pk)
                except HQRegistration.DoesNotExist:
                    log.error('Stripe webhook: HQRegistration %s not found', reg_pk)

        elif event_type == 'checkout.session.expired':
            try:
                reg = HQRegistration.objects.get(pk=reg_pk)
                if reg.payment_status == 'pending':
                    reg.payment_status = 'unpaid'
                    reg.save(update_fields=['payment_status'])
            except HQRegistration.DoesNotExist:
                pass

        return Response({'received': True})


def _mark_registration_paid(reg, paid_at):
    """Mark an HQRegistration as paid and upsert today's revenue_collected analytics snapshot."""
    from django.db.models import Sum
    from decimal import Decimal

    reg.payment_status = 'paid'
    reg.paid_at        = paid_at
    reg.save(update_fields=['payment_status', 'paid_at'])

    today      = paid_at.date()
    total_paid = HQRegistration.objects.filter(
        payment_status='paid'
    ).aggregate(t=Sum('program__fee'))['t'] or Decimal('0')

    AnalyticsSnapshot.objects.update_or_create(
        date        = today,
        metric_name = 'revenue_collected',
        dimension   = '',
        defaults    = {
            'value':     total_paid,
            'breakdown': {'source': 'hq_registration', 'updated_at': paid_at.isoformat()},
        },
    )


# ── Admin: stats ──────────────────────────────────────────────

class HQAdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        from django.db.models import Sum
        from django.utils import timezone
        import datetime

        today     = timezone.now().date()
        month_ago = today - datetime.timedelta(days=30)
        expiring  = today + datetime.timedelta(days=30)

        # Monthly registration counts for the last 6 months (for chart)
        reg_monthly = []
        for i in range(5, -1, -1):
            d  = today.replace(day=1) - datetime.timedelta(days=i * 28)
            mo = d.replace(day=1)
            if mo.month == 12:
                nxt = mo.replace(year=mo.year+1, month=1)
            else:
                nxt = mo.replace(month=mo.month+1)
            count = Athlete.objects.filter(registration_date__gte=mo, registration_date__lt=nxt).count()
            reg_monthly.append({'label': mo.strftime('%b'), 'value': count})

        # Revenue from HQ registrations (Stripe Checkout payments)
        hq_rev_paid    = HQRegistration.objects.filter(payment_status='paid').aggregate(
                             t=Sum('program__fee'))['t'] or 0
        hq_rev_pending = HQRegistration.objects.filter(
                             status='approved', payment_status__in=('unpaid','pending')).aggregate(
                             t=Sum('program__fee'))['t'] or 0
        hq_unpaid      = HQRegistration.objects.filter(
                             status='approved', payment_status__in=('unpaid','pending')).count()

        return Response({
            # Core counts
            'athletes':               Athlete.objects.count(),
            'athletes_active':        Athlete.objects.filter(status='active').count(),
            'athletes_new_30d':       Athlete.objects.filter(registration_date__gte=month_ago).count(),
            'teams':                  Team.objects.count(),
            'users':                  User.objects.count(),
            # Registrations
            'registrations':          HQRegistration.objects.count(),
            'registrations_pending':  HQRegistration.objects.filter(status='pending').count(),
            'registrations_approved': HQRegistration.objects.filter(status='approved').count(),
            # HQ Registration payments (Stripe Checkout)
            'payments':               HQRegistration.objects.filter(status='approved').count(),
            'payments_pending':       hq_unpaid,
            'payments_overdue':       0,
            'revenue_paid':           float(hq_rev_paid),
            'revenue_pending':        float(hq_rev_pending),
            'hq_paid_count':          HQRegistration.objects.filter(payment_status='paid').count(),
            # Events
            'events':                 Event.objects.count(),
            'events_upcoming':        Event.objects.filter(start_datetime__gte=timezone.now(), is_cancelled=False).count(),
            # Compliance & Safety
            'compliance_records':     ComplianceRecord.objects.count(),
            'compliance_expired':     ComplianceRecord.objects.filter(status='expired').count(),
            'compliance_expiring':    ComplianceRecord.objects.filter(expiry_date__gte=today, expiry_date__lte=expiring).count(),
            'incidents_open':         IncidentReport.objects.filter(status='open').count(),
            'incidents_critical':     IncidentReport.objects.filter(status='open', severity='critical').count(),
            # Transfers & comms
            'transfer_requests':      TransferRequest.objects.count(),
            'transfer_pending':       TransferRequest.objects.filter(status='pending').count(),
            'announcements':          Announcement.objects.count(),
            'contact_messages':       ContactMessage.objects.count(),
            # Leagues
            'leagues':                League.objects.count(),
            'fixtures':               Fixture.objects.count(),
            'organizations':          Organization.objects.count(),
            # Chart data
            'reg_monthly':            reg_monthly,
            # Legacy
            'programs':               SeasonProgram.objects.count(),
            'programs_active':        SeasonProgram.objects.filter(is_active=True).count(),
        })


# ── Admin: registrations ──────────────────────────────────────

class HQAdminRegistrationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        status_filter = request.query_params.get('status')
        qs = HQRegistration.objects.select_related('user', 'program').order_by('-created_at')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response([_reg_payload(r) for r in qs])


class HQAdminRegistrationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        try:
            reg = HQRegistration.objects.get(pk=pk)
        except HQRegistration.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
        new_status = request.data.get('status')
        if new_status in ('pending', 'approved', 'rejected'):
            reg.status = new_status
            reg.save()
        return Response({'id': reg.id, 'status': reg.status})


# ── Admin: programs ───────────────────────────────────────────

class HQAdminProgramsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        return Response([_program_payload(p) for p in SeasonProgram.objects.order_by('-registration_open')])

    def post(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        d = request.data
        try:
            p = SeasonProgram.objects.create(
                name               = d.get('name', 'Season'),
                season             = d['season'],
                fee                = d['fee'],
                early_bird_fee     = d.get('early_bird_fee') or None,
                early_bird_deadline= d.get('early_bird_deadline') or None,
                registration_open  = d['registration_open'],
                registration_close = d['registration_close'],
                is_active          = bool(d.get('is_active', True)),
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response(_program_payload(p), status=201)


class HQAdminProgramDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        try:
            p = SeasonProgram.objects.get(pk=pk)
        except SeasonProgram.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)
        for field in ('name', 'season', 'fee', 'early_bird_fee', 'early_bird_deadline',
                      'registration_open', 'registration_close', 'is_active'):
            if field in request.data:
                val = request.data[field]
                setattr(p, field, val if val != '' else None)
        p.save()
        return Response(_program_payload(p))


# ── Admin: athlete records ────────────────────────────────────

class HQAdminAthleteRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        qs = AthleteRecords.objects.all().order_by('athlete_name')
        return Response([{
            'id':            r.id,
            'name':          r.athlete_name,
            'event':         r.athlete_class,
            'mark':          str(r.athlete_mark),
            'age':           r.athlete_age,
            'age_group':     r.athlete_group,
            'year':          r.athlete_date,
            'meet':          r.athlete_meet,
        } for r in qs])


# ── Admin: users ──────────────────────────────────────────────

class HQAdminUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        return Response([{
            'id':         u.id,
            'name':       u.get_full_name() or u.username,
            'email':      u.email,
            'is_staff':   u.is_staff,
            'is_active':  u.is_active,
            'date_joined':u.date_joined.strftime('%b %d, %Y'),
            'registrations': HQRegistration.objects.filter(user=u).count(),
        } for u in User.objects.order_by('-date_joined')])


# ── Admin: contact messages ───────────────────────────────────

class HQAdminContactView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=403)
        return Response([{
            'id':         m.id,
            'name':       m.name,
            'email':      m.email,
            'subject':    m.subject,
            'message':    m.message,
            'created_at': m.created_at.strftime('%b %d, %Y'),
        } for m in ContactMessage.objects.order_by('-created_at')])


# ══════════════════════════════════════════════════════════════
# NEW MODEL API VIEWS
# ══════════════════════════════════════════════════════════════

def _staff_only(request):
    return not request.user.is_staff


class HQAdminFixturesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request):
            return Response({'error': 'Forbidden'}, status=403)
        qs = Fixture.objects.select_related(
            'home_team', 'away_team', 'division', 'season', 'venue'
        ).order_by('scheduled_datetime')
        return Response([{
            'id':       f.id,
            'home':     f.home_team.name,
            'away':     f.away_team.name,
            'division': str(f.division),
            'season':   f.season.name,
            'venue':    f.venue.name if f.venue else '—',
            'date':     f.scheduled_datetime.strftime('%b %d, %Y %H:%M'),
            'round':    f.round_number,
            'status':   f.status,
        } for f in qs])


class HQAdminRegistrationOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request):
            return Response({'error': 'Forbidden'}, status=403)
        qs = RegistrationOrder.objects.select_related('athlete', 'season').order_by('-registration_date')
        return Response([{
            'id':          r.id,
            'athlete':     r.athlete.full_name,
            'season':      r.season.season if r.season else '—',
            'order_num':   r.order_number,
            'status':      r.order_status,
            'fee':         str(r.registration_fee) if r.registration_fee else '—',
            'gross':       str(r.gross) if r.gross else '—',
            'date':        r.registration_date.strftime('%b %d, %Y') if r.registration_date else '—',
        } for r in qs])


class HQAdminAuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request):
            return Response({'error': 'Forbidden'}, status=403)
        qs = AuditLog.objects.select_related('user').order_by('-timestamp')[:200]
        return Response([{
            'id':         a.id,
            'user':       a.user.get_full_name() if a.user else 'System',
            'action':     a.action,
            'model':      a.model_name,
            'object':     a.object_repr,
            'ip':         a.ip_address or '—',
            'timestamp':  a.timestamp.strftime('%b %d, %Y %H:%M'),
        } for a in qs])


class HQAdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request):
            return Response({'error': 'Forbidden'}, status=403)
        qs = AnalyticsSnapshot.objects.order_by('-date', 'metric_name')[:500]
        return Response([{
            'id':        a.id,
            'date':      str(a.date),
            'metric':    a.metric_name,
            'dimension': a.dimension or '—',
            'value':     str(a.value),
        } for a in qs])


# ══════════════════════════════════════════════════════════════
# CRUD HELPERS
# ══════════════════════════════════════════════════════════════

def _sv(d, key, default=None):
    """Return dict value or default when key is absent/empty."""
    v = d.get(key)
    return default if (v == '' or v is None) else v

def _forbidden():
    return Response({'error': 'Forbidden'}, status=403)

def _not_found():
    return Response({'error': 'Not found.'}, status=404)


# ── FK options ────────────────────────────────────────────────

class HQAdminOptsView(APIView):
    """Returns [{id, label}] for populating FK select fields."""
    permission_classes = [IsAuthenticated]

    _MAP = {
        'teams':          (lambda: Team.objects.order_by('name'),         lambda o: o.name),
        'athletes':       (lambda: Athlete.objects.order_by('last_name'), lambda o: o.full_name),
        'users':          (lambda: User.objects.order_by('last_name'),    lambda o: (o.get_full_name() or o.email)),
        'leagues':        (lambda: League.objects.order_by('name'),       lambda o: o.name),
        'divisions':      (lambda: Division.objects.select_related('league').order_by('league','name'), lambda o: str(o)),
        'league-seasons': (lambda: LeagueSeason.objects.select_related('league').order_by('-start_date'), lambda o: str(o)),
        'venues':         (lambda: Venue.objects.order_by('name'),        lambda o: o.name),
        'season-configs': (lambda: SeasonConfig.objects.order_by('-season'), lambda o: f'Season {o.season}'),
        'organizations':  (lambda: Organization.objects.order_by('name'), lambda o: o.name),
    }

    def get(self, request, model):
        if _staff_only(request): return _forbidden()
        if model not in self._MAP:
            return Response({'error': 'Unknown model'}, status=400)
        qs_fn, label_fn = self._MAP[model]
        return Response([{'id': o.pk, 'label': label_fn(o)} for o in qs_fn()])


# ── Athletes CRUD ─────────────────────────────────────────────

class HQAdminAthletesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = Athlete.objects.select_related('team').order_by('last_name', 'first_name')
        return Response([{
            'id': a.id, 'name': a.full_name, 'dob': str(a.date_of_birth),
            'gender': a.get_gender_display(), 'team': a.team.name if a.team else '—',
            'status': a.status, 'waiver': a.waiver_signed,
            'registered': a.registration_date.strftime('%b %d, %Y'),
        } for a in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            a = Athlete.objects.create(
                first_name              = d['first_name'],
                middle_name             = d.get('middle_name', ''),
                last_name               = d['last_name'],
                date_of_birth           = d['date_of_birth'],
                gender                  = d['gender'],
                team_id                 = _sv(d, 'team_id'),
                status                  = d.get('status', 'active'),
                jersey_size             = d.get('jersey_size', ''),
                jersey_number           = _sv(d, 'jersey_number'),
                tank_size               = d.get('tank_size', ''),
                shorts_size             = d.get('shorts_size', ''),
                street_address_1        = d.get('street_address_1', ''),
                street_address_2        = d.get('street_address_2', ''),
                city                    = d.get('city', ''),
                state_province          = d.get('state_province', ''),
                postal_code             = d.get('postal_code', ''),
                country                 = d.get('country', 'United States'),
                secondary_email         = d.get('secondary_email', ''),
                volunteer_willing       = _sv(d, 'volunteer_willing'),
                medical_notes           = d.get('medical_notes', ''),
                medications             = d.get('medications', ''),
                has_allergies           = _sv(d, 'has_allergies'),
                allergies               = d.get('allergies', ''),
                has_medical_conditions  = _sv(d, 'has_medical_conditions'),
                physician_name          = d.get('physician_name', ''),
                physician_phone         = d.get('physician_phone', ''),
                hospital_of_choice      = d.get('hospital_of_choice', ''),
                insurance_provider      = d.get('insurance_provider', ''),
                insurance_group_number  = d.get('insurance_group_number', ''),
                insurance_policy_number = d.get('insurance_policy_number', ''),
                insurance_policy_holder = d.get('insurance_policy_holder', ''),
                insurance_phone         = d.get('insurance_phone', ''),
                emergency_contact_name          = d.get('emergency_contact_name', ''),
                emergency_contact_phone         = d.get('emergency_contact_phone', ''),
                emergency_contact_relationship  = d.get('emergency_contact_relationship', ''),
                secondary_contact_phone         = d.get('secondary_contact_phone', ''),
                waiver_signed           = bool(d.get('waiver_signed', False)),
                waiver_signed_date      = _sv(d, 'waiver_signed_date'),
                sportsengine_id         = d.get('sportsengine_id', ''),
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': a.id, 'name': a.full_name}, status=201)


_ATHLETE_BOOL_FIELDS = ('waiver_signed', 'has_allergies', 'has_medical_conditions', 'volunteer_willing')
_ATHLETE_STR_FIELDS  = (
    'first_name','middle_name','last_name','date_of_birth','gender','status',
    'jersey_size','tank_size','shorts_size',
    'street_address_1','street_address_2','city','state_province','postal_code','country',
    'secondary_email',
    'medical_notes','medications','allergies',
    'physician_name','physician_phone','hospital_of_choice',
    'insurance_provider','insurance_group_number','insurance_policy_number',
    'insurance_policy_holder','insurance_phone',
    'emergency_contact_name','emergency_contact_phone','emergency_contact_relationship',
    'secondary_contact_phone',
    'waiver_signed_date','sportsengine_id',
)


class HQAdminAthleteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return Athlete.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: a = self._obj(pk)
        except Athlete.DoesNotExist: return _not_found()
        return Response({
            'id': a.id,
            'first_name': a.first_name, 'middle_name': a.middle_name, 'last_name': a.last_name,
            'date_of_birth': str(a.date_of_birth), 'gender': a.gender,
            'team_id': a.team_id, 'status': a.status,
            'jersey_size': a.jersey_size, 'jersey_number': a.jersey_number,
            'tank_size': a.tank_size, 'shorts_size': a.shorts_size,
            'street_address_1': a.street_address_1, 'street_address_2': a.street_address_2,
            'city': a.city, 'state_province': a.state_province,
            'postal_code': a.postal_code, 'country': a.country,
            'secondary_email': a.secondary_email,
            'volunteer_willing': a.volunteer_willing,
            'medical_notes': a.medical_notes, 'medications': a.medications,
            'has_allergies': a.has_allergies, 'allergies': a.allergies,
            'has_medical_conditions': a.has_medical_conditions,
            'physician_name': a.physician_name, 'physician_phone': a.physician_phone,
            'hospital_of_choice': a.hospital_of_choice,
            'insurance_provider': a.insurance_provider,
            'insurance_group_number': a.insurance_group_number,
            'insurance_policy_number': a.insurance_policy_number,
            'insurance_policy_holder': a.insurance_policy_holder,
            'insurance_phone': a.insurance_phone,
            'emergency_contact_name': a.emergency_contact_name,
            'emergency_contact_phone': a.emergency_contact_phone,
            'emergency_contact_relationship': a.emergency_contact_relationship,
            'secondary_contact_phone': a.secondary_contact_phone,
            'waiver_signed': a.waiver_signed,
            'waiver_signed_date': str(a.waiver_signed_date) if a.waiver_signed_date else '',
            'sportsengine_id': a.sportsengine_id,
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: a = self._obj(pk)
        except Athlete.DoesNotExist: return _not_found()
        d = request.data
        for f in _ATHLETE_STR_FIELDS:
            if f in d: setattr(a, f, d[f] if d[f] is not None else '')
        for f in _ATHLETE_BOOL_FIELDS:
            if f in d: setattr(a, f, bool(d[f]) if d[f] is not None else None)
        if 'team_id'      in d: a.team_id      = _sv(d, 'team_id')
        if 'jersey_number' in d: a.jersey_number = _sv(d, 'jersey_number')
        try: a.save()
        except Exception as e: return Response({'error': str(e)}, status=400)
        return Response({'id': a.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except Athlete.DoesNotExist: return _not_found()
        return Response(status=204)


# ── Teams CRUD ────────────────────────────────────────────────

class HQAdminTeamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = Team.objects.select_related('head_coach').order_by('age_group', 'name')
        return Response([{
            'id': t.id, 'name': t.name, 'age_group': t.age_group, 'season': t.season,
            'head_coach': t.head_coach.get_full_name() if t.head_coach else '—',
            'status': t.status, 'athletes': t.current_athletes, 'max': t.max_athletes,
        } for t in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            t = Team.objects.create(
                name             = d['name'],
                age_group        = d['age_group'],
                season           = d.get('season', '2025'),
                head_coach_id    = _sv(d, 'head_coach_id'),
                status           = d.get('status', 'active'),
                max_athletes     = int(d.get('max_athletes', 30)),
                team_color       = d.get('team_color', '#c8f135'),
                practice_schedule= d.get('practice_schedule') or {},
                disciplines      = d.get('disciplines') or [],
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': t.id, 'name': t.name}, status=201)


class HQAdminTeamDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return Team.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: t = self._obj(pk)
        except Team.DoesNotExist: return _not_found()
        return Response({
            'id': t.id, 'name': t.name, 'age_group': t.age_group, 'season': t.season,
            'head_coach_id': t.head_coach_id, 'status': t.status,
            'max_athletes': t.max_athletes, 'current_athletes': t.current_athletes,
            'team_color': t.team_color,
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: t = self._obj(pk)
        except Team.DoesNotExist: return _not_found()
        d = request.data
        for f in ('name','age_group','season','status','team_color'):
            if f in d: setattr(t, f, d[f])
        if 'head_coach_id' in d: t.head_coach_id = _sv(d, 'head_coach_id')
        if 'max_athletes'  in d: t.max_athletes  = int(d['max_athletes'])
        try: t.save()
        except Exception as e: return Response({'error': str(e)}, status=400)
        return Response({'id': t.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except Team.DoesNotExist: return _not_found()
        return Response(status=204)


# ── Events CRUD ───────────────────────────────────────────────

class HQAdminEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = Event.objects.order_by('start_datetime')
        return Response([{
            'id': e.id, 'name': e.name, 'type': e.get_event_type_display(),
            'venue': e.venue_name, 'start': e.start_datetime.strftime('%b %d, %Y %H:%M'),
            'published': e.is_published, 'cancelled': e.is_cancelled,
            'registrations': e.registrations.count(),
        } for e in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            e = Event.objects.create(
                name                  = d['name'],
                event_type            = d['event_type'],
                description           = d.get('description', ''),
                start_datetime        = d['start_datetime'],
                end_datetime          = d['end_datetime'],
                registration_deadline = _sv(d, 'registration_deadline'),
                venue_name            = d.get('venue_name', ''),
                address               = d.get('address', ''),
                location_url          = d.get('location_url', ''),
                all_teams             = bool(d.get('all_teams', False)),
                is_published          = bool(d.get('is_published', True)),
                is_cancelled          = bool(d.get('is_cancelled', False)),
                cancellation_reason   = d.get('cancellation_reason', ''),
                requires_registration = bool(d.get('requires_registration', False)),
                max_participants      = _sv(d, 'max_participants'),
                registration_fee      = d.get('registration_fee', 0),
                created_by            = request.user,
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': e.id, 'name': e.name}, status=201)


class HQAdminEventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return Event.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: e = self._obj(pk)
        except Event.DoesNotExist: return _not_found()
        fmt = lambda dt: dt.strftime('%Y-%m-%dT%H:%M') if dt else ''
        return Response({
            'id': e.id, 'name': e.name, 'event_type': e.event_type,
            'description': e.description,
            'start_datetime': fmt(e.start_datetime),
            'end_datetime': fmt(e.end_datetime),
            'registration_deadline': fmt(e.registration_deadline),
            'venue_name': e.venue_name, 'address': e.address,
            'location_url': e.location_url,
            'all_teams': e.all_teams,
            'is_published': e.is_published, 'is_cancelled': e.is_cancelled,
            'cancellation_reason': e.cancellation_reason,
            'requires_registration': e.requires_registration,
            'max_participants': e.max_participants,
            'registration_fee': str(e.registration_fee),
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: e = self._obj(pk)
        except Event.DoesNotExist: return _not_found()
        d = request.data
        for f in ('name','event_type','description','start_datetime','end_datetime',
                  'venue_name','address','location_url','registration_fee','cancellation_reason'):
            if f in d: setattr(e, f, d[f])
        for bf in ('is_published','is_cancelled','requires_registration','all_teams'):
            if bf in d: setattr(e, bf, bool(d[bf]))
        if 'registration_deadline' in d: e.registration_deadline = _sv(d, 'registration_deadline')
        if 'max_participants'      in d: e.max_participants       = _sv(d, 'max_participants')
        try: e.save()
        except Exception as ex: return Response({'error': str(ex)}, status=400)
        return Response({'id': e.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except Event.DoesNotExist: return _not_found()
        return Response(status=204)


# ── Payments CRUD ─────────────────────────────────────────────

class HQAdminPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = Payment.objects.select_related('athlete', 'season').order_by('-created_at')
        return Response([{
            'id': p.id, 'athlete': p.athlete.full_name, 'season': p.season.season,
            'amount': str(p.amount), 'fee_tier': p.get_fee_tier_display(),
            'status': p.status, 'method': p.payment_method or '—',
            'due_date': str(p.due_date), 'invoice': p.invoice_number,
        } for p in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            p = Payment.objects.create(
                athlete_id    = d['athlete_id'],
                season_id     = d['season_id'],
                amount        = d['amount'],
                fee_tier      = d['fee_tier'],
                status        = d.get('status', 'pending'),
                payment_method= _sv(d, 'payment_method'),
                due_date      = d['due_date'],
                invoice_number= d['invoice_number'],
                notes         = d.get('notes', ''),
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': p.id}, status=201)


class HQAdminPaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return Payment.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: p = self._obj(pk)
        except Payment.DoesNotExist: return _not_found()
        return Response({
            'id': p.id, 'athlete_id': p.athlete_id, 'season_id': p.season_id,
            'amount': str(p.amount), 'fee_tier': p.fee_tier, 'status': p.status,
            'payment_method': p.payment_method or '',
            'stripe_payment_intent_id': p.stripe_payment_intent_id,
            'due_date': str(p.due_date),
            'paid_at': p.paid_at.strftime('%Y-%m-%dT%H:%M') if p.paid_at else '',
            'invoice_number': p.invoice_number, 'notes': p.notes,
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: p = self._obj(pk)
        except Payment.DoesNotExist: return _not_found()
        d = request.data
        for f in ('amount','fee_tier','status','due_date','invoice_number','notes','stripe_payment_intent_id'):
            if f in d: setattr(p, f, d[f])
        if 'payment_method' in d: p.payment_method = _sv(d, 'payment_method')
        if 'athlete_id'     in d: p.athlete_id     = d['athlete_id']
        if 'season_id'      in d: p.season_id      = d['season_id']
        if 'paid_at'        in d: p.paid_at         = _sv(d, 'paid_at')
        try: p.save()
        except Exception as e: return Response({'error': str(e)}, status=400)
        return Response({'id': p.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except Payment.DoesNotExist: return _not_found()
        return Response(status=204)


# ── Announcements CRUD ────────────────────────────────────────

class HQAdminAnnouncementsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = Announcement.objects.select_related('published_by','target_team').order_by('-published_at')
        return Response([{
            'id': a.id, 'title': a.title, 'audience': a.get_audience_display(),
            'team': a.target_team.name if a.target_team else '—',
            'published': a.is_published, 'send_email': a.send_email, 'send_sms': a.send_sms,
            'by': a.published_by.get_full_name() if a.published_by else '—',
            'date': a.published_at.strftime('%b %d, %Y'),
        } for a in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            a = Announcement.objects.create(
                title       = d['title'],
                content     = d.get('content', ''),
                audience    = d.get('audience', 'all'),
                target_team_id= _sv(d, 'target_team_id'),
                is_published= bool(d.get('is_published', True)),
                send_email  = bool(d.get('send_email', False)),
                send_sms    = bool(d.get('send_sms', False)),
                published_by= request.user,
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': a.id, 'title': a.title}, status=201)


class HQAdminAnnouncementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return Announcement.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: a = self._obj(pk)
        except Announcement.DoesNotExist: return _not_found()
        return Response({
            'id': a.id, 'title': a.title, 'content': a.content,
            'audience': a.audience, 'target_team_id': a.target_team_id,
            'is_published': a.is_published, 'send_email': a.send_email, 'send_sms': a.send_sms,
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: a = self._obj(pk)
        except Announcement.DoesNotExist: return _not_found()
        d = request.data
        for f in ('title','content','audience'):
            if f in d: setattr(a, f, d[f])
        for bf in ('is_published','send_email','send_sms'):
            if bf in d: setattr(a, bf, bool(d[bf]))
        if 'target_team_id' in d: a.target_team_id = _sv(d, 'target_team_id')
        try: a.save()
        except Exception as e: return Response({'error': str(e)}, status=400)
        return Response({'id': a.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except Announcement.DoesNotExist: return _not_found()
        return Response(status=204)


# ── Compliance CRUD ───────────────────────────────────────────

class HQAdminComplianceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = ComplianceRecord.objects.select_related('user','athlete').order_by('expiry_date')
        return Response([{
            'id': c.id, 'subject': str(c.user or c.athlete or '—'),
            'type': c.get_record_type_display(), 'status': c.status,
            'expiry': str(c.expiry_date) if c.expiry_date else '—',
            'days_left': c.days_until_expiry, 'issuer': c.issuing_body,
        } for c in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            c = ComplianceRecord.objects.create(
                user_id      = _sv(d, 'user_id'),
                athlete_id   = _sv(d, 'athlete_id'),
                record_type  = d['record_type'],
                status       = d.get('status', 'pending'),
                issuing_body = d.get('issuing_body', ''),
                issue_date   = _sv(d, 'issue_date'),
                expiry_date  = _sv(d, 'expiry_date'),
                notes        = d.get('notes', ''),
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': c.id}, status=201)


class HQAdminComplianceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return ComplianceRecord.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: c = self._obj(pk)
        except ComplianceRecord.DoesNotExist: return _not_found()
        return Response({
            'id': c.id, 'user_id': c.user_id, 'athlete_id': c.athlete_id,
            'record_type': c.record_type, 'status': c.status,
            'issuing_body': c.issuing_body, 'document_number': c.document_number,
            'issue_date': str(c.issue_date) if c.issue_date else '',
            'expiry_date': str(c.expiry_date) if c.expiry_date else '',
            'notes': c.notes,
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: c = self._obj(pk)
        except ComplianceRecord.DoesNotExist: return _not_found()
        d = request.data
        for f in ('record_type','status','issuing_body','document_number','notes'):
            if f in d: setattr(c, f, d[f])
        for df in ('issue_date','expiry_date'):
            if df in d: setattr(c, df, _sv(d, df))
        if 'user_id'    in d: c.user_id    = _sv(d, 'user_id')
        if 'athlete_id' in d: c.athlete_id = _sv(d, 'athlete_id')
        try: c.save()
        except Exception as e: return Response({'error': str(e)}, status=400)
        return Response({'id': c.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except ComplianceRecord.DoesNotExist: return _not_found()
        return Response(status=204)


# ── Incidents CRUD ────────────────────────────────────────────

class HQAdminIncidentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = IncidentReport.objects.order_by('-incident_date')
        return Response([{
            'id': i.id, 'title': i.title, 'type': i.get_incident_type_display(),
            'severity': i.severity, 'status': i.status,
            'date': i.incident_date.strftime('%b %d, %Y'),
            'athlete': i.involved_athlete.full_name if i.involved_athlete else '—',
            'location': i.location,
        } for i in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            i = IncidentReport.objects.create(
                title               = d['title'],
                incident_type       = d.get('incident_type', 'injury'),
                severity            = d.get('severity', 'low'),
                status              = d.get('status', 'open'),
                incident_date       = d['incident_date'],
                location            = d.get('location', ''),
                description         = d.get('description', ''),
                action_taken        = d.get('action_taken', ''),
                witnesses           = d.get('witnesses', ''),
                follow_up_required  = bool(d.get('follow_up_required', False)),
                follow_up_notes     = d.get('follow_up_notes', ''),
                escalation_notes    = d.get('escalation_notes', ''),
                involved_athlete_id = _sv(d, 'involved_athlete_id'),
                involved_user_id    = _sv(d, 'involved_user_id'),
                assigned_to_id      = _sv(d, 'assigned_to_id'),
                reported_by         = request.user,
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': i.id, 'title': i.title}, status=201)


class HQAdminIncidentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return IncidentReport.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: i = self._obj(pk)
        except IncidentReport.DoesNotExist: return _not_found()
        return Response({
            'id': i.id, 'title': i.title, 'incident_type': i.incident_type,
            'severity': i.severity, 'status': i.status,
            'incident_date': i.incident_date.strftime('%Y-%m-%dT%H:%M'),
            'location': i.location, 'description': i.description,
            'action_taken': i.action_taken, 'witnesses': i.witnesses,
            'follow_up_required': i.follow_up_required,
            'follow_up_notes': i.follow_up_notes,
            'escalation_notes': i.escalation_notes,
            'involved_athlete_id': i.involved_athlete_id,
            'involved_user_id': i.involved_user_id,
            'assigned_to_id': i.assigned_to_id,
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: i = self._obj(pk)
        except IncidentReport.DoesNotExist: return _not_found()
        d = request.data
        for f in ('title','incident_type','severity','status','incident_date','location',
                  'description','action_taken','witnesses','follow_up_notes','escalation_notes'):
            if f in d: setattr(i, f, d[f])
        if 'follow_up_required'  in d: i.follow_up_required  = bool(d['follow_up_required'])
        if 'involved_athlete_id' in d: i.involved_athlete_id = _sv(d, 'involved_athlete_id')
        if 'involved_user_id'    in d: i.involved_user_id    = _sv(d, 'involved_user_id')
        if 'assigned_to_id'      in d: i.assigned_to_id      = _sv(d, 'assigned_to_id')
        try: i.save()
        except Exception as e: return Response({'error': str(e)}, status=400)
        return Response({'id': i.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except IncidentReport.DoesNotExist: return _not_found()
        return Response(status=204)


# ── Transfers (status update only) ───────────────────────────

class HQAdminTransfersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = TransferRequest.objects.select_related('athlete','from_team','to_team').order_by('-created_at')
        return Response([{
            'id': t.id, 'athlete': t.athlete.full_name,
            'from_team': t.from_team.name if t.from_team else '—',
            'to_team': t.to_team.name, 'status': t.status,
            'date': t.created_at.strftime('%b %d, %Y'),
        } for t in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            t = TransferRequest.objects.create(
                athlete_id   = d['athlete_id'],
                from_team_id = _sv(d, 'from_team_id'),
                to_team_id   = d['to_team_id'],
                reason       = d.get('reason', ''),
                status       = d.get('status', 'pending'),
                requested_by = request.user,
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': t.id}, status=201)


class HQAdminTransferDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return TransferRequest.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: t = self._obj(pk)
        except TransferRequest.DoesNotExist: return _not_found()
        return Response({
            'id': t.id, 'athlete_id': t.athlete_id,
            'from_team_id': t.from_team_id, 'to_team_id': t.to_team_id,
            'status': t.status, 'reason': t.reason, 'admin_notes': t.admin_notes,
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: t = self._obj(pk)
        except TransferRequest.DoesNotExist: return _not_found()
        d = request.data
        if 'status' in d: t.status = d['status']
        if 'admin_notes' in d: t.admin_notes = d['admin_notes']
        if 'reason' in d: t.reason = d['reason']
        if 'to_team_id' in d: t.to_team_id = d['to_team_id']
        if 'from_team_id' in d: t.from_team_id = _sv(d, 'from_team_id')
        try: t.save()
        except Exception as e: return Response({'error': str(e)}, status=400)
        return Response({'id': t.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except TransferRequest.DoesNotExist: return _not_found()
        return Response(status=204)


# ── Leagues CRUD ──────────────────────────────────────────────

class HQAdminLeaguesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = League.objects.select_related('organization').order_by('name')
        return Response([{
            'id': l.id, 'name': l.name, 'sport': l.sport,
            'org': l.organization.name if l.organization else '—',
            'active': l.is_active, 'divisions': l.divisions.count(),
        } for l in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            l = League.objects.create(
                name           = d['name'],
                sport          = d.get('sport', ''),
                description    = d.get('description', ''),
                organization_id= _sv(d, 'organization_id'),
                is_active      = bool(d.get('is_active', True)),
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': l.id, 'name': l.name}, status=201)


class HQAdminLeagueDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return League.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: l = self._obj(pk)
        except League.DoesNotExist: return _not_found()
        return Response({
            'id': l.id, 'name': l.name, 'sport': l.sport,
            'description': l.description, 'organization_id': l.organization_id,
            'is_active': l.is_active,
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: l = self._obj(pk)
        except League.DoesNotExist: return _not_found()
        d = request.data
        for f in ('name','sport','description'):
            if f in d: setattr(l, f, d[f])
        if 'is_active' in d: l.is_active = bool(d['is_active'])
        if 'organization_id' in d: l.organization_id = _sv(d, 'organization_id')
        try: l.save()
        except Exception as e: return Response({'error': str(e)}, status=400)
        return Response({'id': l.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except League.DoesNotExist: return _not_found()
        return Response(status=204)


# ── Organizations CRUD ────────────────────────────────────────

class HQAdminOrganizationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if _staff_only(request): return _forbidden()
        qs = Organization.objects.order_by('name')
        return Response([{
            'id': o.id, 'name': o.name, 'email': o.email, 'phone': o.phone,
            'website': o.website, 'active': o.is_active, 'members': o.members.count(),
        } for o in qs])

    def post(self, request):
        if _staff_only(request): return _forbidden()
        d = request.data
        try:
            o = Organization.objects.create(
                name      = d['name'],
                slug      = d['slug'],
                email     = d.get('email', ''),
                phone     = d.get('phone', ''),
                website   = d.get('website', ''),
                address   = d.get('address', ''),
                is_active = bool(d.get('is_active', True)),
            )
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response({'id': o.id, 'name': o.name}, status=201)


class HQAdminOrgDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _obj(self, pk):
        return Organization.objects.get(pk=pk)

    def get(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: o = self._obj(pk)
        except Organization.DoesNotExist: return _not_found()
        return Response({
            'id': o.id, 'name': o.name, 'slug': o.slug,
            'description': o.description,
            'email': o.email, 'phone': o.phone,
            'website': o.website, 'address': o.address,
            'is_active': o.is_active,
        })

    def patch(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: o = self._obj(pk)
        except Organization.DoesNotExist: return _not_found()
        d = request.data
        for f in ('name','slug','description','email','phone','website','address'):
            if f in d: setattr(o, f, d[f])
        if 'is_active' in d: o.is_active = bool(d['is_active'])
        try: o.save()
        except Exception as e: return Response({'error': str(e)}, status=400)
        return Response({'id': o.id})

    def delete(self, request, pk):
        if _staff_only(request): return _forbidden()
        try: self._obj(pk).delete()
        except Organization.DoesNotExist: return _not_found()
        return Response(status=204)
