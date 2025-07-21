import calendar
from odoo import http, _, exceptions
from odoo.http import request, Response
import json
import  werkzeug.wrappers
import re
import logging
from collections import defaultdict
from datetime import date, timedelta
from datetime import datetime

import secrets
from functools import wraps
_logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.httprequest.headers.get('Authorization')
        if not token:
            return {'result': 'error', 'error_message': 'Token is missing.'}, 401

        user = request.env['res.users'].sudo().search([('access_token', '=', token)])
        if not user:
            return {'result': 'error', 'error_message': 'Invalid token.'}, 401

        request.uid = user.id
        return f(*args, **kwargs)
    return decorated_function

def token_required_client(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.httprequest.headers.get('Authorization')
        if not token:
            return request.make_response(
                json.dumps({'result': 'error', 'error_message': 'Token is missing.'}),
                headers=[('Content-Type', 'application/json')],
                status=401
            )

        # Pastikan token bertipe string biasa tanpa "Bearer"
        if token.startswith('Bearer '):
            token = token[7:]

        partner = request.env['res.partner'].sudo().search([('access_token', '=', token)], limit=1)
        if not partner:
            return request.make_response(
                json.dumps({'result': 'error', 'error_message': 'Invalid token.'}),
                headers=[('Content-Type', 'application/json')],
                status=401
            )

        request.partner = partner  # Simpan ke dalam context
        return f(*args, **kwargs)
    return decorated_function

def token_required_flexible(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.httprequest.headers.get('Authorization')
        if not token:
            return request.make_response(
                json.dumps({'result': 'error', 'error_message': 'Token is missing.'}),
                headers=[('Content-Type', 'application/json')],
                status=401
            )
        if token.startswith('Bearer '):
            token = token[7:]

        partner = request.env['res.partner'].sudo().search([('access_token', '=', token)], limit=1)
        if partner:
            request.partner = partner
            request.user = None
            return f(*args, **kwargs)

        user = request.env['res.users'].sudo().search([('access_token', '=', token)], limit=1)
        if user:
            request.user = user
            request.partner = None
            return f(*args, **kwargs)

        return request.make_response(
            json.dumps({'result': 'error', 'error_message': 'Invalid token.'}),
            headers=[('Content-Type', 'application/json')],
            status=401
        )
    return decorated_function

class RestApiTsi(http.Controller):
    def set_cors_headers(self, response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, access_token'
        return response
    
    @http.route('/session/authenticate', csrf=False, type='json', auth="none", methods=['POST'], cors='*')
    def authenticate(self, db, login, password, base_location=None):
        if not db:
            return {
                'result': 'error',
                'error_message': 'Database tidak ditemukan.',
            }

        try:
            request.session.db = db
            request.session.authenticate(db, login, password)
            user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
            if user:
                session_id = request.session.sid if request and request.session else None
                token = user._compute_session_token(session_id) if session_id else secrets.token_hex(32)
                
                _logger.info("User %s logged in with session: %s", user.login, request.session)

                user.sudo().write({'access_token': token})
                request.session.update({
                    'uid': user.id,
                    'login': user.login,
                    'access_token': token,
                    'context': user.context_get(),
                })
                request.env.cr.commit()
                
                return {
                    'result': 'success',
                    'user_id': user.id,
                    'user_name': user.name,
                    'access_token': user.access_token,
                }
        except Exception as e:
            user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
            if user:
                return {
                    'result': 'error password',
                    'error_message': 'Invalid password',
                }
            else:
                return {
                    'result': 'error not found',
                    'error_message': 'Email tidak terdaftar.',
                }
    @http.route('/session/authenticate', csrf=False, type='json', auth='none', methods=['OPTIONS'], cors="*")
    def options_post_authenticate(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )

    @http.route('/client/authenticate', csrf=False, type='json', auth="none", methods=['POST'], cors='*')
    def client_authenticate(self, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')

        if not username or not password:
            return {
                'result': 'error',
                'error_message': 'Username dan password wajib diisi.',
            }

        partner = request.env['res.partner'].sudo().search([
            ('username', '=', username),
            ('password', '=', password)
        ], limit=1)

        if not partner:
            return {
                'result': 'error',
                'error_message': 'Username atau password salah.',
            }

        # Generate token
        token = secrets.token_hex(32)
        partner.write({'access_token': token})  # simpan token di field baru

        return {
            'result': 'success',
            'uid': partner.id,
            'username': partner.username,
            'partner_name': partner.name,
            'access_token': token,
        }
    @http.route('/client/authenticate', csrf=False, type='json', auth='none', methods=['OPTIONS'], cors="*")
    def options_client_authenticate(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )

    # @http.route('/register/client', csrf=False, type='json', auth="none", methods=['POST'], cors='*')
    # def register_client(self, **post):
    #     customer = post.get('customer')
    #     username = post.get('username')
    #     password = post.get('password')

    #     if not customer or not username or not password:
    #         return {'status': 'error', 'message': 'customer, username, and password are required'}

    #     Partner = request.env['res.partner'].sudo()
    #     existing_partner = Partner.search([('name', '=', customer), ('is_company', '=', True)], limit=1)

    #     if existing_partner:
    #         # update existing partner
    #         existing_partner.write({
    #             'username': username,
    #             'password': password,
    #         })
    #         message = 'Updated customer'
    #     else:
    #         # create new partner
    #         Partner.create({
    #             'name': customer,
    #             'username': username,
    #             'password': password,
    #             'is_company': True,
    #             'company_type': 'company',
    #             'company_id': None,
    #         })
    #         message = 'Created new customer'

    #     return {'status': 'success', 'message': message}

    # @http.route('/register/client', csrf=False, type='json', auth='none', methods=['OPTIONS'], cors="*")
    # def options_register_client(self, **kw):
    #     headers = {
    #         'Access-Control-Allow-Headers': 'Content-Type',
    #         'Access-Control-Allow-Origin': '*',
    #         'Access-Control-Allow-Methods': 'POST'
    #     }
    #     return werkzeug.wrappers.Response(
    #         status=200,
    #         content_type='application/json',
    #         response={},
    #         headers=headers
    #         )
        
    @http.route('/session/logout', type='json', auth='none', methods=['POST'], csrf=False)
    def logout(self, access_token=None, **kwargs):
        if not access_token:
            return {
                'result': 'error',
                'error_message': 'Access token tidak ditemukan.',
            }

        try:
            user = request.env['res.users'].sudo().search([('access_token', '=', access_token)], limit=1)
            if user:
                user.sudo().write({'access_token': False})
                return {
                    'result': 'success',
                    'message': 'Logout berhasil.',
                }
            else:
                return {
                    'result': 'error',
                    'error_message': 'Token tidak valid atau tidak ditemukan.',
                }
        except Exception as e:
            return {
                'result': 'error',
                'error_message': 'Terjadi kesalahan saat logout.',
            }   
    @http.route('/session/logout', csrf=False, type='json', auth='none', methods=['OPTIONS'], cors="*")
    def options_post_logout(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )     
                

    @http.route('/api/get_schedule_auditor', csrf=False, type='http', auth='none', methods=['GET'],cors='*')
    @token_required
    def get_schedule_auditor(self, **kwargs):
        programs = request.env['ops.program'].sudo().search([])
        program_lines_data = []
        for program in programs:
            customer_name = program.customer.name if program.customer else ''
            iso_standard = ', '.join(program.iso_standard_ids.mapped('name')) if program.iso_standard_ids else ''
            for line in program.program_lines_aktual:
                date_start_str = line.date_start.strftime('%d-%m-%Y') if isinstance(line.date_start, date) else ''
                date_end_str = line.date_end.strftime('%d-%m-%Y') if isinstance(line.date_end, date) else ''
                lead_auditor = line.lead_auditor.name if line.lead_auditor else ''
                auditor = line.auditor.name if line.auditor else ''
                auditor_2 = line.auditor_2.name if line.auditor_2 else ''
                auditor_3 = line.auditor_3.name if line.auditor_3 else ''
                program_lines_data.append({
                    'customer': customer_name,
                    'iso_standard': iso_standard,
                    'lead_auditor': lead_auditor,
                    'auditor': [auditor,auditor_2,auditor_3],
                    'date_start': date_start_str,
                    'date_end': date_end_str,
                })

        response = request.make_response(json.dumps(program_lines_data), headers={'Content-Type': 'application/json'})
        return self.set_cors_headers(response)
    @http.route('/api/get_schedule_auditor', csrf=False, type='http', auth='none', methods=['OPTIONS'],cors='*')
    def options_get_schedule_auditor(self, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, access_token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response='',
            headers=headers
        )
        
        
    @http.route('/api/get_all_auditor', csrf=False, type='http', auth='none', methods=['GET'],cors='*')
    @token_required
    def get_all_auditor(self, **kwargs):
        data = request.env['hr.employee'].sudo().search([('department_id',"=",[15,16,36]),('id','!=',[89,319,144,320,340,118,119])])
        all_auditor = data.read(['name']) 

        response = request.make_response(json.dumps(all_auditor), headers={'Content-Type': 'application/json'})
        return self.set_cors_headers(response)
    @http.route('/api/get_all_auditor', csrf=False, type='http', auth='none', methods=['OPTIONS'],cors='*')
    def options_get_all_auditor(self, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, access_token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response='',
            headers=headers
        )
        

    @http.route('/api/get_status_auditor', csrf=False, type='http', auth='none', methods=['GET'],cors='*')
    @token_required
    def get_status_auditor(self, **kwargs):
        month = int(kwargs.get('month', datetime.today().month))
        year = int(kwargs.get('year', datetime.today().year))
        days_in_month = calendar.monthrange(year, month)[1]

        # Dapatkan daftar auditor yang termasuk dalam departemen tertentu
        list_auditors = request.env['hr.employee'].sudo().search([
            ('department_id', 'in', [15, 16, 36]), 
            ('id', 'not in', [89, 319, 144, 320, 340, 118, 119])
        ])

        # Dapatkan semua program audit yang tersedia
        programs = request.env['ops.program'].sudo().search([])

        auditor_not_available = {}
        auditor_dates_unavailable = {}

        # Loop untuk mengecek jadwal auditor
        for program in programs:
            customer_name = program.customer.name if program.customer else ''
            iso_standard = ', '.join(program.iso_standard_ids.mapped('name')) if program.iso_standard_ids else ''

            for line in program.program_lines_aktual:
                date_start = line.date_start if isinstance(line.date_start, date) else None
                date_end = line.date_end if isinstance(line.date_end, date) else None

                # **FILTER BERDASARKAN BULAN DAN TAHUN**
                if date_start and date_end:
                    if not (date_start.month == month and date_start.year == year) and not (date_end.month == month and date_end.year == year):
                        continue  # Skip jika tidak dalam bulan & tahun yang diminta

                lead_auditor = line.lead_auditor.name if line.lead_auditor else ''
                auditors = [
                    line.auditor.name if line.auditor else '',
                    line.auditor_2.name if line.auditor_2 else '',
                    line.auditor_3.name if line.auditor_3 else ''
                ]

                involved_auditors = [line.lead_auditor, line.auditor, line.auditor_2, line.auditor_3]

                for auditor in involved_auditors:
                    if auditor:
                        if auditor.name not in auditor_not_available:
                            auditor_not_available[auditor.name] = {
                                "name": auditor.name,
                                "not_available_dates": [],
                                "details": []
                            }

                        if date_start and date_end:
                            unavailable_dates = [
                                (date_start + timedelta(days=i)).strftime('%d-%m-%Y') 
                                for i in range((date_end - date_start).days + 1)
                            ]
                            auditor_not_available[auditor.name]["not_available_dates"].extend(unavailable_dates)

                            # Tambahkan detail program
                            auditor_not_available[auditor.name]["details"].append({
                                "customer": customer_name,
                                "standard": iso_standard,
                                "lead_auditor": lead_auditor,
                                "auditor": auditors,
                                "date_start": date_start.strftime('%d-%m-%Y'),
                                "date_end": date_end.strftime('%d-%m-%Y')
                            })

        # Mengonversi dictionary auditor_not_available ke dalam list
        auditor_not_availables = list(auditor_not_available.values())

        # Mengumpulkan daftar auditor yang masih tersedia
        auditor_availables = []
        for auditor in list_auditors:
            name = auditor.name
            available_dates = [
                date(year, month, day).strftime('%d-%m-%Y')
                for day in range(1, days_in_month + 1)
                if name not in auditor_not_available or date(year, month, day).strftime('%d-%m-%Y') not in auditor_not_available[name]["not_available_dates"]
            ]
            auditor_availables.append({
                "name": name,
                "available_dates": available_dates
            })

        # Struktur JSON yang akan dikembalikan
        response_data = {
            "auditor_available": auditor_availables,
            "auditor_not_available": auditor_not_availables
        }

        response = request.make_response(
            json.dumps(response_data, default=str), 
            headers={'Content-Type': 'application/json'}
        )
        return self.set_cors_headers(response)
    @http.route('/api/get_status_auditor', csrf=False, type='http', auth='none', methods=['OPTIONS'],cors='*')
    def options_get_status_auditor(self, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, access_token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response='',
            headers=headers
        )
        
    @http.route('/api/get_date_customer', csrf=False, type='http', auth='none', methods=['GET'], cors='*')
    @token_required_flexible
    def get_date_customer(self, **kwargs):
        models = [
            ('tsi.iso', 'customer', 'tgl_aplication_form'),
            ('tsi.iso.review', 'customer', 'tgl_review_penugasan_st_satu'),
            ('audit.notification', 'customer', 'tgl_pengiriman_notif'),
            ('ops.program', 'customer', 'tgl_pengiriman_audit_plan'),
            ('ops.plan', 'customer', 'tgl_pelaksanaan_audit'),
            ('ops.report', 'customer', 'tgl_penyelesaian_capa'),
            ('ops.review', 'nama_customer', 'tgl_pengajuan'),
            ('ops.sertifikat', 'nama_customer', 'tgl_pengiriman_draft_sertifikat'),
        ]

        def format_lead_time(start_date, end_date):
            if not start_date or not end_date:
                return ''
            diff = end_date - start_date
            days = diff.days
            seconds = diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60

            parts = []
            if days > 0:
                parts.append(f"{days} hari")
            if hours > 0:
                parts.append(f"{hours} jam")
            if minutes > 0:
                parts.append(f"{minutes} menit")
            return ' '.join(parts) if parts else '0 menit'

        def sum_lead_times(*lead_times):
            total = timedelta()
            for lt in lead_times:
                if not lt:
                    continue
                parts = lt.split()
                days, hours, minutes = 0, 0, 0
                for i in range(0, len(parts), 2):
                    val = int(parts[i])
                    unit = parts[i+1]
                    if 'hari' in unit:
                        days += val
                    elif 'jam' in unit:
                        hours += val
                    elif 'menit' in unit:
                        minutes += val
                total += timedelta(days=days, hours=hours, minutes=minutes)
            return f"{total.days} hari {total.seconds//3600} jam {(total.seconds//60)%60} menit"

        def extract_days_from_lead_time(dt):
            if not dt:
                return 0
            parts = dt.split()
            for i in range(0, len(parts), 2):
                if 'hari' in parts[i+1]:
                    return int(parts[i])
            return 0

        date_filter = '2024-05-01 00:00:00'
        valid_partner_ids = request.env['sale.order'].sudo().search([
            ('date_order', '>=', date_filter),
            ('state', 'in', ['waiting_verify_operation', 'sent', 'sale'])
        ]).mapped('partner_id').ids

        partner_ids = []
        if hasattr(request, 'partner') and request.partner:
            if request.partner.id in valid_partner_ids:
                partner_ids = [request.partner.id]
            else:
                _logger.warning("Partner %s tidak memiliki sale.order dengan date_order >= %s", request.partner.name, date_filter)
        elif hasattr(request, 'user') and request.user:
            partner_ids = valid_partner_ids

        customer_data_ia = {}
        tsi_iso_domain = [
            ('customer', 'in', partner_ids),
            ('sale_order_id.state', 'in', ['waiting_verify_operation', 'sent', 'sale']),
            ('sale_order_id.date_order', '>=', date_filter),
            ('iso_standard_ids', '!=', False),
            ('sale_order_id', '!=', False),
        ]
        tsi_iso_records = request.env['tsi.iso'].sudo().search(tsi_iso_domain)

        for rec in tsi_iso_records:
            customer = rec.customer
            if not customer:
                continue

            cust_name = customer.name
            customer_data_ia[cust_name] = {
                'customer': cust_name,
                'sales_person': rec.sales_person.name if rec.sales_person else '',
                'iso_standards': rec.iso_standard_ids.mapped('name'),
                'accreditation': [],
                'tahapan': 'IA',
                'tgl_aplication_form': rec.create_date.strftime('%Y-%m-%d %H:%M:%S') if rec.create_date else '',
                'tgl_kontrak': rec.sale_order_id.date_order.strftime('%Y-%m-%d %H:%M:%S') if rec.sale_order_id and rec.sale_order_id.date_order else '',
            }

            accreditations = set()
            for std in rec.iso_standard_ids:
                name = std.name
                acc_map = {
                    'ISO 9001:2015': rec.accreditation,
                    'ISO 14001:2015': rec.accreditation_14001,
                    'ISO/IEC 27001:2013': rec.accreditation_27001,
                    'ISO/IEC 27001:2022': rec.accreditation_27001_2022,
                    'ISO/IEC 27017:2015': rec.accreditation_27017,
                    'ISO/IEC 27018:2019': rec.accreditation_27018,
                    'ISO/IEC 27701:2019': rec.accreditation_27701,
                    'ISO 45001:2018': rec.accreditation_45001,
                    'ISO 22000:2018': rec.accreditation_22000,
                    'HACCP': rec.accreditation_haccp,
                    'ISO 13485:2016': rec.accreditation_13485,
                    'ISO 37001:2016': rec.accreditation_37001,
                    'ISO 22301:2019': rec.accreditation_22301,
                }
                acc = acc_map.get(name)
                if acc:
                    accreditations.add(acc.name)
            customer_data_ia[cust_name]['accreditation'] = list(accreditations)

        for model_name, customer_field, label in models[1:]:
            valid_customer_ids = [customer_data_ia[cust_name]['customer'] for cust_name in customer_data_ia]
            domain = [(customer_field, 'in', partner_ids)]
            records = request.env[model_name].sudo().search(domain)

            bulan_dict = {
                1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"
            }

            for rec in records:
                customer = getattr(rec, customer_field)
                if not customer:
                    continue

                cust_name = customer.name
                if cust_name not in customer_data_ia:
                    continue

                if model_name == 'tsi.iso.review':
                    create_dt = rec.create_date
                    if create_dt:
                        customer_data_ia[cust_name]['day'] = create_dt.day
                        customer_data_ia[cust_name]['month'] = bulan_dict.get(create_dt.month, "")
                        customer_data_ia[cust_name]['year'] = create_dt.year

                field_name = label
                if label == 'tgl_pengiriman_notif':
                    field_name = 'tgl_pengiriman_notif_st_satu'
                elif label == 'tgl_pengiriman_audit_plan':
                    field_name = 'tgl_pengiriman_audit_plan_st_satu'
                elif label == 'tgl_pelaksanaan_audit':
                    field_name = 'tgl_pelaksanaan_audit_st_satu'
                elif label == 'tgl_penyelesaian_capa':
                    field_name = 'tgl_penyelesaian_capa_st_satu'

                customer_data_ia[cust_name][field_name] = rec.create_date.strftime('%Y-%m-%d %H:%M:%S') if rec.create_date else ''

                accreditation = customer_data_ia[cust_name]['accreditation']
                is_kan = 'KAN' in accreditation

                sertifikat = request.env['ops.sertifikat'].sudo().search([('nama_customer', '=', cust_name)], limit=1)
                customer_data_ia[cust_name]['tgl_pengajuan'] = ''
                customer_data_ia[cust_name]['tgl_pengiriman_draft_sertifikat'] = ''
                customer_data_ia[cust_name]['tgl_persetujuan'] = ''
                customer_data_ia[cust_name]['tgl_kirim_sertifikat'] = ''

                if sertifikat:
                    if is_kan:
                        for sert in sertifikat.sertifikat_kan:
                            if sert.status_sertifikat == 'register_kan' and sert.date:
                                customer_data_ia[cust_name]['tgl_pengajuan'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                            elif sert.status_sertifikat == 'sned_client' and sert.date:
                                customer_data_ia[cust_name]['tgl_pengiriman_draft_sertifikat'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                            elif sert.status_sertifikat == 'approv_kan' and sert.date:
                                customer_data_ia[cust_name]['tgl_persetujuan'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                            elif sert.status_sertifikat == 'seritifikat_client' and sert.date:
                                customer_data_ia[cust_name]['tgl_kirim_sertifikat'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        for sert in sertifikat.sertifikat_non:
                            if sert.status_sertifikat == 'approv_client' and sert.date:
                                customer_data_ia[cust_name]['tgl_pengajuan'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                            elif sert.status_sertifikat == 'sned_client' and sert.date:
                                customer_data_ia[cust_name]['tgl_pengiriman_draft_sertifikat'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                            elif sert.status_sertifikat == 'seritifikat_client' and sert.date:
                                customer_data_ia[cust_name]['tgl_persetujuan'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                            elif sert.status_sertifikat == 'received_client' and sert.date:
                                customer_data_ia[cust_name]['tgl_kirim_sertifikat'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')

        for data in customer_data_ia.values():
            for field in ['tgl_aplication_form', 'tgl_review_penugasan_st_satu', 'tgl_kontrak', 'tgl_pengiriman_notif_st_satu',
                        'tgl_pengiriman_audit_plan_st_satu', 'tgl_pelaksanaan_audit_st_satu', 'tgl_penyelesaian_capa_st_satu',
                        'tgl_pengajuan', 'tgl_pengiriman_draft_sertifikat', 'tgl_persetujuan', 'tgl_kirim_sertifikat']:
                if field not in data:
                    data[field] = ''

            def dt(val): return datetime.strptime(val, '%Y-%m-%d %H:%M:%S') if val else None

            data['lead_time_tgl_aplication_form_to_tgl_review_penugasan_st_satu'] = format_lead_time(dt(data['tgl_aplication_form']), dt(data['tgl_review_penugasan_st_satu']))
            data['lead_time_tgl_review_penugasan_st_satu_to_tgl_kontrak'] = format_lead_time(dt(data['tgl_review_penugasan_st_satu']), dt(data['tgl_kontrak']))
            data['lead_time_tgl_kontrak_to_tgl_pengiriman_notif_st_satu'] = format_lead_time(dt(data['tgl_kontrak']), dt(data['tgl_pengiriman_notif_st_satu']))
            data['lead_time_tgl_pengiriman_notif_st_satu_to_tgl_pengiriman_audit_plan_st_satu'] = format_lead_time(dt(data['tgl_pengiriman_notif_st_satu']), dt(data['tgl_pengiriman_audit_plan_st_satu']))
            data['lead_time_tgl_pengiriman_audit_plan_st_satu_to_tgl_pelaksanaan_audit_st_satu'] = format_lead_time(dt(data['tgl_pengiriman_audit_plan_st_satu']), dt(data['tgl_pelaksanaan_audit_st_satu']))
            data['lead_time_tgl_pelaksanaan_audit_st_satu_to_tgl_penyelesaian_capa_st_satu'] = format_lead_time(dt(data['tgl_pelaksanaan_audit_st_satu']), dt(data['tgl_penyelesaian_capa_st_satu']))
            data['lead_time_tgl_penyelesaian_capa_st_satu_to_tgl_pengiriman_draft_sertifikat'] = format_lead_time(dt(data['tgl_penyelesaian_capa_st_satu']), dt(data['tgl_pengiriman_draft_sertifikat']))
            data['lead_time_tgl_pengiriman_draft_sertifikat_to_tgl_pengajuan'] = format_lead_time(dt(data['tgl_pengiriman_draft_sertifikat']), dt(data['tgl_pengajuan']))
            data['lead_time_tgl_pengajuan_to_tgl_persetujuan'] = format_lead_time(dt(data['tgl_pengajuan']), dt(data['tgl_persetujuan']))
            data['lead_time_tgl_persetujuan_to_tgl_kirim_sertifikat'] = format_lead_time(dt(data['tgl_persetujuan']), dt(data['tgl_kirim_sertifikat']))

            data['lead_time_finish'] = sum_lead_times(
                data['lead_time_tgl_aplication_form_to_tgl_review_penugasan_st_satu'],
                data['lead_time_tgl_review_penugasan_st_satu_to_tgl_kontrak'],
                data['lead_time_tgl_kontrak_to_tgl_pengiriman_notif_st_satu'],
                data['lead_time_tgl_pengiriman_notif_st_satu_to_tgl_pengiriman_audit_plan_st_satu'],
                data['lead_time_tgl_pengiriman_audit_plan_st_satu_to_tgl_pelaksanaan_audit_st_satu'],
                data['lead_time_tgl_pelaksanaan_audit_st_satu_to_tgl_penyelesaian_capa_st_satu'],
                data['lead_time_tgl_penyelesaian_capa_st_satu_to_tgl_pengiriman_draft_sertifikat'],
                data['lead_time_tgl_pengiriman_draft_sertifikat_to_tgl_pengajuan'],
                data['lead_time_tgl_pengajuan_to_tgl_persetujuan'],
                data['lead_time_tgl_persetujuan_to_tgl_kirim_sertifikat'],
            )

            data['lead_time_project_finish_for_chart'] = extract_days_from_lead_time(data['lead_time_finish'])

        surveilance_grouped = defaultdict(lambda: {
            'customer': '',
            'sales_person': '',
            'iso_standards': set(),
            'accreditation': set(),
            'tahapan': '',
        })

        audit_requests = request.env['tsi.audit.request'].sudo().search([], order='approve_date desc')
        _logger.info("Ditemukan %s audit requests untuk Surveillance", len(audit_requests))

        for audit in audit_requests:
            partner = audit.reference.partner_id if audit.reference and audit.reference.partner_id else None
            if not partner:
                continue

            key = (partner.id, audit.audit_stage)
            group = surveilance_grouped[key]
            group['customer'] = partner.name
            group['tahapan'] = audit.audit_stage

            if audit.sales and not group['sales_person']:
                group['sales_person'] = audit.sales.name

            group['iso_standards'].update(audit.iso_standard_ids.mapped('name'))

            acc_fields = [
                'accreditation_9001', 'accreditation_14001', 'accreditation_27001', 'accreditation_27001_2022',
                'accreditation_27017', 'accreditation_27018', 'accreditation_27701', 'accreditation_45001',
                'accreditation_22000', 'accreditation_haccp', 'accreditation_13485', 'accreditation_37001',
                'accreditation_22301'
            ]
            for field_name in acc_fields:
                acc = getattr(audit, field_name)
                if acc:
                    group['accreditation'].add(acc.name)

            group['tgl_aplication_form'] = audit.create_date.strftime('%Y-%m-%d %H:%M:%S') if audit.create_date else ''
            group['tgl_review_penugasan'] = audit.approve_date.strftime('%Y-%m-%d %H:%M:%S') if audit.approve_date else ''

        surveilance_data = []
        surveillance_customers = set()
        for (partner_id, stage), data in surveilance_grouped.items():
            for model_name, customer_field, label in models[2:]:
                records = request.env[model_name].sudo().search([(customer_field, '=', partner_id)])
                data[label] = records[0].create_date.strftime('%Y-%m-%d %H:%M:%S') if records else ''

            is_kan = 'KAN' in data['accreditation']
            sertifikat = request.env['ops.sertifikat'].sudo().search([('nama_customer', '=', data['customer'])], limit=1)
            data['tgl_pengajuan'] = ''
            data['tgl_pengiriman_draft_sertifikat'] = ''
            data['tgl_persetujuan'] = ''
            data['tgl_kirim_sertifikat'] = ''

            if sertifikat:
                if is_kan:
                    for sert in sertifikat.sertifikat_kan:
                        if sert.status_sertifikat == 'register_kan' and sert.date:
                            data['tgl_pengajuan'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                        elif sert.status_sertifikat == 'sned_client' and sert.date:
                            data['tgl_pengiriman_draft_sertifikat'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                        elif sert.status_sertifikat == 'approv_kan' and sert.date:
                            data['tgl_persetujuan'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                        elif sert.status_sertifikat == 'seritifikat_client' and sert.date:
                            data['tgl_kirim_sertifikat'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    for sert in sertifikat.sertifikat_non:
                        if sert.status_sertifikat == 'approv_client' and sert.date:
                            data['tgl_pengajuan'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                        elif sert.status_sertifikat == 'sned_client' and sert.date:
                            data['tgl_pengiriman_draft_sertifikat'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                        elif sert.status_sertifikat == 'seritifikat_client' and sert.date:
                            data['tgl_persetujuan'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')
                        elif sert.status_sertifikat == 'received_client' and sert.date:
                            data['tgl_kirim_sertifikat'] = sert.date.strftime('%Y-%m-%d %H:%M:%S')

            data['iso_standards'] = list(data['iso_standards'])
            data['accreditation'] = list(data['accreditation'])

            def dt(val): return datetime.strptime(val, '%Y-%m-%d %H:%M:%S') if val else None

            data['lead_time_tgl_aplication_form_to_tgl_review_penugasan'] = format_lead_time(dt(data['tgl_aplication_form']), dt(data['tgl_review_penugasan']))
            data['lead_time_tgl_review_penugasan_to_tgl_pengiriman_notif'] = format_lead_time(dt(data['tgl_review_penugasan']), dt(data['tgl_pengiriman_notif']))
            data['lead_time_tgl_pengiriman_notif_to_tgl_pengiriman_audit_plan'] = format_lead_time(dt(data['tgl_pengiriman_notif']), dt(data['tgl_pengiriman_audit_plan']))
            data['lead_time_tgl_pengiriman_audit_plan_to_tgl_pelaksanaan_audit'] = format_lead_time(dt(data['tgl_pengiriman_audit_plan']), dt(data['tgl_pelaksanaan_audit']))
            data['lead_time_tgl_pelaksanaan_audit_to_tgl_penyelesaian_capa'] = format_lead_time(dt(data['tgl_pelaksanaan_audit']), dt(data['tgl_penyelesaian_capa']))
            data['lead_time_tgl_penyelesaian_capa_to_tgl_pengiriman_draft_sertifikat'] = format_lead_time(dt(data['tgl_penyelesaian_capa']), dt(data['tgl_pengiriman_draft_sertifikat']))
            data['lead_time_tgl_pengiriman_draft_sertifikat_to_tgl_pengajuan'] = format_lead_time(dt(data['tgl_pengiriman_draft_sertifikat']), dt(data['tgl_pengajuan']))
            data['lead_time_tgl_pengajuan_to_tgl_persetujuan'] = format_lead_time(dt(data['tgl_pengajuan']), dt(data['tgl_persetujuan']))
            data['lead_time_tgl_persetujuan_to_tgl_kirim_sertifikat'] = format_lead_time(dt(data['tgl_persetujuan']), dt(data['tgl_kirim_sertifikat']))

            data['lead_time_finish'] = sum_lead_times(
                data['lead_time_tgl_aplication_form_to_tgl_review_penugasan'],
                data['lead_time_tgl_review_penugasan_to_tgl_pengiriman_notif'],
                data['lead_time_tgl_pengiriman_notif_to_tgl_pengiriman_audit_plan'],
                data['lead_time_tgl_pengiriman_audit_plan_to_tgl_pelaksanaan_audit'],
                data['lead_time_tgl_pelaksanaan_audit_to_tgl_penyelesaian_capa'],
                data['lead_time_tgl_penyelesaian_capa_to_tgl_pengiriman_draft_sertifikat'],
                data['lead_time_tgl_pengiriman_draft_sertifikat_to_tgl_pengajuan'],
                data['lead_time_tgl_pengajuan_to_tgl_persetujuan'],
                data['lead_time_tgl_persetujuan_to_tgl_kirim_sertifikat'],
            )

            data['lead_time_project_finish_for_chart'] = extract_days_from_lead_time(data['lead_time_finish'])

            surveilance_data.append(data)
            surveillance_customers.add(data['customer'])

        filtered_ia_data = [data for data in customer_data_ia.values() if data['customer'] not in surveillance_customers]
        result = filtered_ia_data + surveilance_data

        return request.make_response(json.dumps(result), headers=[('Content-Type', 'application/json')])

    @http.route('/api/get_date_customer', csrf=False, type='http', auth='none', methods=['OPTIONS'], cors='*')
    def options_get_date_customer(self, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, access_token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response='',
            headers=headers
        )

    @http.route('/api/get_date_customer_ispo', csrf=False, type='http', auth='none', methods=['GET'], cors='*')
    @token_required
    def get_date_customer_ispo(self, **kwargs):
        models = [
            ('tsi.ispo', 'customer', 'aplication_form'),
            ('tsi.ispo.review', 'customer', 'review_penugasan'),
            ('audit.notification.ispo', 'customer', 'pengiriman_notifikasi'),
            ('ops.program.ispo', 'customer', 'pengiriman_audit_plan'),
            ('ops.plan.ispo', 'customer', 'pelaksanaan_audit'),
            ('ops.report.ispo', 'customer', 'penyelesaian_capa'),
            ('ops.review.ispo', 'nama_customer', 'tanggal_pengajuan'),
            ('ops.sertifikat.ispo', 'nama_customer', 'pengiriman_draft_sertifikat'),
        ]

        def format_lead_time(start_date, end_date):
            if not start_date or not end_date:
                return ''
            diff = end_date - start_date
            days = diff.days
            seconds = diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60

            parts = []
            if days > 0:
                parts.append(f"{days} hari")
            if hours > 0:
                parts.append(f"{hours} jam")
            if minutes > 0:
                parts.append(f"{minutes} menit")
            return ' '.join(parts) if parts else '0 menit'

        # ===== IA DATA =====
        customer_data_ia = {}
        for model_name, customer_field, label in models:
            records = request.env[model_name].sudo().search([])
            for rec in records:
                customer = getattr(rec, customer_field)
                if not customer:
                    continue

                cust_name = customer.name

                if cust_name not in customer_data_ia:
                    customer_data_ia[cust_name] = {
                        'customer': cust_name,
                        'sales_person': '',
                        'ispo_standards': [],
                        'accreditation': [],
                        'tahapan': 'IA',
                    }

                ops_sert = request.env['ops.sertifikat'].sudo().search([('nama_customer', '=', cust_name)], limit=1)
                customer_data_ia[cust_name]['tgl_persetujuan'] = ops_sert.confirm_date.strftime('%Y-%m-%d %H:%M:%S') if ops_sert and ops_sert.confirm_date else ''
                customer_data_ia[cust_name]['tgl_kirim_sertifikat'] = ops_sert.done_date.strftime('%Y-%m-%d %H:%M:%S') if ops_sert and ops_sert.done_date else ''

                customer_data_ia[cust_name][label] = rec.create_date.strftime('%Y-%m-%d %H:%M:%S') if rec.create_date else ''

                if model_name == 'tsi.ispo':
                    rec_data = customer_data_ia[cust_name]
                    if rec.sales_person:
                        rec_data['sales_person'] = rec.sales_person.name
                    if rec.iso_standard_ids:
                        rec_data['ispo_standards'] = rec.iso_standard_ids.mapped('name')

                    accreditations = set()
                    for std in rec.iso_standard_ids:
                        name = std.name
                        acc_map = {
                            'ISPO': rec.accreditation,
                        }
                        acc = acc_map.get(name)
                        if acc:
                            accreditations.add(acc.name)
                    rec_data['accreditation'] = list(accreditations)

        for data in customer_data_ia.values():
            for field in ['aplication_form', 'review_penugasan', 'pengiriman_notifikasi',
                          'pengiriman_audit_plan', 'pelaksanaan_audit', 'penyelesaian_capa',
                          'tanggal_pengajuan', 'pengiriman_draft_sertifikat']:
                if field not in data:
                    data[field] = ''

            # Hitung lead_time IA
            def dt(val): return datetime.strptime(val, '%Y-%m-%d %H:%M:%S') if val else None

            data['lead_time_aplication_form_to_review_penugasan'] = format_lead_time(dt(data['aplication_form']), dt(data['review_penugasan']))
            data['lead_time_review_penugasan_to_pengiriman_notifikasi'] = format_lead_time(dt(data['review_penugasan']), dt(data['pengiriman_notifikasi']))
            data['lead_time_pengiriman_notifikasi_to_pengiriman_audit_plan'] = format_lead_time(dt(data['pengiriman_notifikasi']), dt(data['pengiriman_audit_plan']))
            data['lead_time_pengiriman_audit_plan_to_pelaksanaan_audit'] = format_lead_time(dt(data['pengiriman_audit_plan']), dt(data['pelaksanaan_audit']))
            data['lead_time_pelaksanaan_audit_to_penyelesaian_capa'] = format_lead_time(dt(data['pelaksanaan_audit']), dt(data['penyelesaian_capa']))
            data['lead_time_penyelesaian_capa_to_tanggal_pengajuan'] = format_lead_time(dt(data['penyelesaian_capa']), dt(data['tanggal_pengajuan']))
            data['lead_time_tanggal_pengajuan_to_pengiriman_draft_sertifikat'] = format_lead_time(dt(data['tanggal_pengajuan']), dt(data['pengiriman_draft_sertifikat']))

        # ===== Surveillance & Recertification =====
        from collections import defaultdict
        surveilance_grouped = defaultdict(lambda: {
            'customer': '',
            'sales_person': '',
            'ispo_standards': set(),
            'accreditation': set(),
            'tahapan': '',
        })

        audit_requests = request.env['tsi.audit.request.ispo'].sudo().search([])
        for audit in audit_requests:
            partner = audit.reference.partner_id if audit.reference and audit.reference.partner_id else None
            if not partner:
                continue

            key = (partner.id, audit.audit_stage)
            group = surveilance_grouped[key]
            group['customer'] = partner.name
            group['tahapan'] = audit.audit_stage

            if audit.sales and not group['sales_person']:
                group['sales_person'] = audit.sales.name

            group['ispo_standards'].update(audit.iso_standard_ids.mapped('name'))

            acc_fields = [
                'accreditation_ispo'
            ]
            for field_name in acc_fields:
                acc = getattr(audit, field_name)
                if acc:
                    group['accreditation'].add(acc.name)

            group['aplication_form'] = audit.create_date.strftime('%Y-%m-%d %H:%M:%S') if audit.create_date else ''

        surveilance_data = []
        surveillance_customers = set()
        for (partner_id, stage), data in surveilance_grouped.items():
            for model_name, customer_field, label in models[2:]:
                records = request.env[model_name].sudo().search([(customer_field, '=', partner_id)])
                data[label] = records[0].create_date.strftime('%Y-%m-%d %H:%M:%S') if records else ''

            data['ispo_standards'] = list(data['ispo_standards'])
            data['accreditation'] = list(data['accreditation'])

            # Hitung lead_time Surveillance
            def dt(val): return datetime.strptime(val, '%Y-%m-%d %H:%M:%S') if val else None

            data['lead_time_pengiriman_notifikasi_to_pengiriman_audit_plan'] = format_lead_time(dt(data['pengiriman_notifikasi']), dt(data['pengiriman_audit_plan']))
            data['lead_time_pengiriman_audit_plan_to_pelaksanaan_audit'] = format_lead_time(dt(data['pengiriman_audit_plan']), dt(data['pelaksanaan_audit']))
            data['lead_time_pelaksanaan_audit_to_penyelesaian_capa'] = format_lead_time(dt(data['pelaksanaan_audit']), dt(data['penyelesaian_capa']))
            data['lead_time_penyelesaian_capa_to_tanggal_pengajuan'] = format_lead_time(dt(data['penyelesaian_capa']), dt(data['tanggal_pengajuan']))
            data['lead_time_tanggal_pengajuan_to_pengiriman_draft_sertifikat'] = format_lead_time(dt(data['tanggal_pengajuan']), dt(data['pengiriman_draft_sertifikat']))

            surveilance_data.append(data)
            surveillance_customers.add(data['customer'])

        filtered_ia_data = [data for data in customer_data_ia.values() if data['customer'] not in surveillance_customers]

        result = filtered_ia_data + surveilance_data

        return request.make_response(json.dumps(result), headers=[('Content-Type', 'application/json')])

    @http.route('/api/get_date_customer_ispo', csrf=False, type='http', auth='none', methods=['OPTIONS'], cors='*')
    def options_get_date_customer_ispo(self, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, access_token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response='',
            headers=headers
        )

    @http.route('/api/chart_list_standards', csrf=False, type='http', auth='none', methods=['GET'], cors='*')
    @token_required_flexible
    def chart_list_standards(self, **kwargs):
        SaleOrder = request.env['sale.order'].sudo()
        sale_orders = SaleOrder.search([('state', '=', 'sale')])

        grouped_data = {}

        for order in sale_orders:
            order_date = order.date_order
            if not order_date:
                continue

            order_day = order_date.strftime('%Y-%m-%d')
            order_month = order_date.strftime('%B')
            order_year = order_date.year
            customer_name = order.partner_id.name or 'Unknown Customer'

            for line in order.order_line:
                product_name = line.product_id.name or ''
                
                # 🚫 Skip jika mengandung "Termin"
                if re.search(r'Termin\s*[1-5]\b', product_name, re.IGNORECASE):
                    continue

                standards = [product_name.strip()]

                # 🔄 Normalisasi nama standar
                # if product_name.strip() == "ISO 9001":
                #     standards = ["ISO 9001:2015"]
                # elif product_name.strip() == "ISO 14001":
                #     standards = ["ISO 14001:2015"]
                # elif "&" in product_name or ";" in product_name:
                #     raw_standards = re.split(r'[;&]', product_name)
                #     standards = [s.strip() for s in raw_standards if s.strip()]
                # else:
                #     standards = [product_name.strip()]

                # count = len(standards)
                # price_per_standard = line.price_unit / count if count else line.price_unit
                price_per_standard = line.price_unit

                for std in standards:
                    key = (order_month, order_year, std)
                    if key not in grouped_data:
                        grouped_data[key] = {
                            'date': order_day,
                            'month': order_month,
                            'year': order_year,
                            'standard_name': std,
                            'harga': 0.0,
                            'quantity': 0,
                            'customers': set(),
                        }
                    grouped_data[key]['harga'] += price_per_standard
                    grouped_data[key]['quantity'] += 1
                    grouped_data[key]['customers'].add(customer_name)

        result = []
        for item in grouped_data.values():
            item['customers'] = list(item['customers']) if item['quantity'] > 1 else list(item['customers'])[:1]
            result.append(item)

        return request.make_response(json.dumps(result), headers=[('Content-Type', 'application/json')])

    @http.route('/api/chart_list_standards', csrf=False, type='http', auth='none', methods=['OPTIONS'], cors='*')
    def options_chart_list_standards(self, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, access_token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response='',
            headers=headers
        )
        
    @http.route('/api/validate_token', csrf=False, type='json', auth='none', methods=['POST'],cors='*')
    def validate_token(self, **kwargs):
        try:
            # users = request.env['res.users'].sudo().search([('access_token', '!=', False)])
            # request.session.authenticate(access_token)
            
            access_token = request.jsonrequest.get('access_token')
            if not access_token:
                return {
                    'status': 'error',
                    'message': 'Access token is required'
                }

            user = request.env['res.users'].sudo().search([
                ('access_token', '=', access_token),
            ], limit=1)

            if user:
                return {
                    'status': 'success',
                    'message': 'Access token valid',
                    'user_id': user.id,
                    'user_name': user.name,
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Invalid access token'
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    @http.route('/api/validate_token', csrf=False, type='http', auth='none', methods=['OPTIONS'],cors='*')
    def options_validate_token(self, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response='',
            headers=headers
        )
    
    @http.route('/api/validate_client_token', csrf=False, type='json', auth='none', methods=['POST'], cors='*')
    def validate_client_token(self, **kwargs):
        try:
            access_token = request.jsonrequest.get('access_token')
            if not access_token:
                return {
                    'status': 'error',
                    'message': 'Access token is required'
                }

            partner = request.env['res.partner'].sudo().search([
                ('access_token', '=', access_token)
            ], limit=1)

            if partner:
                return {
                    'status': 'success',
                    'message': 'Access token valid',
                    'partner_id': partner.id,
                    'partner_name': partner.name,
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Invalid access token'
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    @http.route('/api/validate_client_token', csrf=False, type='http', auth='none', methods=['OPTIONS'],cors='*')
    def options_validate_client_token(self, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response='',
            headers=headers
        )