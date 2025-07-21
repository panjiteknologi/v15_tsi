from odoo import models, fields, api, _
import odoo
import logging
import secrets
from odoo.http import request

_logger = logging.getLogger(__name__)

class AuditSystem(models.Model):
    _name = "tsi.audit.system"
    _description = "Audit System"
    _order = 'id DESC'
    
    nama = fields.Char(string='Nama')
            
    def action_open_audit_system(self):
        base_url = "https://status-audit.manajemensistem.com"
        user = self.env.user.sudo()  
        token = user.access_token
        
        _logger.info("Token %s",token)
        _logger.info("Token %s",user)
        
        return {
            'type': 'ir.actions.act_url',
            'url': f"{base_url}?access_token={token}",
            'target': 'new',
        }

# class ResUsers(models.Model):
#     _inherit = "res.users"

#     access_token = fields.Char(string="Access Token")

#     @classmethod
#     def _login(cls, db, login, password, user_agent_env):
#         user_id = super()._login(db, login, password, user_agent_env)
#         if user_id:
#             env = api.Environment(odoo.registry(db).cursor(), user_id, user_agent_env)
#             user = env["res.users"].browse(user_id)

#             session_id = request.session.sid if request and request.session else None
#             token = user._compute_session_token(session_id) if session_id else None
            
#             request.session.update({
#                 'uid': user.id,
#                 'login': user.login,
#                 'access_token': token,
#                 'context': user.context_get(),
#             })
#             user.sudo().write({'access_token': token})
#             env.cr.commit()
            
#             _logger.info("User %s logged in with session: %s", user.login, request.session)
#         return user_id


        