from odoo import http
from odoo.http import Response, request, JsonRequest
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import json
import logging
import requests
import re
import threading
import time
import os
from datetime import datetime

_logger = logging.getLogger(__name__)

APP_SECRET = '1cc7014c922e062c4d3a8a8c542f69c4'
PASSPHRASE = 'newtsi'
PRIVATE_KEY_PATH = '/mnt/extra-addons/v15_tsi/static/src/keys/private_key.pem'

def alternative_response(self, result=None, error=None):
    if error is not None:
        response = error
    if result is not None:
        response = result
    mime = 'text/plain'
    body = response
    return Response(
        body, status=error and error.pop('http_status', 200) or 200,
        headers=[('Content-Type', mime), ('Content-Length', len(body))]
    )

def delayed_execution(callback, delay):
        time.sleep(delay)
        callback()


data_response_new_application_form =[]
data_response_audit_request_form =[]
data_response_ticket_complain =[]

class FlowController(http.Controller):
    def load_private_key(self):
        with open(PRIVATE_KEY_PATH, 'rb') as key_file:
            private_key = load_pem_private_key(key_file.read(), password=PASSPHRASE.encode('utf-8'))
            return private_key

    def decrypt_request(self, encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
        flow_data = b64decode(encrypted_flow_data_b64)
        iv = b64decode(initial_vector_b64)
        encrypted_aes_key = b64decode(encrypted_aes_key_b64)
        private_key = self.load_private_key()

        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        encrypted_flow_data_body = flow_data[:-16]
        encrypted_flow_data_tag = flow_data[-16:]
        decryptor = Cipher(algorithms.AES(aes_key), modes.GCM(iv, encrypted_flow_data_tag)).decryptor()
        decrypted_data_bytes = decryptor.update(encrypted_flow_data_body) + decryptor.finalize()
        decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))

        return decrypted_data, aes_key, iv

    def encrypt_response(self, response, aes_key, iv):
        flipped_iv = bytearray([byte ^ 0xFF for byte in iv])
        encryptor = Cipher(algorithms.AES(aes_key), modes.GCM(bytes(flipped_iv))).encryptor()
        encrypted_data = encryptor.update(json.dumps(response).encode("utf-8")) + encryptor.finalize()
        encoded_response = b64encode(encrypted_data + encryptor.tag).decode("utf-8")
        return encoded_response
    
    
    @http.route('/new_application_form', type='json', auth='public', methods=['POST'], csrf=False)
    def new_application_form(self, **kwargs):
        try:
            iso_standard = request.env['tsi.iso.standard'].sudo().search([('standard','=','iso')])
            standard_data = [{"id": str(record.name), "title": record.name} for record in iso_standard[:20]]
            # Sisa data standard
            standard_datas = [{"id": str(record.name), "title": record.name} for record in iso_standard[20:]]
            
        
            body = json.loads(http.request.httprequest.data)
            encrypted_flow_data_b64 = body['encrypted_flow_data']
            encrypted_aes_key_b64 = body['encrypted_aes_key']
            initial_vector_b64 = body['initial_vector']
            
            _logger.info("Request received at /flow:: %s",body)

            decrypted_data, aes_key, iv = self.decrypt_request(encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64)
            _logger.info("💬 Decrypted Request: %s", decrypted_data)
            
            data = decrypted_data.get('data', {})
            standard_names = data.get('iso_standard') or []
            standards_names = data.get('iso_standards') or []
            certificate_type = data.get('certificate_type')
            if certificate_type == "Multi Site":
                is_multi_site = True
            else:
                is_multi_site = False
                
                        
            SCREEN_RESPONSES = {
                "Company_info": {
                    "screen": "Company_info",
                    "data": {
                        "standard": standard_data,
                        "standards": standard_datas
                    }
                },
                "Scope_and_Boundaries": {
                    "screen": "Scope_and_Boundaries",
                    "data": {
                        "standard": standard_data,
                        "standards": standard_datas
                    }
                },
                "Personnel_Situation": {
                    "screen": "Personnel_Situation",
                    "data": {
                        "is_multi_site": is_multi_site
                    }
                },
                "SUMMARY": {
                    "screen": "SUMMARY",
                    "data": {
                        "summary_company_name": f"Company Name: {data.get('company_name')}",
                        "summary_office_address": f"Office Address : {data.get('office_address')}",
                        "summary_invoice_address": f"Invoice Address : {data.get('invoice_address')}",
                        "summary_contact_person": f"Contact Person : {data.get('contact_person')}",
                        "summary_phone": f"Phone : {data.get('phone')}",
                        "summary_jabatan": f"Jabatan : {data.get('jabatan')}",
                        "summary_email": f"Email : {data.get('email')}",
                        "summary_website": f"Website : {data.get('website')}",
                        
                        "summary_scope": f"Scope : {data.get('scope')}",
                        "summary_boundaries": f"Boundaries  : {data.get('boundaries')}",
                        "summary_standard": f"ISO Standard : {', '.join(standard_names)}, {', '.join(standards_names)}",
                        "summary_certificate_type": f"Certificate Type : {data.get('certificate_type')}",
                        "summary_audit_stage": f"Audit Stage : {data.get('audit_stage')}",
                        "summary_number_of_site": f"Number of site : {data.get('number_of_site')}",
                        "summary_remarks": f"Remarks : {data.get('remarks')}",
                        
                        "summary_type": f"Type(HO,Factory etc) : {data.get('type')}",
                        "summary_address": f"Address : {data.get('address')}",
                        "summary_prod_pros_activi": f"Product/Process/Activity : {data.get('prod_pros_activi')}",
                        "summary_emp_total": f"Number of Employees : {data.get('emp_total')}",
                        
                        "summary_type_2": f"Type(HO,Factory etc) : {data.get('type_2')}",
                        "summary_address_2": f"Address : {data.get('address_2')}",
                        "summary_prod_pros_activi_2": f"Product/Process/Activity : {data.get('prod_pros_activi_2')}",
                        "summary_emp_total_2": f"Number of Employees : {data.get('emp_total_2')}",
                        
                        "summary_type_3": f"Type(HO,Factory etc) : {data.get('type_3')}",
                        "summary_address_3": f"Address : {data.get('address_3')}",
                        "summary_prod_pros_activi_3": f"Product/Process/Activity : {data.get('prod_pros_activi_3')}",
                        "summary_emp_total_3": f"Number of Employees : {data.get('emp_total_3')}",
                        
                        "is_multi_site": is_multi_site
                    }
                },
                "SUCCESS": {
                    "screen": "SUCCESS",
                    "data": {
                        "extension_message_response": {
                            "params": {
                                "flow_token": "REPLACE_FLOW_TOKEN",
                                "company_name": "VALUE",
                                "office_address": "VALUE",
                                "invoice_address": "VALUE",
                                "contact_person": "VALUE",
                                "phone": "VALUE",
                                "jabatan": "VALUE",
                                "email": "VALUE",
                                "website": "VALUE",
                                
                                "scope": "VALUE",
                                "boundaries": "VALUE",
                                "iso_standard": "VALUE",
                                "iso_standards": "VALUE",
                                "certificate_type": "VALUE",
                                "audit_stage": "VALUE",
                                "remarks": "VALUE",
                                "number_of_site": "VALUE",
                                
                                "type": "VALUE",
                                "address": "VALUE",
                                "prod_pros_activi": "VALUE",
                                "emp_total": "VALUE",
                                
                                "type_2": "VALUE",
                                "address_2": "VALUE",
                                "prod_pros_activi_2": "VALUE",
                                "emp_total_2": "VALUE",
                                
                                "type_3": "VALUE",
                                "address_3": "VALUE",
                                "prod_pros_activi_3": "VALUE",
                                "emp_total_3": "VALUE",
                                
                                "is_multi_site": "VALUE"
                            }
                        }
                    }
                }
            }
    
            action = decrypted_data.get('action')
            screen = decrypted_data.get('screen')
            flow_token = decrypted_data.get('flow_token')
            
            if action == "ping":
                response = {"data": {"status": "active"}}
                
            elif action == "INIT":
                response = SCREEN_RESPONSES["Company_info"]
                
            elif action == "data_exchange":
                if screen == "Company_info":
                    response = SCREEN_RESPONSES["Company_info"]
                elif screen == "Scope_and_Boundaries":
                    response = SCREEN_RESPONSES["Personnel_Situation"]
                elif screen == "Personnel_Situation":
                    response = SCREEN_RESPONSES["SUMMARY"]
                elif screen == "SUMMARY":
                    response = {
                        **SCREEN_RESPONSES["SUCCESS"], 
                        "data": {
                            "extension_message_response": {
                                "params": {
                                    "flow_token": flow_token,
                                    
                                    "company_name": data.get('company_name'),
                                    "office_address": data.get('office_address'),
                                    "invoice_address": data.get('invoice_address'),
                                    "contact_person": data.get('contact_person'),
                                    "phone": data.get('phone'),
                                    "jabatan": data.get('jabatan'),
                                    "email": data.get('email'),
                                    "website": data.get('website'),
                                    
                                    "scope": data.get('scope'),
                                    "boundaries": data.get('boundaries'),
                                    "iso_standard": data.get('iso_standard',''),
                                    "iso_standards": data.get('iso_standards',''),
                                    "certificate_type": data.get('certificate_type'),
                                    "audit_stage": data.get('audit_stage'),
                                    "remarks": data.get('remarks','none'),
                                    "number_of_site": data.get('number_of_site'),
                                    
                                    "type": data.get('type','none'),
                                    "address": data.get('address','none'),
                                    "prod_pros_activi": data.get('prod_pros_activi','none'),
                                    "emp_total": data.get('emp_total','none'),
                                    
                                    "type_2": data.get('type_2','none'),
                                    "address_2": data.get('address_2','none'),
                                    "prod_pros_activi_2": data.get('prod_pros_activi_2','none'),
                                    "emp_total_2": data.get('emp_total_2','none'),
                                    
                                    "type_3": data.get('type_3','none'),
                                    "address_3": data.get('address_3','none'),
                                    "prod_pros_activi_3": data.get('prod_pros_activi_3','none'),
                                    "emp_total_3": data.get('emp_total_3','none'),
                                    
                                    "is_multi_site": is_multi_site
                                    }
                                }
                            }
                        }
                    
                else:
                    raise ValueError(f"Unhandled screen: {screen}")
            else:
                raise ValueError(f"Unhandled action: {action}")
            
            _logger.info("👉 Response to Encrypt: %s", response)
            
            if response and isinstance(response, dict) and response.get('screen') == 'SUCCESS':
                data_success = response.get('data', {}).get('extension_message_response', {}).get('params', {})
                company_name = data_success.get('company_name').strip()
                contact_person = data_success.get('contact_person').strip()
                company_name = data_success.get('company_name')
                contact_person = data_success.get('contact_person')
                phone = data_success.get('phone')
                if phone:
                    phones = re.sub(r"\D", "", phone)
                    if phones.startswith("0"):
                        phones = "62" + phones[1:]
                    elif phones.startswith("62"):
                        phones = phones 
                    else:
                        raise ValueError(f"Invalid phone number format: {phone}")
                
                iso_standard = data_success.get('iso_standard',[])
                iso_standards = data_success.get('iso_standards',[])
                if not iso_standard and iso_standards:
                    iso_standard_all = iso_standards if isinstance(iso_standards, list) else [iso_standards]
                elif iso_standard and not iso_standards:
                    iso_standard_all = iso_standard if isinstance(iso_standard, list) else [iso_standard]
                else:
                    iso_standard_all = iso_standard + (iso_standards if isinstance(iso_standards, list) else [iso_standards])
                
                                
                audit_stages=[]
                audit_stage = data_success.get('audit_stage')
                if audit_stage == "Initial Assesment":
                    audit_stages = "initial"
                elif audit_stage == "Recertification":
                    audit_stages = "recertification"
                elif audit_stage == "Transfer From Surveilance":
                    audit_stages = "transfer_surveilance"
                elif audit_stage == "Transfer From Recertification":
                    audit_stages = "transfer_recert"
                
                
                pic = request.env['res.partner'].sudo().search([('name', '=', contact_person)], limit=1)
                if pic:
                    _logger.info("Contact Person '%s' already exists, raising exception.", contact_person)
                else:
                    pic = request.env['res.partner'].sudo().create({
                        'name': contact_person,
                        'company_type': 'person'
                    })
                    _logger.info("Success Create Contact Person: %s",pic)
                
                company = request.env['res.partner'].sudo().search([('name', '=', company_name)], limit=1)
                if company:
                    _logger.info("Company with name '%s' already exists, raising exception.", company_name)
                else:
                    company = request.env['res.partner'].sudo().create({
                        'name': company_name,
                        "office_address": data_success.get('office_address'),
                        "invoice_address": data_success.get('invoice_address'),
                        "pic_id": pic.id,
                        "phone": phones,
                        "mobile": phones,
                        "email": data_success.get('email'),
                        "website": data_success.get('website'),
                        'scope': data_success.get('scope'),
                        'boundaries': data_success.get('boundaries'),
                        'is_company':True
                    })
                    _logger.info("Success Create Contact Company: %s",company)
                    _logger.info("Contact Company Phone: %s",company.phone)
                    _logger.info("Contact Company Mobile: %s",company.mobile)
                    
                data_list = [
                    {
                        'type': data.get('type'),
                        'address': data.get('address'),
                        'prod_pros_activi': data.get('prod_pros_activi'),
                        'emp_total': data.get('emp_total',0),
                    },
                    {
                        'type': data.get('type_2'),
                        'address': data.get('address_2'),
                        'prod_pros_activi': data.get('prod_pros_activi_2'),
                        'emp_total': data.get('emp_total_2', 0),
                    },
                    {
                        'type': data.get('type_3'),
                        'address': data.get('address_3'),
                        'prod_pros_activi': data.get('prod_pros_activi_3'),
                        'emp_total': data.get('emp_total_3', 0),
                    },
                ]
 
                personnel_situations = []
                for item in data_list:
                    if any(item.values()):
                        personnel_situations.append((0, 0, {
                            'type': item['type'],
                            'address': item['address'],
                            'product': item['prod_pros_activi'],
                            'emp_total': item['emp_total'],
                        }))

                iso_form = request.env['tsi.iso'].sudo().create({
                    'doctype': 'iso',
                    'customer': company.id,
                    'pic_id': pic.id,
                    'invoicing_address': data_success.get('invoice_address'),
                    'telepon': phones,
                    'email': data_success.get('email'),
                    'office_address': data_success.get('office_address'),
                    'jabatan': data_success.get('jabatan'),
                    'website': data_success.get('website'),
                    
                    'scope': data_success.get('scope'),
                    'boundaries': data_success.get('boundaries'),
                    
                    'iso_standard_ids': request.env['tsi.iso.standard'].sudo().search([('name', 'in', iso_standard_all)]).ids,
                    
                    'certification': data_success.get('certificate_type'),
                    'tx_remarks': data_success.get('remarks'),
                    'audit_stage': audit_stages,
                    'tx_site_count': int(data_success.get('number_of_site', 0)),
                    
                    'partner_site': personnel_situations,
                })
                _logger.info("Form ISO SUCCESS Create: %s",iso_form)
                data_response_new_application_form.clear()
                data_response_new_application_form.append(data_success)
                _logger.info("Data Array http: %s",data_response_new_application_form)
                threading.Thread(target=delayed_execution, args=(self.send_application_form_success, 2)).start()
            encrypted_response = self.encrypt_response(response, aes_key, iv)
            request._json_response = alternative_response.__get__(request, JsonRequest)
            return encrypted_response

        except Exception as e:
            _logger.error(f"Error: {str(e)}")
            return Response(f"Error: {str(e)}", content_type='text/plain')
    
    def send_application_form_success(self):
        if data_response_new_application_form:
            last_item = data_response_new_application_form[-1]
            _logger.info("array def last item:%s",last_item)
            phone = last_item.get("phone")
            is_multi_site = last_item.get("is_multi_site")
            _logger.info("Vlue Is Multi Site: %s",is_multi_site)
            
            if phone:
                phones = re.sub(r"\D", "", phone)
                if phones.startswith("0"):
                    phones = "62" + phones[1:]
                elif phones.startswith("62"):
                    phones = phones 
                else:
                    raise ValueError(f"Invalid phone number format: {phone}")
                
                iso_standard = last_item.get('iso_standard', [])
                if isinstance(iso_standard, str):
                    iso_standard = [iso_standard]

                iso_standards = last_item.get('iso_standards', [])
                if isinstance(iso_standards, str):
                    iso_standards = [iso_standards]

                iso_standard_all = iso_standard + iso_standards
                iso_standard_string = ", ".join(iso_standard_all)
                
                if is_multi_site == False:
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": phones,
                        "type": "template",
                        "template": {
                            "name": "success_application_form_1_dev",
                            "language": {
                                "code": "en_US"
                            },
                            "components": [
                                {
                                    "type": "body",
                                    "parameters": [
                                        {"type": "text", "text": last_item.get("company_name")},
                                        {"type": "text", "text": last_item.get("office_address")},
                                        {"type": "text", "text": last_item.get("invoice_address")},
                                        {"type": "text", "text": last_item.get("contact_person")},
                                        {"type": "text", "text": phone},
                                        {"type": "text", "text": last_item.get("jabatan")},
                                        {"type": "text", "text": last_item.get("email")},
                                        {"type": "text", "text": last_item.get("website")},
                                        
                                        {"type": "text", "text": last_item.get("scope")},
                                        {"type": "text", "text": last_item.get("boundaries")},
                                        {"type": "text", "text": iso_standard_string},
                                        {"type": "text", "text": last_item.get("certificate_type")},
                                        {"type": "text", "text": last_item.get("audit_stage")},
                                        {"type": "text", "text": last_item.get("number_of_site")},
                                        {"type": "text", "text": last_item.get("remarks")},
                                        
                                        {"type": "text", "text": last_item.get("type")},
                                        {"type": "text", "text": last_item.get("address")},
                                        {"type": "text", "text": last_item.get("prod_pros_activi")},
                                        {"type": "text", "text": last_item.get("emp_total")}
                                    ]
                                }
                            ]
                        }
                    }
                else:
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": phones,
                        "type": "template",
                        "template": {
                            "name": "success_application_form_2_dev",
                            "language": {
                                "code": "en_US"
                            },
                            "components": [
                                {
                                    "type": "body",
                                    "parameters": [
                                        {"type": "text", "text": last_item.get("company_name")},
                                        {"type": "text", "text": last_item.get("office_address")},
                                        {"type": "text", "text": last_item.get("invoice_address")},
                                        {"type": "text", "text": last_item.get("contact_person")},
                                        {"type": "text", "text": phone},
                                        {"type": "text", "text": last_item.get("jabatan")},
                                        {"type": "text", "text": last_item.get("email")},
                                        {"type": "text", "text": last_item.get("website")},
                                        
                                        {"type": "text", "text": last_item.get("scope")},
                                        {"type": "text", "text": last_item.get("boundaries")},
                                        {"type": "text", "text": iso_standard_string},
                                        {"type": "text", "text": last_item.get("certificate_type")},
                                        {"type": "text", "text": last_item.get("audit_stage")},
                                        {"type": "text", "text": last_item.get("number_of_site")},
                                        {"type": "text", "text": last_item.get("remarks")},
                                        
                                        {"type": "text", "text": last_item.get("type")},
                                        {"type": "text", "text": last_item.get("address")},
                                        {"type": "text", "text": last_item.get("prod_pros_activi")},
                                        {"type": "text", "text": last_item.get("emp_total")},
                                        
                                        {"type": "text", "text": last_item.get("type_2")},
                                        {"type": "text", "text": last_item.get("address_2")},
                                        {"type": "text", "text": last_item.get("prod_pros_activi_2")},
                                        {"type": "text", "text": last_item.get("emp_total_2")},
                                        
                                        {"type": "text", "text": last_item.get("type_3")},
                                        {"type": "text", "text": last_item.get("address_3")},
                                        {"type": "text", "text": last_item.get("prod_pros_activi_3")},
                                        {"type": "text", "text": last_item.get("emp_total_3")},
                                    ]
                                }
                            ]
                        }
                    }
                    
                

                url = 'https://graph.facebook.com/v21.0/426469107220591/messages'
                access_token = 'EAAOT6dJD7ZBMBOzdC9eranvzlc4SbFM5RmZCIsKaKyWMKNFZBqmPHQNTZAMop4WcjPMOyuNl8tAlBsM9zi6S5LG7Jys58HXPvqXcMbndmP0mlcBHJz6o3lKKFGmI5CTbWo3o3ZBpN6cqEjbLYUmII2U0LZAshv48ZAiSNKKaXzlZAXY13oCkYBtEEk8JkHaZCbWPskgZDZD'
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 200:
                    _logger.info("WhatsApp message sent successfully.")
                else:
                    _logger.error("Failed to send WhatsApp message.")
    
    
    @http.route('/audit_request_form', type='json', auth='public', methods=['POST'], csrf=False)
    def audit_request_form(self, **kwargs):
        try:
            iso_standard = request.env['tsi.iso.standard'].sudo().search([('standard','=','iso')])
            standard_data = [{"id": str(record.name), "title": record.name} for record in iso_standard[:20]]
            # Sisa data standard
            standard_datas = [{"id": str(record.name), "title": record.name} for record in iso_standard[20:]]
            
            accreditation = request.env['tsi.iso.accreditation'].sudo().search([])
            accreditation_data = [{"id": str(record.name), "title": record.name} for record in accreditation]
        
            body = json.loads(http.request.httprequest.data)
            encrypted_flow_data_b64 = body['encrypted_flow_data']
            encrypted_aes_key_b64 = body['encrypted_aes_key']
            initial_vector_b64 = body['initial_vector']
            
            _logger.info("Request received at /flow:: %s",body)

            decrypted_data, aes_key, iv = self.decrypt_request(encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64)
            _logger.info("💬 Decrypted Request: %s", decrypted_data)
            
            data = decrypted_data.get('data', {})
            standard_names = data.get('iso_standard')
            standards_names = data.get('iso_standards')
            
            tanggal_baru = ""
            exp_date = data.get('exp_date')
            if exp_date and "-" in exp_date:
                try:
                    tahun, bulan, hari = exp_date.split("-")
                    bulan_id = {
                        "01": "Januari", "02": "Februari", "03": "Maret",
                        "04": "April", "05": "Mei", "06": "Juni",
                        "07": "Juli", "08": "Agustus", "09": "September",
                        "10": "Oktober", "11": "November", "12": "Desember"
                    }
                    tanggal_baru = f"{int(hari)} {bulan_id[bulan]} {tahun}"
                except Exception as e:
                    _logger.error("Error processing exp_date: %s, Error: %s", exp_date, str(e))
                        
            SCREEN_RESPONSES = {
                "Audit_Request": {
                    "screen": "Audit_Request",
                    "data": {
                        "standard": standard_data,
                        "standards": standard_datas,
                        "accreditation": accreditation_data
                    }
                },
                "SUMMARY": {
                    "screen": "SUMMARY",
                    "data": {
                        "summary_company_name": f"Company Name : {data.get('company_name')}",
                        "summary_office_address": f"Office Address : {data.get('office_address')}",
                        "summary_scope": f"Scope : {data.get('scope')}",
                        "summary_number_of_employees": f"Number of Employees : {data.get('number_of_employees')}",
                        "summary_project": f"Project : {data.get('project')}",
                        "summary_number_of_employees_p": f"Employees Project : {data.get('number_of_employees_p')}",
                        "summary_contact_person": f"Contact Person : {data.get('contact_person')}",
                        "summary_phone": f"Phone : {data.get('phone')}",
                        "summary_email": f"Email : {data.get('email')}",
                        "summary_standard": f"ISO Standard : {', '.join(standard_names) if standard_names else ''}, {', '.join(standards_names) if standards_names else ''}",
                        "summary_audit_stage": f"Audit Stage : {data.get('audit_stage')}",
                        "summary_accreditations": f"Accreditations : {data.get('accreditations')}",
                        "summary_exp_date": f"Expired Date : {tanggal_baru}",
                        "summary_change_information": f"Change Information : {data.get('change_information')}",
                        "summary_other_notes": f"Other Notes : {data.get('other_notes')}",
                    }
                },
                "SUCCESS": {
                    "screen": "SUCCESS",
                    "data": {
                        "extension_message_response": {
                            "params": {
                                "flow_token": "REPLACE_FLOW_TOKEN",
                                
                                "company_name": "VALUE",
                                "office_address": "VALUE",
                                "scope": "VALUE",
                                "number_of_employees": "VALUE",
                                "project": "VALUE",
                                "number_of_employees_p": "VALUE",
                                "contact_person": "VALUE",
                                "phone": "VALUE",
                                "email": "VALUE",
                                
                                "iso_standard": "VALUE",
                                "iso_standards": "VALUE",
                                "audit_stage": "VALUE",
                                "accreditations": "VALUE",
                                "exp_date": "VALUE",
                                "change_information": "VALUE",
                                "other_notes": "VALUE",
                            }
                        }
                    }
                }
            }
    
            action = decrypted_data.get('action')
            screen = decrypted_data.get('screen')
            flow_token = decrypted_data.get('flow_token')
            
            if action == "ping":
                response = {"data": {"status": "active"}}
            elif action == "INIT":
                response = SCREEN_RESPONSES["Audit_Request"]
                
            elif action == "data_exchange":
                if screen == "Audit_Request":
                    response = SCREEN_RESPONSES["SUMMARY"]
                elif screen == "SUMMARY":
                    response = {
                        **SCREEN_RESPONSES["SUCCESS"], 
                        "data": {
                            "extension_message_response": {
                                "params": {
                                    "flow_token": flow_token,
                                    
                                    "company_name": data.get('company_name',''),
                                    "office_address": data.get('office_address',''),
                                    "scope": data.get('scope',''),
                                    "number_of_employees": data.get('number_of_employees',''),
                                    "project": data.get('project',''),
                                    "number_of_employees_p": data.get('number_of_employees_p',''),
                                    "contact_person": data.get('contact_person',''),
                                    "phone": data.get('phone',''),
                                    "email": data.get('email',''),
                                    
                                    "iso_standard": data.get('iso_standard',''),
                                    "iso_standards": data.get('iso_standards',''),
                                    "audit_stage": data.get('audit_stage',''),
                                    "accreditations": data.get('accreditations',''),
                                    "exp_date" : data.get('exp_date',''),
                                    "change_information" : data.get('change_information','none'),
                                    "other_notes" : data.get('other_notes','none'),
                                    }
                                }
                            }
                        }
                    
                else:
                    raise ValueError(f"Unhandled screen: {screen}")
            else:
                raise ValueError(f"Unhandled action: {action}")
            
            _logger.info("👉 Response to Encrypt: %s", response)
            
            if response and isinstance(response, dict) and response.get('screen') == 'SUCCESS':
                data_success = response.get('data', {}).get('extension_message_response', {}).get('params', {})
                company_name = data_success.get('company_name').strip()
                contact_person = data_success.get('contact_person').strip()
                
                iso_standard = data_success.get('iso_standard',[])
                iso_standards = data_success.get('iso_standards',[])
                if not iso_standard and iso_standards:
                    iso_standard_all = iso_standards if isinstance(iso_standards, list) else [iso_standards]
                elif iso_standard and not iso_standards:
                    iso_standard_all = iso_standard if isinstance(iso_standard, list) else [iso_standard]
                else:
                    iso_standard_all = iso_standard + (iso_standards if isinstance(iso_standards, list) else [iso_standards])
                
                audit_stages=[]
                audit_stage = data_success.get('audit_stage')
                if audit_stage == "Surveilance 1":
                    audit_stages = "surveilance1"
                elif audit_stage == "Surveilance 2":
                    audit_stages = "surveilance2"
                elif audit_stage == "Recertification":
                    audit_stages = "recertification"
                    
                
                
                company = request.env['res.partner'].sudo().search([('name', '=', company_name)], limit=1)
                if company:
                    crm = request.env['tsi.history_kontrak'].sudo().search([('partner_id', '=', company.id)], limit=1)
                    _logger.info("Data CRM : %s",crm)
                    if crm:
                        # run fungsi customer lanjut
                        crm.action_go_to_tsi_crm()
                        
                        accreditation_name = data_success.get('accreditations', '').strip()
                        if accreditation_name:
                            accreditation = request.env['tsi.iso.accreditation'].sudo().search([('name', '=', accreditation_name)], limit=1)
                            _logger.info("Accreditation Name :%s",accreditation)
                        else :
                            _logger.info("Accreditation Tidak ada :%s",accreditation_data)
                        
                        # line
                        line_items = []
                        audit_stage = ''  

                        if crm.tahapan_ori_lines1:
                            audit_stage = 'surveilance1'
                            for tahapan_ori_line in crm.tahapan_ori_lines1:
                                standard_name = tahapan_ori_line.standard.name
                                product = request.env['product.product'].sudo().search([('name', '=', standard_name)], limit=1)
                                mandays_s1_value = tahapan_ori_line.mandays_s1

                                try:
                                    mandays_s1_float = float(mandays_s1_value)
                                except (ValueError, TypeError) as e:
                                    mandays_s1_float = 0.0 
                                
                                line_items.append((0, 0, {
                                    'product_id': product.id if product else False,
                                    'price_lama': mandays_s1_float,
                                    'audit_tahapan': 'Surveillance 1',
                                }))

                        if crm.tahapan_ori_lines2:
                            audit_stage = 'surveilance2'
                            for tahapan_ori_line2 in crm.tahapan_ori_lines2:
                                standard_name = tahapan_ori_line2.standard.name
                                product = request.env['product.product'].sudo().search([('name', '=', standard_name)], limit=1)
                                mandays_s2_value = tahapan_ori_line2.mandays_s2

                                try:
                                    mandays_s2_float = float(mandays_s2_value)
                                except (ValueError, TypeError) as e:
                                    mandays_s2_float = 0.0 

                                line_items.append((0, 0, {
                                    'product_id': product.id if product else False,
                                    'price_lama': mandays_s2_float,
                                    'audit_tahapan': 'Surveillance 2',
                                }))

                        if crm.tahapan_ori_lines_re:
                            audit_stage = 'recertification'
                            for tahapan_ori_line_re in crm.tahapan_ori_lines_re:
                                standard_name = tahapan_ori_line_re.standard.name
                                product = request.env['product.product'].sudo().search([('name', '=', standard_name)], limit=1)
                                mandays_re_value = tahapan_ori_line_re.mandays_rs

                                try:
                                    mandays_re_float = float(mandays_re_value)
                                except (ValueError, TypeError) as e:
                                    mandays_re_float = 0.0 

                                line_items.append((0, 0, {
                                    'product_id': product.id if product else False,
                                    'price_lama': mandays_re_float,
                                    'audit_tahapan': 'Recertification',
                                }))
                                
                        audit_chatbot = request.env['tsi.audit_request_chatbot'].sudo().create({
                            "partner_id": company.id,
                            # value from chatbot
                            "office_address": data_success.get('office_address',''),
                            "invoicing_address": company.invoice_address,
                            "telp": company.phone,
                            "email": data_success.get('email',''),
                            "website": company.website,
                            "cellular": data_success.get('phone',''),
                            "scope": data_success.get('scope',''),
                            "boundaries": company.boundaries,
                            "number_site": company.number_site,
                            "total_emp": data_success.get('number_of_employees',''),
                            
                            # add new field from doc audit request crm
                            "contact_person": data_success.get('contact_person',''),
                            "project": data_success.get('project',''),
                            "total_emp_project": data_success.get('number_of_employees_p',''),
                            "exp_date": data_success.get('exp_date',''),
                            "change_information": data_success.get('change_information',''),
                            "other_notes": data_success.get('other_notes',''),
                            
                            
                            # value get contact
                            # "office_address": company.office_address,
                            # "invoicing_address": company.invoice_address,
                            # "telp": company.phone,
                            # "email": company.email,
                            # "website": company.website,
                            # "cellular": company.mobile,
                            # "scope": company.scope,
                            # "boundaries": company.boundaries,
                            # "number_site": company.number_site,
                            # "total_emp": company.total_emp,

                            "accreditation": accreditation.id,
                            'iso_standard_ids': request.env['tsi.iso.standard'].sudo().search([('name', 'in', iso_standard_all)]).ids,
                            "audit_stage": audit_stages,
                            
                            "line_ids" : line_items
                        })
                        _logger.info("Success Action Lanjut CRM ")
                        _logger.info("Success Create Audit Request %s",audit_chatbot)
                        data_response_audit_request_form.clear()
                        data_response_audit_request_form.append(data_success)
                        _logger.info("Data Array http: %s",data_response_audit_request_form)
                        threading.Thread(target=delayed_execution, args=(self.send_audit_request_form_success, 2)).start()
                    else:
                        _logger.info("No CRM Data Found for Partner: %s", company.name)
                else:
                    _logger.info("Company Not Found", company_name)
                    

            encrypted_response = self.encrypt_response(response, aes_key, iv)
            request._json_response = alternative_response.__get__(request, JsonRequest)
            return encrypted_response

        except Exception as e:
            _logger.error(f"Error: {str(e)}")
            return Response(f"Error: {str(e)}", content_type='text/plain')

    def send_audit_request_form_success(self):
        if data_response_audit_request_form:
            last_item = data_response_audit_request_form[-1]
            _logger.info("array def last item:%s",last_item)
            phone = last_item.get("phone")
            
            if phone:
                phones = re.sub(r"\D", "", phone)
                if phones.startswith("0"):
                    phones = "62" + phones[1:]
                elif phones.startswith("62"):
                    phones = phones 
                else:
                    raise ValueError(f"Invalid phone number format: {phone}")
                
                iso_standard = last_item.get('iso_standard', [])
                if isinstance(iso_standard, str):
                    iso_standard = [iso_standard]

                iso_standards = last_item.get('iso_standards', [])
                if isinstance(iso_standards, str):
                    iso_standards = [iso_standards]

                iso_standard_all = iso_standard + iso_standards
                iso_standard_string = ", ".join(iso_standard_all)
                
                exp_date = last_item.get('exp_date')
                if exp_date and "-" in exp_date:
                    try:
                        tahun, bulan, hari = exp_date.split("-")
                        bulan_id = {
                            "01": "Januari", "02": "Februari", "03": "Maret",
                            "04": "April", "05": "Mei", "06": "Juni",
                            "07": "Juli", "08": "Agustus", "09": "September",
                            "10": "Oktober", "11": "November", "12": "Desember"
                        }
                        tanggal_baru = f"{int(hari)} {bulan_id[bulan]} {tahun}"
                    except Exception as e:
                        _logger.error("Error processing exp_date: %s, Error: %s", exp_date, str(e))
                                     
                payload = {
                    "messaging_product": "whatsapp",
                    "to": phones,
                    "type": "template",
                    "template": {
                        "name": "success_audit_request_dev",
                        "language": {
                            "code": "en_US"
                        },
                        "components": [
                            {
                                "type": "body",
                                "parameters": [
                                    {"type": "text", "text": last_item.get("company_name")},
                                    {"type": "text", "text": last_item.get("office_address")},
                                    {"type": "text", "text": last_item.get("scope")},
                                    {"type": "text", "text": last_item.get("number_of_employees")},
                                    {"type": "text", "text": last_item.get("project")},
                                    {"type": "text", "text": last_item.get("number_of_employees_p")},
                                    {"type": "text", "text": last_item.get("contact_person")},
                                    {"type": "text", "text": phone},
                                    {"type": "text", "text": last_item.get("email")},
                                    {"type": "text", "text": iso_standard_string},
                                    {"type": "text", "text": last_item.get("audit_stage")},
                                    {"type": "text", "text": last_item.get("accreditations")},
                                    {"type": "text", "text": tanggal_baru},
                                    {"type": "text", "text": last_item.get("change_information")},
                                    {"type": "text", "text": last_item.get("other_notes")}
                                ]
                            }
                        ]
                    }
                }

                url = 'https://graph.facebook.com/v21.0/426469107220591/messages'
                access_token = 'EAAOT6dJD7ZBMBOzdC9eranvzlc4SbFM5RmZCIsKaKyWMKNFZBqmPHQNTZAMop4WcjPMOyuNl8tAlBsM9zi6S5LG7Jys58HXPvqXcMbndmP0mlcBHJz6o3lKKFGmI5CTbWo3o3ZBpN6cqEjbLYUmII2U0LZAshv48ZAiSNKKaXzlZAXY13oCkYBtEEk8JkHaZCbWPskgZDZD'
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 200:
                    _logger.info("WhatsApp message sent successfully.")
                else:
                    _logger.error("Failed to send WhatsApp message.")
    
    @http.route('/ticket_complain', type='json', auth='public', methods=['POST'], csrf=False)
    def ticket_complain(self, **kwargs):
        try:
            iso_standard = request.env['tsi.iso.standard'].sudo().search([('standard','=','iso')])
            standard_data = [{"id": str(record.name), "title": record.name} for record in iso_standard[:20]]
            # Sisa data standard
            standard_datas = [{"id": str(record.name), "title": record.name} for record in iso_standard[20:]]
            
        
            body = json.loads(http.request.httprequest.data)
            encrypted_flow_data_b64 = body['encrypted_flow_data']
            encrypted_aes_key_b64 = body['encrypted_aes_key']
            initial_vector_b64 = body['initial_vector']
            
            _logger.info("Request received at /flow:: %s",body)

            decrypted_data, aes_key, iv = self.decrypt_request(encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64)
            _logger.info("💬 Decrypted Request: %s", decrypted_data)
            
            data = decrypted_data.get('data', {})
            standard_names = data.get('iso_standard')
            standards_names = data.get('iso_standards')
            
            tanggal_baru = ""
            complaint_date = data.get('complaint_date')
            if complaint_date and "-" in complaint_date:
                try:
                    tahun, bulan, hari = complaint_date.split("-")
                    bulan_id = {
                        "01": "Januari", "02": "Februari", "03": "Maret",
                        "04": "April", "05": "Mei", "06": "Juni",
                        "07": "Juli", "08": "Agustus", "09": "September",
                        "10": "Oktober", "11": "November", "12": "Desember"
                    }
                    tanggal_baru = f"{int(hari)} {bulan_id[bulan]} {tahun}"
                except Exception as e:
                    _logger.error("Error processing complaint_date: %s, Error: %s", complaint_date, str(e))
                        
            SCREEN_RESPONSES = {
                "Ticket_Complain": {
                    "screen": "Ticket_Complain",
                    "data": {
                        "standard": standard_data,
                        "standards": standard_datas
                    }
                },
                "SUMMARY": {
                    "screen": "SUMMARY",
                    "data": {
                        "summary_company_name": f"Company Name: {data.get('company_name')}",
                        "summary_address": f"Address : {data.get('address')}",
                        "summary_pic_name": f"PIC Name : {data.get('pic_name')}",
                        "summary_jabatan": f"Jabatan : {data.get('jabatan')}",
                        "summary_phone": f"Phone: {data.get('phone')}",
                        "summary_email": f"Email : {data.get('email')}",
                        "summary_standard": f"Standard : {', '.join(standard_names) if standard_names else ''}, {', '.join(standards_names) if standards_names else ''}",
                        "summary_audit_stage": f"Audit Stage : {data.get('audit_stage')}",
                        "summary_complaint_date" : f"Complaint Date : {tanggal_baru}",
                        "summary_complaint_media": f"Complaint Media : {data.get('complaint_media')}",
                        "summary_compline_details": f"Complinet Details : {data.get('compline_details')}"
                    }
                },
                "SUCCESS": {
                    "screen": "SUCCESS",
                    "data": {
                        "extension_message_response": {
                            "params": {
                                "flow_token": "REPLACE_FLOW_TOKEN",
                                
                                "company_name": "Company Name",
                                "address": "Address",
                                "pic_name": "Contact Person",
                                "jabatan": "Jabatan",
                                "phone": "Phone",
                                "email": "Email",
                                "standard": "Standard",
                                "standards": "Standards",
                                "audit_stage": "Audit Stage",
                                "complaint_date": "Complaint Date",
                                "complaint_media": "Complaint Media",
                                "compline_details": "Compline Details"
                            }
                        }
                    }
                }
            }

            action = decrypted_data.get('action')
            screen = decrypted_data.get('screen')
            flow_token = decrypted_data.get('flow_token')
            
            if action == "ping":
                response = {"data": {"status": "active"}}
            elif action == "INIT":
                response = SCREEN_RESPONSES["Ticket_Complain"]
                
            elif action == "data_exchange":
                if screen == "Ticket_Complain":
                    response = SCREEN_RESPONSES["SUMMARY"]
                elif screen == "SUMMARY":
                    response = {
                        **SCREEN_RESPONSES["SUCCESS"], 
                        "data": {
                            "extension_message_response": {
                                "params": {
                                    "flow_token": flow_token,
                                
                                    "company_name": data.get('company_name',''),
                                    "address": data.get('address',''),
                                    "pic_name": data.get('pic_name',''),
                                    "jabatan": data.get('jabatan',''),
                                    "phone": data.get('phone',''),
                                    "email": data.get('email',''),
                                    "standard": data.get('iso_standard',''),
                                    "standards": data.get('iso_standards',''),
                                    "audit_stage": data.get('audit_stage',''),
                                    "complaint_date": data.get('complaint_date',''),
                                    "complaint_media": data.get('complaint_media',''),
                                    "compline_details": data.get('compline_details','')
                                    }
                                }
                            }
                        }
                    
                else:
                    raise ValueError(f"Unhandled screen: {screen}")
            else:
                raise ValueError(f"Unhandled action: {action}")
            
            _logger.info("👉 Response to Encrypt: %s", response)
            
            if response and isinstance(response, dict) and response.get('screen') == 'SUCCESS':
                data_success = response.get('data', {}).get('extension_message_response', {}).get('params', {})
                company_name = data_success.get('company_name').strip()
                
                iso_standard = data_success.get('standard',[])
                iso_standards = data_success.get('standards',[])
                if not iso_standard and iso_standards:
                    iso_standard_all = iso_standards if isinstance(iso_standards, list) else [iso_standards]
                elif iso_standard and not iso_standards:
                    iso_standard_all = iso_standard if isinstance(iso_standard, list) else [iso_standard]
                else:
                    iso_standard_all = iso_standard + (iso_standards if isinstance(iso_standards, list) else [iso_standards])
                
                
                audit_stages=[]
                audit_stage = data_success.get('audit_stage')
                if audit_stage == "Initial Audit":
                    audit_stages = "initial_audit"
                elif audit_stage == "Surveilance 1":
                    audit_stages = "surveilance_1"
                elif audit_stage == "Surveilance 2":
                    audit_stages = "surveilance_2"
                elif audit_stage == "Recertification":
                    audit_stages = "recertification"
                    
                complaint_medias=[]
                complaint_media = data_success.get('complaint_media')
                if complaint_media == "Phone":
                    complaint_medias = "phone"
                elif complaint_media == "Email":
                    complaint_medias = "email"
                elif complaint_media == "Website":
                    complaint_medias = "website"
                
                
                
                company = request.env['res.partner'].sudo().search([('name', '=', company_name)], limit=1)
                if company:
                    ticket_complain = request.env['tsi.partner_feedback'].sudo().create({
                        "nama_perusahaan": company.id,
                        "alamat": data_success.get('address',''),
                        "nama_pic": data_success.get('pic_name',''),
                        "jabatan": data_success.get('jabatan',''),
                        "telepon": data_success.get('phone',''),
                        "email": data_success.get('email',''),
                        "standar": request.env['tsi.iso.standard'].sudo().search([('name', 'in', iso_standard_all)]).ids,
                        "tahap_audit": audit_stages,
                        "tgl_keluhan": data_success.get('complaint_date',''),
                        "media_keluhan": complaint_medias,
                        "deskripsi": data_success.get('compline_details','')
                    })
                    _logger.info("Success Create Ticket Complain: %s",ticket_complain)
                    no_ticket = ticket_complain.name
                    _logger.info("No Ticket: %s", no_ticket)
        
                    data_response_ticket_complain.clear()
                    data_success["no_ticket"] = no_ticket
                    data_response_ticket_complain.append(data_success)
                    _logger.info("Data Array http: %s",data_response_ticket_complain)
                    threading.Thread(target=delayed_execution, args=(self.send_ticket_complain_success, 2)).start()
                    

            encrypted_response = self.encrypt_response(response, aes_key, iv)
            request._json_response = alternative_response.__get__(request, JsonRequest)
            return encrypted_response

        except Exception as e:
            _logger.error(f"Error: {str(e)}")
            return Response(f"Error: {str(e)}", content_type='text/plain')
        
    def send_ticket_complain_success(self):
        if data_response_ticket_complain:
            last_item = data_response_ticket_complain[-1]
            _logger.info("array def last item:%s",last_item)
            phone = last_item.get("phone")
            
            if phone:
                phones = re.sub(r"\D", "", phone)
                if phones.startswith("0"):
                    phones = "62" + phones[1:]
                elif phones.startswith("62"):
                    phones = phones
                else:
                    raise ValueError(f"Invalid phone number format: {phone}")
                
                _logger.info("Transformed phone number: %s", phones)
                
                iso_standard = last_item.get('standard', [])
                if isinstance(iso_standard, str):
                    iso_standard = [iso_standard]

                iso_standards = last_item.get('standards', [])
                if isinstance(iso_standards, str):
                    iso_standards = [iso_standards]

                iso_standard_all = iso_standard + iso_standards
                iso_standard_string = ", ".join(iso_standard_all)
                complaint_date = last_item.get('complaint_date')
                if complaint_date and "-" in complaint_date:
                    try:
                        tahun, bulan, hari = complaint_date.split("-")
                        bulan_id = {
                            "01": "Januari", "02": "Februari", "03": "Maret",
                            "04": "April", "05": "Mei", "06": "Juni",
                            "07": "Juli", "08": "Agustus", "09": "September",
                            "10": "Oktober", "11": "November", "12": "Desember"
                        }
                        tanggal_baru = f"{int(hari)} {bulan_id[bulan]} {tahun}"
                    except Exception as e:
                        _logger.error("Error processing complaint_date: %s, Error: %s", complaint_date, str(e))
                                     
                payload = {
                    "messaging_product": "whatsapp",
                    "to": phones,
                    "type": "template",
                    "template": {
                        "name": "success_ticket_complain_dev",
                        "language": {
                            "code": "en_US"
                        },
                        "components": [
                            {
                                "type": "body",
                                "parameters": [
                                    {"type": "text", "text": last_item.get("company_name")},
                                    {"type": "text", "text": last_item.get("address")},
                                    {"type": "text", "text": last_item.get("pic_name")},
                                    {"type": "text", "text": last_item.get("jabatan")},
                                    {"type": "text", "text": last_item.get("phone")},
                                    {"type": "text", "text": last_item.get("email")},
                                    {"type": "text", "text": iso_standard_string},
                                    {"type": "text", "text": last_item.get("audit_stage")},
                                    {"type": "text", "text": tanggal_baru},
                                    {"type": "text", "text": last_item.get("complaint_media")},
                                    {"type": "text", "text": last_item.get("compline_details")}
                                ]
                            }
                        ]
                    }
                }

                url = 'https://graph.facebook.com/v21.0/426469107220591/messages'
                access_token = 'EAAOT6dJD7ZBMBOzdC9eranvzlc4SbFM5RmZCIsKaKyWMKNFZBqmPHQNTZAMop4WcjPMOyuNl8tAlBsM9zi6S5LG7Jys58HXPvqXcMbndmP0mlcBHJz6o3lKKFGmI5CTbWo3o3ZBpN6cqEjbLYUmII2U0LZAshv48ZAiSNKKaXzlZAXY13oCkYBtEEk8JkHaZCbWPskgZDZD'
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 200:
                    _logger.info("WhatsApp message sent successfully.")
                else:
                    _logger.error("Failed to send WhatsApp message.")
    