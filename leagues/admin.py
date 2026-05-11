from django.contrib import admin
from .models import Venue, League, Division, LeagueSeason, CompetitionRule, TeamLeagueAssignment, Fixture, RefereeAssignment, Match, MatchEvent, Standing, Bracket

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'surface_type', 'capacity', 'is_active']
    list_filter = ['is_active', 'surface_type']

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name', 'sport', 'organization', 'is_active']
    list_filter = ['is_active', 'sport']

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'league', 'age_group', 'gender_category', 'max_teams']

@admin.register(LeagueSeason)
class LeagueSeasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'league', 'status', 'start_date', 'end_date', 'is_active']
    list_filter = ['status', 'is_active']

@admin.register(CompetitionRule)
class CompetitionRuleAdmin(admin.ModelAdmin):
    list_display = ['rule_name', 'league', 'division', 'rule_value', 'order']

@admin.register(TeamLeagueAssignment)
class TeamLeagueAssignmentAdmin(admin.ModelAdmin):
    list_display = ['team', 'division', 'season', 'status']
    list_filter = ['status']

@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'division', 'season', 'scheduled_datetime', 'status']
    list_filter = ['status', 'division']

@admin.register(RefereeAssignment)
class RefereeAssignmentAdmin(admin.ModelAdmin):
    list_display = ['referee', 'fixture', 'role', 'status']
    list_filter = ['role', 'status']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['fixture', 'home_score', 'away_score', 'status']
    list_filter = ['status']

@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ['match', 'event_type', 'player_name', 'minute']
    list_filter = ['event_type']

@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ['team', 'division', 'season', 'played', 'wins', 'draws', 'losses', 'points']

@admin.register(Bracket)
class BracketAdmin(admin.ModelAdmin):
    list_display = ['division', 'season', 'bracket_type', 'status']
    list_filter = ['bracket_type', 'status']
