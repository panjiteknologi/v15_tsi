from odoo import models, fields, api
from datetime import date

class PengeluaranBarang(models.Model):
    _name = 'tsi.pengeluaran_barang'
    _description = 'Pengeluaran Barang'

    name = fields.Char(string="Document No", required=True, readonly=True, tracking=True, default='New')
    name_karyawan = fields.Many2one('res.partner', string="Nama Karyawan", domain="[('is_company', '=', False)]", tracking=True)
    tanggal_barang_keluar = fields.Datetime(string="Tanggal Keluar Barang", tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status', tracking=True, default='draft')

    lines_barang = fields.One2many('tsi.pengeluaran_barang.line', 'reference_id', string="Order Lines", index=True, tracking=True)
    # picking_type_id = fields.Many2one(
    #     'stock.picking.type', 'Operation Type',   
    #     required=True, readonly=True,
    #     states={'draft': [('readonly', False)]})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('tsi.pengeluaran_barang') or _('New')
        return super(PengeluaranBarang, self).create(vals)

    def action_create_stock_picking(self):
        self.ensure_one()

        # Validasi awal
        if not self.name_karyawan:
            raise UserError("Nama Karyawan harus diisi.")
        if not self.lines_barang:
            raise UserError("Setidaknya satu produk harus ditambahkan.")

        # Lokasi asal (internal) dan lokasi tujuan (customer)
        location_internal = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
        location_customer = self.env.ref('stock.stock_location_customers')

        # Picking type (outgoing)
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
        if not picking_type:
            raise UserError("Picking Type dengan kode 'outgoing' tidak ditemukan.")

        picking_vals = {
            'origin': self.name,
            'partner_id': self.name_karyawan.id,
            'tanggal': self.tanggal_barang_keluar,
            'location_id': location_internal.id,
            'location_dest_id': location_customer.id,
            'picking_type_id': picking_type.id,
        }
        picking = self.env['stock.picking'].create(picking_vals)

        for line in self.lines_barang:
            move_vals = {
                'picking_id': picking.id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'name': line.description or line.product_id.name,
                'product_uom': line.product_id.uom_id.id,
                'location_id': location_internal.id,
                'location_dest_id': location_customer.id,
            }
            self.env['stock.move'].create(move_vals)

        picking.action_confirm()
        # picking.action_assign()

        self.write({'state': 'done'})

class PengeluaranBarangLine(models.Model):
    _name = 'tsi.pengeluaran_barang.line'
    _description = 'Pengeluaran Barang Line'

    reference_id    = fields.Many2one('tsi.pengeluaran_barang', string="Reference")
    product_id      = fields.Many2one('product.product', string='Product')
    description     = fields.Char(string='Description')
    quantity        = fields.Float(string='Quantity', required=True, default=1.0)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tanggal = fields.Date(string="Tanggal Keluar Barang", tracking=True)
    show_fields = fields.Boolean(compute='_compute_show_fields', store=True)

    def _compute_show_fields(self):
        for record in self:
            if record.picking_type_id and record.picking_type_id.code == 'outgoing':
                record.show_fields = True
            else:
                record.show_fields = False
