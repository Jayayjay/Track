from django.db import models


class Venue(models.Model):
    SURFACE_CHOICES = (
        ('grass', 'Grass'), ('turf', 'Artificial Turf'), ('track', 'Track'),
        ('pool', 'Pool'), ('gym', 'Gymnasium'), ('indoor', 'Indoor Court'), ('other', 'Other'),
    )

    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    surface_type = models.CharField(max_length=20, choices=SURFACE_CHOICES, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'venues'
        ordering = ['name']

    def __str__(self):
        return self.name


class League(models.Model):
    name = models.CharField(max_length=200)
    sport = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(
        'organizations.Organization', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='leagues',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leagues'
        ordering = ['name']

    def __str__(self):
        return self.name


class Division(models.Model):
    GENDER_CHOICES = (
        ('mixed', 'Mixed'), ('male', 'Male'), ('female', 'Female'),
    )

    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='divisions')
    name = models.CharField(max_length=100)
    age_group = models.CharField(max_length=20, blank=True)
    gender_category = models.CharField(max_length=10, choices=GENDER_CHOICES, default='mixed')
    description = models.TextField(blank=True)
    max_teams = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'divisions'
        ordering = ['league', 'name']
        unique_together = [['league', 'name']]

    def __str__(self):
        return f"{self.league.name} — {self.name}"


class LeagueSeason(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'), ('registration', 'Registration Open'),
        ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled'),
    )

    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='seasons')
    name = models.CharField(max_length=100)  # e.g. "Spring 2026"
    start_date = models.DateField()
    end_date = models.DateField()
    registration_open = models.DateField(null=True, blank=True)
    registration_close = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'league_seasons'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.league.name} — {self.name}"


class CompetitionRule(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='rules', null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='rules', null=True, blank=True)
    rule_name = models.CharField(max_length=100)
    rule_value = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'competition_rules'
        ordering = ['order']

    def __str__(self):
        return self.rule_name


class TeamLeagueAssignment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'), ('withdrawn', 'Withdrawn'), ('pending', 'Pending'),
    )

    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='league_assignments')
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='team_assignments')
    season = models.ForeignKey(LeagueSeason, on_delete=models.CASCADE, related_name='team_assignments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'team_league_assignments'
        unique_together = [['team', 'division', 'season']]

    def __str__(self):
        return f"{self.team.name} → {self.division} ({self.season.name})"


class Fixture(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'), ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'), ('completed', 'Completed'),
    )

    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='fixtures')
    season = models.ForeignKey(LeagueSeason, on_delete=models.CASCADE, related_name='fixtures')
    home_team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='home_fixtures')
    away_team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='away_fixtures')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True, related_name='fixtures')
    scheduled_datetime = models.DateTimeField()
    round_number = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fixtures'
        ordering = ['scheduled_datetime', 'round_number']
        indexes = [
            models.Index(fields=['division', 'season', 'round_number']),
            models.Index(fields=['scheduled_datetime']),
        ]

    def __str__(self):
        return f"R{self.round_number}: {self.home_team.name} vs {self.away_team.name}"


class RefereeAssignment(models.Model):
    ROLE_CHOICES = (
        ('head', 'Head Referee'), ('assistant', 'Assistant Referee'), ('timekeeper', 'Timekeeper'),
    )
    STATUS_CHOICES = (
        ('assigned', 'Assigned'), ('confirmed', 'Confirmed'), ('declined', 'Declined'),
    )

    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE, related_name='referee_assignments')
    referee = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='referee_assignments')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='head')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'referee_assignments'
        unique_together = [['fixture', 'referee']]

    def __str__(self):
        return f"{self.referee.get_full_name()} — {self.fixture} ({self.role})"


class Match(models.Model):
    STATUS_CHOICES = (
        ('not_started', 'Not Started'), ('in_progress', 'In Progress'),
        ('half_time', 'Half Time'), ('completed', 'Completed'), ('abandoned', 'Abandoned'),
    )

    fixture = models.OneToOneField(Fixture, on_delete=models.CASCADE, related_name='match')
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matches'

    def __str__(self):
        return f"{self.fixture} [{self.home_score}–{self.away_score}]"

    @property
    def result(self):
        if self.home_score > self.away_score:
            return 'home_win'
        if self.away_score > self.home_score:
            return 'away_win'
        return 'draw'


class MatchEvent(models.Model):
    EVENT_TYPES = (
        ('goal', 'Goal'), ('own_goal', 'Own Goal'), ('yellow_card', 'Yellow Card'),
        ('red_card', 'Red Card'), ('substitution', 'Substitution'),
        ('penalty', 'Penalty'), ('penalty_miss', 'Penalty Miss'), ('note', 'Note'),
    )

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True)
    player_name = models.CharField(max_length=200, blank=True)
    minute = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'match_events'
        ordering = ['minute', 'created_at']

    def __str__(self):
        return f"{self.event_type} — {self.player_name} ({self.minute}')"


class Standing(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='standings')
    season = models.ForeignKey(LeagueSeason, on_delete=models.CASCADE, related_name='standings')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='standings')
    played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        db_table = 'standings'
        unique_together = [['division', 'season', 'team']]
        ordering = ['-points', '-goals_for']

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    def __str__(self):
        return f"{self.team.name} — {self.points}pts ({self.division})"


class Bracket(models.Model):
    BRACKET_TYPES = (
        ('single_elimination', 'Single Elimination'),
        ('double_elimination', 'Double Elimination'),
        ('round_robin', 'Round Robin'),
    )
    STATUS_CHOICES = (
        ('draft', 'Draft'), ('active', 'Active'), ('completed', 'Completed'),
    )

    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='brackets')
    season = models.ForeignKey(LeagueSeason, on_delete=models.CASCADE, related_name='brackets')
    bracket_type = models.CharField(max_length=30, choices=BRACKET_TYPES, default='single_elimination')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    bracket_data = models.JSONField(default=dict)  # full bracket tree structure
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brackets'

    def __str__(self):
        return f"{self.bracket_type} — {self.division} ({self.season.name})"
