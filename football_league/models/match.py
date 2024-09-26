from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SoccerMatch(models.Model):
    _name = 'soccer.match'
    _description = 'Soccer Match'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    state = fields.Selection(selection=[('draft', 'Draft'),('confirmed', 'Confirmed')], string='Status', default='draft')
    match_date = fields.Date(string='Match Date', required=True, default=fields.Date.context_today)
    match_ids = fields.One2many('soccer.match.line', 'match_id', string='Matches')
    is_multiple = fields.Boolean('Apakah akan membuat banyak match?')
    home_team = fields.Many2one('soccer.club', string='Home Team')
    away_team = fields.Many2one('soccer.club', string='Away Team')
    home_score = fields.Integer(string='Home Score')
    away_score = fields.Integer(string='Away Score')
    existing_clubs = fields.Many2many('soccer.club', string='Existing Clubs', compute='_compute_existing_clubs')


    # menyimpan data club yang sudah di assign. agar yang di assign tidak dapat di pilih lagi
    @api.depends('match_ids')
    def _compute_existing_clubs(self):
        for rec in self:
            existing_clubs = self.env['soccer.club']
            for line in rec.match_ids:
                if line.home_team:
                    existing_clubs |= line.home_team
                if line.away_team:
                    existing_clubs |= line.away_team
            rec.existing_clubs = existing_clubs

    # cek apakah input single match atau multiple
    @api.constrains('is_multiple')
    def _check_multiple_or_single(self):
        for match in self:
            if match.is_multiple and not match.match_ids:
                raise ValidationError("You must add at least one match when multiple matches are selected.")

    # Fungsi untuk melakukan confirm pada form match, data yang di buat harus di confirm agar dapat di proses.
    def confirm_match(self):
        if self.is_multiple:
            for line in self.match_ids:
                self.env['soccer.standings'].update_standings(line)
        else:
            match_line_vals = {
                'home_team': self.home_team.id,
                'away_team': self.away_team.id,
                'home_score': self.home_score,
                'away_score': self.away_score,
            }
            match_line = self.env['soccer.match.line'].create(match_line_vals)
            self.env['soccer.standings'].update_standings(match_line)
        self.state='confirmed'


class SoccerMatchLine(models.Model):
    _name = 'soccer.match.line'
    _description = 'Soccer Match Line'

    match_id = fields.Many2one('soccer.match', string='Match Day')
    home_team = fields.Many2one('soccer.club', string='Home Team', required=True)
    away_team = fields.Many2one('soccer.club', string='Away Team', required=True)
    home_score = fields.Integer(string='Home Score', required=True)
    away_score = fields.Integer(string='Away Score', required=True)
    domain_team = fields.Many2many('soccer.club', compute='_compute_domain_club')
    existing_clubs = fields.Many2many('soccer.club', related='match_id.existing_clubs', string="Existing Clubs")

    # Fungsi untuk domain club yang akan di pilih
    @api.depends('away_team', 'home_team')
    def _compute_domain_club(self):
        for rec in self:
            existing_clubs = rec.existing_clubs.ids
            if existing_clubs:
                domains_match = self.env['soccer.club'].search([
                    ('id', 'not in', existing_clubs)
                ])
                rec.domain_team = [(6, 0, domains_match.ids)]
            else:
                domains_match = self.env['soccer.club'].search([])
                rec.domain_team = rec.domain_team = [(6, 0, domains_match.ids)]

    # cek apakah home team dan away team sama
    @api.constrains('home_team', 'away_team', 'match_id')
    def _check_teams(self):
        for record in self:
            if record.home_team == record.away_team:
                raise ValidationError("Home team and away team must be different!")
            domain = [
                ('match_id', '=', record.match_id.id),
                ('id', '!=', record.id),
                '|',
                '&', ('home_team', '=', record.home_team.id), ('away_team', '=', record.away_team.id),
                '&', ('home_team', '=', record.away_team.id), ('away_team', '=', record.home_team.id)
            ]
            if self.search_count(domain) > 0:
                raise ValidationError("This match already exists for the selected date!")
