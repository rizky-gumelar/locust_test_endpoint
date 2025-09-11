from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
import urllib2
import json
from openerp.exceptions import ValidationError
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime, timedelta
from ...text import IS_PRODUCTION
import logging

LOKASI_CHECK_IN = [{
	'name': 'pusat',
	'detail': {
		'lokasi': 'siba surya pusat',
		'latitude': -6.951359, #- 6.9514305,
		'longitude': 110.461566, #110.4611244,
		'radius': 517
    	}
    }]

UNIT_STATUS = (
    ('active', 'Active'),
    ('readywithoutdriver', 'Ready Without Driver'),
    ('ready', 'Ready'),
    ('inactive', 'Inactive')
)
	
class KarloMasterFleet(models.Model):
	"""
	Model untuk menyimpan data master Fleet.
	"""
	_name = "sisu.karlo.master.fleet"
	_description = "Model Karlo Master Fleet"
	# _sql_constraints = (
    #     ("sisu_karlo_fleet_policenumber", "UNIQUE(trucknumber)", "No. Polisi must be unique."),
    # )

	_id = fields.Char("_Id")
	name = fields.Char("Name", compute="compute_name", store=True,)
	trucknumber = fields.Char("No. Lambung")
	policenumber = fields.Char("No. Polisi")
	machinenumber = fields.Char("No. Mesin")
	brand = fields.Char("Brand")
	productionyear = fields.Char("Production Year")
	color = fields.Char("Color")
	long = fields.Float(digits=dp.get_precision('Account'), string="Long")
	wide = fields.Float(digits=dp.get_precision('Account'), string="Wide")
	high = fields.Float(digits=dp.get_precision('Account'), string="High")
	weightmin = fields.Float(digits=dp.get_precision('Account'), string="Min Weight")
	weightmax = fields.Float(digits=dp.get_precision('Account'), string="Max Weight")
	volumemin = fields.Float(digits=dp.get_precision('Account'), string="Min Volume")
	volumemax = fields.Float(digits=dp.get_precision('Account'), string="Max Volume")
	stnknumber = fields.Char("No. STNK")
	stnkactiveperiodefrom = fields.Char("STNK periode from")
	stnkactiveperiodeto = fields.Char("STNK periode to")
	kirnumber = fields.Char("No. Kir")
	kiractiveperiodefrom = fields.Char("Kir periode from")
	kiractiveperiodeto = fields.Char("Kir periode to")
	cargotype = fields.Char("Cargo Type", default="Solid tanpa kemasan/tanpa pallet")
	trucktype = fields.Char("Truck Type", default="Pickup Box")
	currentcity = fields.Char("Current City", default="KOTA SEMARANG")
	pending_sj_fleets_karlo = fields.One2many("sisu.karlo.master.fleet.pending_sj", "fleet_karlo_id", "Pending SJ")
	head_id = fields.Many2one(comodel_name="sisu.niaga.head", compute="get_head", store=True, string="Head")
	transporter_id = fields.Many2one(comodel_name="sisu.karlo.master.transporter", string="Transporter")
	status = fields.Char("Status Monitoring")
	status_order = fields.Char("Status Order")
	status_dt = fields.Datetime(string="Status Monitoring On")
	last_order = fields.Char("Last Order")
	organization_id = fields.Many2one("sisu.marketing.organization", "Organization")
	orderentry_id = fields.Many2one("sisu.karlo.order", "Order Entry")
	label = fields.Char("Label Truck Karlo")
	labelissue = fields.Char("Notification Karlo")
	
	checkin_dt = fields.Datetime(string="Check In")
	cekin_cekout_history_last_id = fields.Many2one("sisu.karlo.master.fleet.history.cekincekout", "History Check-In Check-Out Id")
	cekin_cekout_historys = fields.One2many("sisu.karlo.master.fleet.history.cekincekout", "fleet_karlo_id", "History Check-In Check-Out")
	mr_id = fields.Many2one("sisu.tk.mr", "Maintenance Request")

	is_active = fields.Boolean('Is Active', related="head_id.is_active", readonly=True)
	unit_status = fields.Selection(UNIT_STATUS, 'Unit Status', related="head_id.unit_status",)

	info = fields.Char("Info")
	cron_gps_dt = fields.Datetime(string="Cron GPS")

	gps_area = fields.Char(string='GPS Area')
	gps_locations = fields.One2many("sisu.karlo.master.fleet.gpslocation", "fleet_id", "GPS Location")
	
	@api.depends("policenumber")
	def compute_name(self):
		for record in self:
			if record.policenumber:
				record.name = (record.policenumber).upper()

	@api.multi
	def unlink(self):
		return super(KarloMasterFleet, self).unlink()				

	@api.multi
	def post_fleet(self, old_policenumber, method):
		METHOD_POST = 'POST'
		if method == 'create':
			METHOD_POST = 'POST'
		elif method == 'update':
			METHOD_POST = 'PUT'
		elif method == 'delete':
			METHOD_POST = 'DELETE'

		for record in self:
			if record.policenumber:
				ROLE = 'trans'
				address = '/{}/{}/{}'.format("fleet", old_policenumber, method)
				config_api = self.env["sisu.karlo.config.api"].suspend_security().search([('name', '=', 'Karlo'), ('is_active', '=', True)], limit=1, order="id desc")
				
				param = {
					"truckNumber": record.trucknumber,
					"policeNumber": record.policenumber,
					"machineNumber": record.machinenumber,
					"brand": record.brand,
					"productionYear": record.productionyear,
					"color": record.color,
					"long": record.long,
					"wide": record.wide,
					"high": record.high,
					"weightMin": record.weightmin,
					"weightMax": record.weightmax,
					"volumeMin": record.volumemin,
					"volumeMax": record.volumemax,
					"stnkNumber": record.stnknumber,
					"kirNumber": record.kirnumber,
					"stnkActivePeriodeFrom": record.stnkactiveperiodefrom,
					"stnkActivePeriodeTo": record.stnkactiveperiodeto,
					"kirActivePeriodeFrom": record.kiractiveperiodefrom,
					"kirActivePeriodeTo": record.kiractiveperiodeto,
					"cargoType": [record.cargotype],
					"truckType": record.trucktype,
					"currentCity": record.currentcity,
					"fotoStnk": "",
					"fotoKir": "",
					"fotoTruck": ""
				}
				if config_api.id:
					result = config_api.karloApiPost(address, ROLE, param, METHOD_POST)
					json_dumps = json.dumps(result)
					raw_data = json.loads(json_dumps)
					if raw_data:
						if raw_data["statuscode"] == 200:
							return record.policenumber
						else:
							raise ValidationError(raw_data["message"])
				else:
					raise ValidationError("Konfigurasi API belum di setting, Silahkan Hubungi ICT.")

	@api.multi
	def get_fleet(self, policenumber):
		METHOD_POST = 'GET'
		param = {}
		count = 0

		for record in self:
			if policenumber:
				ROLE = 'trans'
				address = '{}'.format('/fleet?filtered=[{"id":"policeNumber","value":"'+policenumber+'","type":"like"}]')
				config_api = self.env["sisu.karlo.config.api"].suspend_security().search([('name', '=', 'Karlo'), ('is_active', '=', True)], limit=1, order="id desc")
				
				if config_api.id:
					result = config_api.karloApiPost(address, ROLE, param, METHOD_POST)
					json_dumps = json.dumps(result)
					raw_data = json.loads(json_dumps)
					if raw_data:
						if raw_data["statuscode"] == 200:
							if raw_data["data"]:
								count = len(raw_data["data"]["data"])
						else:
							raise ValidationError(raw_data["message"])
				else:
					raise ValidationError("Konfigurasi API belum di setting, Silahkan Hubungi ICT.")
		return count	

	@api.depends("policenumber")
	def get_head(self):
		for record in self:
			if record.policenumber:
				head_id = self.env["sisu.niaga.head"].suspend_security().search([('nopol', '=', record.policenumber)], limit=1, order="id desc")
				if head_id:
					record.head_id = head_id.id		

	@api.multi
	def get_head_all(self):
		head_ids = self.env["sisu.karlo.master.fleet"].suspend_security().search([], limit=5000, order="id desc")
		for rec in head_ids:
			if rec.policenumber:
				print(rec.policenumber)
				head_id = self.env["sisu.niaga.head"].suspend_security().search([('nopol', '=', rec.policenumber)], limit=1, order="id desc")
				if head_id:
					rec.head_id = head_id.id    

	@api.multi
	def update_fleet_label_karlo(self):
		method = 'update'
		METHOD_POST = 'PUT'
		TEXT = ''
		TEXT_ISSUE = ''

		if self.label or self.label != '':
			TEXT = self.label

		if self.labelissue or self.labelissue != '':
			TEXT_ISSUE = self.labelissue	

		if not self.policenumber:
			raise ValidationError('Nomor Polisi Tidak Boleh Kosong')

		armada_driver = self.env["sisu.niaga.armada_driver"].suspend_security().search([("active", "=", True),("nopol", "=", self.policenumber)], limit=1, order="id desc")
		if armada_driver:
			armada = armada_driver.armada_id

			ROLE = 'trans'
			address = '/{}/{}/{}'.format("fleet", self.policenumber, method)
			config_api = self.env["sisu.karlo.config.api"].suspend_security().search([('name', '=', 'Karlo'), ('is_active', '=', True)], limit=1, order="id desc")

			long = armada.armada_type_id.length if armada.armada_type_id.id == 4 else armada.nolambung_bed_id.bed_model_id.length
			wide = armada.armada_type_id.width if armada.armada_type_id.id == 4 else armada.nolambung_bed_id.bed_model_id.width
			high = armada.armada_type_id.height if armada.armada_type_id.id == 4 else armada.nolambung_bed_id.bed_model_id.height

			param = {
				"truckNumber": 	armada.nolambung_head_id.nolambung,
				"policeNumber": armada.nopol,
				"machineNumber": armada.nolambung_head_id.nomesin,
				"brand": armada.nolambung_head_id.brand_unit_id.name,
				"productionYear": armada.nolambung_head_id.manufaturing_year,
				"color": armada.nolambung_head_id.warna,
				"long": long if long else 0,
				"wide": wide if wide else 0,
				"high": high if high else 0,
				"weightMin": "0",
				"weightMax": armada.armada_type_id.tonase_maksimal * 1000,
				"volumeMin": "0",
				"volumeMax": armada.armada_type_id.kubikasi_maksimal,
				# "stnkNumber": armada.nolambung_head_id.asset_number.stnk_id.name,
				# "stnkActivePeriodeFrom": armada.nolambung_head_id.asset_number.stnk_id.dt_exp,
				# "stnkActivePeriodeTo": armada.nolambung_head_id.asset_number.stnk_id.dt_exp_stnk,
				# "kirNumber": armada.nolambung_head_id.asset_number.keur_head_id.name,
				# "kirActivePeriodeFrom": armada.nolambung_head_id.asset_number.keur_head_id.extension_period,
				# "kirActivePeriodeTo": armada.nolambung_head_id.asset_number.keur_head_id.dt_expired,
				"stnkNumber": armada.nolambung_head_id.nolambung,
				"kirNumber": armada.nolambung_head_id.nolambung,
				"stnkActivePeriodeFrom": '2022-04-09T02:05:24.431Z',
				"stnkActivePeriodeTo": '2025-04-09T02:05:24.431Z',
				"kirActivePeriodeFrom": '2022-04-09T02:05:24.431Z',
				"kirActivePeriodeTo": '2025-04-09T02:05:24.431Z',
				"cargoType": ["Solid tanpa kemasan/tanpa pallet"],
				"truckType": armada.armada_type_id.trucktype_id.name,
				"currentCity": "KOTA SEMARANG",
				"fotoStnk": "",
				"fotoKir": "",
				"fotoTruck": "",
				"status": "",
				"axle": int(armada.nolambung_head_id.head_model_id.axle_no or 0) + int(armada.nolambung_bed_id.bed_model_id.axle_no or 0), #Axle Number head + bed
				"label": TEXT,
				"labelIssue": TEXT_ISSUE
			}
			if config_api.id:
				result = config_api.karloApiPost(address, ROLE, param, METHOD_POST)
				
				json_dumps = json.dumps(result)
				raw_data = json.loads(json_dumps)
				if raw_data:
					if raw_data["statuscode"] == 200:
						return 'success'
					# else:
					# 	raise ValidationError(raw_data["message"])
			else:
				raise ValidationError("Konfigurasi API belum di setting, Silahkan Hubungi ICT.")

	@api.multi
	def get_fleet_location(self):
		METHOD_POST = 'GET'
		ROLE = 'mnger'
		address = '/{}'.format("all-location")
		param = {}

		config_api = self.env["sisu.karlo.config.api"].suspend_security().search([('name', '=', 'Karlo'), ('is_active', '=', True)], limit=1, order="id desc")
		
		if config_api.id:
			result = config_api.karloApiPost(address, ROLE, param, METHOD_POST)
			json_dumps = json.dumps(result)
			raw_data = json.loads(json_dumps)
			if raw_data:
				if raw_data["statuscode"] == 200:
					return raw_data["data"]
				else:
					raise ValidationError(raw_data["message"])

	@api.multi				
	def get_distance_meter(self, lat_awal, lon_awal, lat_akhir, lon_akhir):
		# Approximate radius of earth in km
		R = 6373.0

		lat_awal_r = radians(lat_awal)
		lon_awal_r = radians(lon_awal)
		lat_akhir_r = radians(lat_akhir)
		lon_akhir_r = radians(lon_akhir)

		dlon = lon_akhir_r - lon_awal_r
		dlat = lat_akhir_r - lat_awal_r

		a = sin(dlat / 2)**2 + cos(lat_awal_r) * cos(lat_akhir_r) * sin(dlon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))
		return (R * c) * 1000

	@api.multi
	def get_geocode(self, latitude, longitude):
		result = ""
		try:
			base_url = "http://10.0.0.47/"
			# base_url = "http://nominatim.openstreetmap.org/"
			url = '{}{}{}{}{}{}'.format(base_url, 'reverse?lat=', latitude, '&lon=', longitude, '&format=jsonv2')
			req = urllib2.Request(url)
			req.add_header('Content-Type', 'application/json')
			response = urllib2.urlopen(req, json.dumps({}))
			raw_data = response.read()
			data = json.loads(raw_data)
			if data['display_name']:
				result = str(data['display_name']).encode('utf8')
		except urllib2.URLError as err:
			result = str(err.reason).encode('utf8')
		return result

	@api.model
	def cron_checkin_checkout(self):
		_logger = logging.getLogger(__name__)

		locations = self.get_fleet_location()
		radius = LOKASI_CHECK_IN[0]['detail']['radius']
		lat_awal = LOKASI_CHECK_IN[0]['detail']['latitude']
		lon_awal = LOKASI_CHECK_IN[0]['detail']['longitude']
		lokasi = LOKASI_CHECK_IN[0]['detail']['lokasi']

		log = "CRON GPS CHECKIN?CHECKOUT --> "
		for loc in locations:
			if loc['policeNumber'] and loc['lastLocation']:
				fleet_id = self.env["sisu.karlo.master.fleet"].suspend_security().search([("is_active", "=", True), ("head_id", "!=", False), ("policenumber", "=", loc['policeNumber'])], limit=1, order="id desc")
				if fleet_id:
					lon_akhir = float(loc["lastLocation"]["longitude"])
					lat_akhir = float(loc["lastLocation"]["latitude"])

					if not lon_akhir or not lat_akhir or lon_akhir == 0 or lat_akhir == 0:
						print(' ---- CEK LONGLAT NULL ----\nnopol : {}\ntime : {}'.format(loc['policeNumber'], (datetime.now() + timedelta(hours=float(7))).strftime('%d-%m-%Y %H:%M:%S')))
						continue

					distance = self.get_distance_meter(lat_awal, lon_awal, lat_akhir, lon_akhir)
					gps_updatedat =  datetime.strptime(loc["lastLocation"]["updatedAt"], '%Y-%m-%dT%H:%M:%S.%fZ')
					gps_updatedat_plus7 = (gps_updatedat + timedelta(hours=float(7))).strftime('%d-%m-%Y %H:%M:%S')
					cron_update_plus7 = (datetime.now() + timedelta(hours=float(7))).strftime('%d-%m-%Y %H:%M:%S')

					# fleet_id.write({'info': 'lat:{}\nlon:{}\ndistance_from_pst:{}\ngpskarlo_updt:{}\ncron_updt:{}'.format(lat_akhir, lon_akhir, int(distance), gps_updatedat_plus7, cron_update_plus7)})

					# fleet_id.weightmin = distance

					# init_update = {'info': 'lat:{}\nlon:{}\ndistance_from_pst:{}\ngpskarlo_updt:{}\ncron_updt:{}'.format(lat_akhir, lon_akhir, int(distance), gps_updatedat_plus7, cron_update_plus7)}
					# new_update = {}

					log += ' nopol : {} lat : {} lon : {} distance : {} gps_updatedat : {}'.format(fleet_id.policenumber, lat_akhir, lon_akhir, distance, gps_updatedat)

					if int(distance) <= radius:
						mr_id = self.env["sisu.tk.mr"].search([
								("license_plate", "=", loc['policeNumber']),
								("request_type", "in", [False, 'regular']),
								("type_id", "=", "emergency"),
								("state", "not in", ["done", "reject", "cancel", "expired"])
							], order="date_request desc", limit=1)
						
						# cek jika belum ada histori maka akan dibuatkan
						if not fleet_id.cekin_cekout_history_last_id:
							history_id = self.env['sisu.karlo.master.fleet.history.cekincekout'].suspend_security().create({
								"name": '{} {}'.format(lokasi.upper(), (gps_updatedat + timedelta(hours=float(7))).strftime('%d-%m-%Y %H:%M:%S')),
								"fleet_karlo_id": fleet_id.id,
								"lokasi": lokasi.upper(),
								"checkin_dt": gps_updatedat,
								"latitude": lat_akhir,
								"longitude": lon_akhir,
								"mr_id": mr_id.id
							})
							if history_id:
								# new_update = {'cekin_cekout_history_last_id': history_id.id, 'checkin_dt': gps_updatedat, 'mr_id': mr_id.id}
								fleet_id.write({
									'cekin_cekout_history_last_id': history_id.id,
									'checkin_dt': gps_updatedat,
									'mr_id': mr_id.id,
									# 'info': 'lat:{}\nlon:{}\ndistance_from_pst:{}\ngpskarlo_updt:{}\ncron_updt:{}'.format(lat_akhir, lon_akhir, int(distance), gps_updatedat_plus7, cron_update_plus7)
									'cron_gps_dt': fields.Datetime.now()
									})
								
								log += ' in area pusat ->  cekin_cekout_history_last_id : {} mr_id : {}'.format(history_id.id, mr_id.id)
						else:
							# cek jika ada mr baru maka akan di update
							if mr_id:
								if not mr_id.id == fleet_id.cekin_cekout_history_last_id.mr_id.id:
									fleet_id.cekin_cekout_history_last_id.mr_id = mr_id.id
									fleet_id.mr_id = mr_id.id
						
					elif int(distance) > radius:
						if fleet_id.cekin_cekout_history_last_id and fleet_id.checkin_dt:
							if fleet_id.mr_id:
								mr_reg_ids = self.env["sisu.tk.mr.reg"].suspend_security().search([("maintenance_request_id", "=", fleet_id.mr_id.id), ("state", "=", 'in')], order="id desc")
								for mr_reg_id in mr_reg_ids:
									mr_reg_id.to_out()
									mr_reg_id.note = 'CheckOut By Geofencing'

							history_checkin_id = self.env["sisu.karlo.master.fleet.history.cekincekout"].suspend_security().search([("id", "=", fleet_id.cekin_cekout_history_last_id.id)], limit=1, order="id desc")
							if history_checkin_id:
								history_checkin_id.write({
									"checkout_dt": gps_updatedat,
									"latitude": lat_akhir,
									"longitude": lon_akhir
									})
								# new_update = {'cekin_cekout_history_last_id': False, 'checkin_dt': False, 'mr_id': False}
								fleet_id.write({
									'cekin_cekout_history_last_id': False,
									'checkin_dt': False,
									# 'mr_id': False, # tidak usah dikosongkan karena untuk history mr yang terakhir
									# 'info': 'lat:{}\nlon:{}\ndistance_from_pst:{}\ngpskarlo_updt:{}\ncron_updt:{}'.format(lat_akhir, lon_akhir, int(distance), gps_updatedat_plus7, cron_update_plus7)
									'cron_gps_dt': fields.Datetime.now()
									}) 
								
								log += ' out area pusat ->  checkout_dt : {}'.format(gps_updatedat)
					log += ', '	
		_logger.info(log)	
					# init_update.update(new_update)
					# print(init_update)
					# fleet_id.write(init_update)		
					# print('result : {}'.format(fleet_id.name))


	@api.multi
	def update_fleet_available(self, available=True, tour_id=False):
		METHOD_POST = 'PUT'

		if self.policenumber and IS_PRODUCTION:
			ROLE = 'trans'
			address = '/{}'.format("available-truck")
			config_api = self.env["sisu.karlo.config.api"].suspend_security().search([('name', '=', 'Karlo'), ('is_active', '=', True)], limit=1, order="id desc")

			param = {
				"policeNumber": self.policenumber,
				"available": available
			}

			if config_api.id:
				result = config_api.karloApiPost(address, ROLE, param, METHOD_POST)
				json_dumps = json.dumps(result)
				raw_data = json.loads(json_dumps)
				# raise ValidationError(raw_data)
				if raw_data:
					if raw_data["statuscode"] == 200:
						if tour_id:
							if tour_id.karlo_orderentry_id:
								order_id = tour_id.karlo_orderentry_id.suspend_security()
								if order_id:
									if available:
										for status in order_id.statushistorys:
											order_id.write({'activestatustruck': status.activestatustruck, 'activestatustruck_dt': status.createdat_dt})
											self.suspend_security().write({'status': status.activestatustruck, 'status_dt': status.createdat_dt})
											break
									else:
										self.suspend_security().write({'status': 'Unavailable', 'status_dt': fields.Datetime.now()})
										order_id.write({'activestatustruck': 'Unavailable', 'activestatustruck_dt': fields.Datetime.now()})
						return 'success'
					else:
						return raw_data["message"]
			else:
				return "Konfigurasi API belum di setting, Silahkan Hubungi ICT."
		else:
			return "Police Number Tidak Boleh Kosong"	

	@api.model
	def cron_available_unavailable(self):
		mr_ids = self.env["sisu.tk.mr"].suspend_security().search([("message_api_karlo", "!=", False), ("message_api_karlo", "!=", 'success')], order="id desc")
		for mr_id in mr_ids:
			fleet_id = self.env["sisu.karlo.master.fleet"].suspend_security().search([('policenumber', '=', mr_id.license_plate)], limit=1, order="id desc")
			if fleet_id:
				if mr_id.request_type == 'regular':
					if mr_id.state == 'arrive':
						mr_id.message_api_karlo = fleet_id.update_fleet_available(False)
					elif mr_id.state == 'done':
						mr_id.message_api_karlo = fleet_id.update_fleet_available()		
			
	@api.multi
	def get_geocode_x(self):	
		x = self.get_geocode(-6.9459833, 110.4712766)	
		raise ValidationError(x)

	@api.multi
	def update_fleet_available_manual(self):
		METHOD_POST = 'PUT'

		if self.policenumber and IS_PRODUCTION:
			ROLE = 'trans'
			address = '/{}'.format("available-truck")
			config_api = self.env["sisu.karlo.config.api"].suspend_security().search([('name', '=', 'Karlo'), ('is_active', '=', True)], limit=1, order="id desc")

			param = {
				"policeNumber": self.policenumber,
				"available": True
			}

			if config_api.id:
				result = config_api.karloApiPost(address, ROLE, param, METHOD_POST)
				json_dumps = json.dumps(result)
				raw_data = json.loads(json_dumps)
				# raise ValidationError(raw_data)
				if raw_data:
					if raw_data["statuscode"] == 200:
						raise ValidationError('berhasil')
					else:
						return raw_data["message"]


	@api.multi
	def update_fleet_unavailable_manual(self):
		METHOD_POST = 'PUT'

		if self.policenumber and IS_PRODUCTION:
			ROLE = 'trans'
			address = '/{}'.format("available-truck")
			config_api = self.env["sisu.karlo.config.api"].suspend_security().search([('name', '=', 'Karlo'), ('is_active', '=', True)], limit=1, order="id desc")

			param = {
				"policeNumber": self.policenumber,
				"available": False
			}

			if config_api.id:
				result = config_api.karloApiPost(address, ROLE, param, METHOD_POST)
				json_dumps = json.dumps(result)
				raw_data = json.loads(json_dumps)
				# raise ValidationError(raw_data)
				if raw_data:
					if raw_data["statuscode"] == 200:
						raise ValidationError('berhasil')
					else:
						return raw_data["message"]