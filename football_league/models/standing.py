from odoo import models, fields, api, _

class SoccerStandings(models.Model):
    _name = 'soccer.standings'
    _description = 'Soccer Standings'
    _order = 'points desc, goal_difference desc, goals_for desc'

    club_id = fields.Many2one('soccer.club', string='Club', required=True)
    matches_played = fields.Integer(string='Matches Played', default=0)
    wins = fields.Integer(string='Wins', default=0)
    draws = fields.Integer(string='Draws', default=0)
    losses = fields.Integer(string='Losses', default=0)
    goals_for = fields.Integer(string='Goals For', default=0)
    goals_against = fields.Integer(string='Goals Against', default=0)
    points = fields.Integer(string='Points', default=0)
    goal_difference = fields.Integer(string='Goal Difference', compute='_compute_goal_difference', store=True)
    rank = fields.Integer(string='Rank', compute='_compute_rank', store=True)

    # fungsi untuk update goal_difference
    @api.depends('goals_for', 'goals_against')
    def _compute_goal_difference(self):
        for record in self:
            record.goal_difference = record.goals_for - record.goals_against

    # fungsi untuk update ranking
    @api.depends('points', 'goal_difference', 'goals_for')
    def _compute_rank(self):
        # Recalculate the rank for all teams
        standings = self.search([], order='points desc, goal_difference desc, goals_for desc')
        rank = 1
        for standing in standings:
            standing.rank = rank
            rank += 1

    # fungsi untuk update Standings
    @api.model
    def update_standings(self, match_line):
        home_standings = self.search([('club_id', '=', match_line.home_team.id)])
        away_standings = self.search([('club_id', '=', match_line.away_team.id)])

        if not home_standings:
            home_standings = self.create({'club_id': match_line.home_team.id})
        if not away_standings:
            away_standings = self.create({'club_id': match_line.away_team.id})

        home_standings.matches_played += 1
        away_standings.matches_played += 1

        home_standings.goals_for += match_line.home_score
        home_standings.goals_against += match_line.away_score
        away_standings.goals_for += match_line.away_score
        away_standings.goals_against += match_line.home_score

        if match_line.home_score > match_line.away_score:
            home_standings.wins += 1
            home_standings.points += 3
            away_standings.losses += 1
        elif match_line.home_score < match_line.away_score:
            away_standings.wins += 1
            away_standings.points += 3
            home_standings.losses += 1
        else:
            home_standings.draws += 1
            away_standings.draws += 1
            home_standings.points += 1
            away_standings.points += 1

        # Recalculate ranks only for the affected teams
        self._compute_rank_for_teams([home_standings.id, away_standings.id])

    # fungsi untuk update Standings
    def _compute_rank_for_teams(self, team_ids):
        # Get all standings, including the ones that need updating
        standings = self.search([], order='points desc, goal_difference desc, goals_for desc')

        rank = 1
        for standing in standings:
            standing.rank = rank
            rank += 1