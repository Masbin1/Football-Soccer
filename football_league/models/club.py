from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SoccerClub(models.Model):
    _name = 'soccer.club'
    _description = 'Soccer Club'

    name = fields.Char(string='Club Name', required=True)
    city = fields.Char(string='Club City', required=True)

    # Fungsi untuk melakukan validasi
    @api.constrains('name', 'city')
    def _check_name_city_uniqueness(self):
        for record in self:
            # Check name and city combination uniqueness
            same_name_city = self.search([
                ('id', '!=', record.id),
                ('name', '=', record.name),
                ('city', '=', record.city)
            ])
            if same_name_city:
                raise ValidationError(f"Kombinasi nama klub '{record.name}' dan kota '{record.city}' sudah ada. Data harus unik.")
            # Check name uniqueness
            same_name = self.search([
                ('id', '!=', record.id),
                ('name', '=', record.name)
            ])
            if same_name:
                raise ValidationError(f"Nama klub '{record.name}' sudah digunakan. Klub name harus unik.")
            # Check city uniqueness
            same_city = self.search([
                ('id', '!=', record.id),
                ('city', '=', record.city)
            ])
            if same_city:
                raise ValidationError(f"Kota '{record.city}' sudah digunakan. Klub kota harus unik.")