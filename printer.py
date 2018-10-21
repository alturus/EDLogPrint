import json
import datetime
from time import sleep
from math import pi
import colorama
import screenshot
from monitor import monitor
from config import config


STAR_DESC = {
    'Main sequance': ('O','B','A','F','G','K','M','L','T','Y'),
    'Proto star': ('TTS', 'AeBe'),
    'Wolf-Rayet': ('W','WN','WNC','WC','WO'),
    'Carbon star': ('CS','C','CN','CJ','CH','CHd'),
    'White dwarf': ('D','DA','DAB','DAO','DAZ','DAV','DB','DBZ','DBV','DO','DOV','DQ','DC','DCV','DX'),
    'Neutron': ('N',),
    'Black hole': ('H',),
    'exotic': ('X',),
}

STAR_LUM_DESC = {
    'Super-supergiants': ('0','0Ia','Ia0'),
    'Supergiants': ('Ia','Iab','Ib'),
    'Bright giants': ('IIa','IIab','IIb'),
    'Giants': ('IIIa','IIIab','IIIb'),
    'Subgiants': ('IVa','IVab','IVb'),
    'Main sequence stars': ('Va','Vab','Vb'),
    'Subdwarfs': ('VI'),
    'White dwarf': ('VIII'),
}


class LogPrinter:

    TRACK_EVENTS = (
        'LoadGame',
        'Location',
        'ApproachBody',
        'LeaveBody',
        'Touchdown',
        'Liftoff',
        'FSDJump',
        'SupercruiseEntry',
        'SupercruiseExit',
        'DiscoveryScan',
        'FuelScoop',
        'Shutdown',
        'LaunchSRV',
        'DockSRV',
        'MaterialCollected',
        'MaterialDiscarded',
        'Docked',
        'Undocked',
        'StartJump',
        'SRVDestroyed',
        'Scan',
        'Screenshot',
        'DockFighter',
        'LaunchFighter',
        'VehicleSwitch',
        'ShipyardSwap',
        'ShipyardNew',
    )

    def __init__(self):
        colorama.init()
        colors = config['colors']
        self.default_color = getattr(colorama.Fore, colors['default'][0])
        self.default_style = getattr(colorama.Style, colors['default'][1])
        self.event_key_style = getattr(colorama.Style, colors['event_key'][1])
        self.event_value_style = getattr(colorama.Style, colors['event_value'][1])
        self.event_key_color = getattr(colorama.Fore, colors['event_key'][0])
        self.event_value_color = getattr(colorama.Fore, colors['event_value'][0])
        self.key_style = getattr(colorama.Style, colors['key'][1])
        self.key_color = getattr(colorama.Fore, colors['key'][0])
        self.value_style = getattr(colorama.Style, colors['value'][1])
        self.value_color = getattr(colorama.Fore, colors['value'][0])
        print(f'{self.default_style}')

    def run(self):
        if monitor.start():
            try:
                while True:
                    entry = monitor.get_entry()
                    if entry:
                        self.print_event(entry)
                        continue
                    sleep(1)
            except KeyboardInterrupt:
                monitor.stop()

    def print_event(self, entry):
        entry = json.loads(entry)
        event = entry['event']

        if event not in self.TRACK_EVENTS:
            return

        timestamp = datetime.datetime.strptime(
            entry['timestamp'],
            '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')

        k_s = self.key_style
        k_c = self.key_color
        v_s = self.value_style
        v_c = self.value_color
        evt_k_s = self.event_key_style
        evt_v_s = self.event_value_style
        evt_k_c = self.event_key_color
        evt_v_c = self.event_value_color

        default_color = self.default_color

        print(f'{evt_k_c}{evt_k_s}{timestamp}: {evt_v_s}{evt_v_c}{event}{default_color}')

        record = ''

        if event == 'LoadGame':
            cmdr = entry['Commander']
            ship = entry['Ship_Localised']
            ship_name = entry['ShipName']
            ship_ident = entry['ShipIdent']
            record = (
                f'\t{k_s}{k_c}CMDR: {v_s}{v_c}{cmdr}\n'
                f'\t{k_s}{k_c}Ship: {v_s}{v_c}{ship} "{ship_name}" {ship_ident} '
            )
            try:
                fuel_capacity = entry['FuelCapacity']
                fuel_level = (entry['FuelLevel'] / fuel_capacity) * 100
                record += self.get_fuel_level(fuel_level)
            except ZeroDivisionError:
                pass

        elif event == 'Location':
            star_system = entry['StarSystem']
            system_sec = entry['SystemSecurity_Localised']
            population = entry['Population']
            docked = entry['Docked']
            station_type = entry.get('StationType')
            station_name = entry.get('StationName')
            body_name = entry['Body']
            body_type = entry['BodyType']
            latitude = entry.get('Latitude')
            longitude = entry.get('Longitude')

            if body_type == 'Null':
                body_type = 'In space'

            record = (
                f'\t{k_s}{k_c}System: {v_s}{v_c}{star_system} '
                f'{k_s}{k_c}Sec.: {v_s}{v_c}{system_sec} '
                f'{k_s}{k_c}Population: {v_s}{v_c}{population:,d}\n'
                f'\t{k_s}{k_c}{body_type}: {v_s}{v_c}{body_name}'
            )

            if docked:
                record += (
                    f'\n\t{k_s}{k_c}Docked at {station_type}: {v_s}{v_c}{station_name}'
                )

            if latitude and longitude:
                record += (
                    f'\n\t{k_s}{k_c}Landed in coordinates: {v_s}{v_c}{latitude}, {longitude}'
                )

        elif event in ['ApproachBody', 'LeaveBody']:
            body_name = entry['Body']
            star_system = entry['StarSystem']

            record = (
                f'\t{k_s}{k_c}Planet: {v_s}{v_c}{body_name} '
                f'{k_s}{k_c}System: {v_s}{v_c}{star_system}'
            )

        elif event in ['Touchdown', 'Liftoff']:
            player_controlled = entry['PlayerControlled']
            if player_controlled:
                latitude = entry['Latitude']
                longitude = entry['Longitude']
                record = (
                    f'\t{k_s}{k_c}Lat.: {v_s}{v_c}{latitude:.4f} '
                    f'{k_s}{k_c}Long.: {v_s}{v_c}{longitude:.4f}'
                )
            else:
                record = (
                    f'\tAutopilot'
                )

        elif event == 'FSDJump':
            star_system = entry['StarSystem']  # name of destination starsystem
            jump_dist = entry['JumpDist']
            system_sec = entry['SystemSecurity_Localised']
            population = entry['Population']

            record = (
                f'\t{k_s}{k_c}System: {v_s}{v_c}{star_system} '
                f'{k_s}{k_c}Sec.: {v_s}{v_c}{system_sec} '
                f'{k_s}{k_c}Population: {v_s}{v_c}{population:,d}\n'
                f'\t{k_s}{k_c}Jump distance: {v_s}{v_c}{jump_dist:.1f} ly'
            )
            try:
                fuel_used = (float(entry['FuelUsed']) / float(entry['FuelCapacity'])) * 100
                fuel_level = (float(entry['FuelLevel']) / float(entry['FuelCapacity'])) * 100
                record += f'\n\t{k_s}{k_c}Fuel used: {v_s}{v_c}{fuel_used:.1f}% '
                record += self.get_fuel_level(fuel_level)
            except ZeroDivisionError:
                record += (
                    f'\n\t{k_s}{k_c}Fuel: {v_s}{v_c}N/A '
                )

        elif event == 'SupercruiseEntry':
            star_system = entry['StarSystem']
            record = (
                f'\t{k_s}{k_c}System: {v_s}{v_c}{star_system}'
            )

        elif event == 'SupercruiseExit':
            body = entry['Body']
            body_type = entry['BodyType']
            if body_type == 'Null':
                body_type = 'In space'
            record = (
                f'\t{k_s}{k_c}{body_type}: {v_s}{v_c}{body}'
            )

        elif event == 'DiscoveryScan':
            bodies = entry['Bodies']
            record += (
                f'\t{k_s}{k_c}New bodies discovered: {v_s}{v_c}{bodies} '
            )

        elif event in ['MaterialCollected', 'MaterialDiscarded']:
            category = entry['Category']
            count = entry['Count']
            total = entry['Total']
            operation = event.replace('Material', '')
            name = entry.get('Name_Localised')
            if not name:
                name = entry['Name']
            record += (
                f'\t{k_s}{k_c}{category}: {v_s}{v_c}{name}\n'
                f'\t{k_s}{k_c}{operation}: {v_s}{v_c}{count} '
                f'{k_s}{k_c}Total: {v_s}{v_c}{total}'
            )

        elif event == 'FuelScoop':
            scooped = float(entry['Scooped'])
            fuel_capacity = monitor.state['FuelCapacity']
            total = float(entry['Total'])
            try:
                fuel_level = (total / fuel_capacity) * 100
                record = '\t' + self.get_fuel_level(fuel_level)
            except ZeroDivisionError:
                pass

        elif event == 'Docked':
            station_name = entry['StationName']
            station_type = entry['StationType']
            station_faction = entry['StationFaction']
            faction_state = entry.get('FactionState')
            record += (
                f'\t{k_s}{k_c}Docked at {station_type}: {v_s}{v_c}{station_name}\n'
                f'\t{k_s}{k_c}Faction: {v_s}{v_c}{station_faction} '
                f'{k_s}{k_c}State: {v_s}{v_c}{faction_state}'
            )

        elif event == 'StartJump':
            jump_type = entry['JumpType']
            if jump_type == 'Hyperspace':
                star_system = entry['StarSystem']
                star_class = entry['StarClass']
                star_desc = self.get_star_desc(star_class)
                record = (
                    f'\t{k_s}{k_c}Jump to system: {v_s}{v_c}{star_system} '
                    f'{k_s}{k_c}Class: {v_s}{v_c}{star_class} ({star_desc})'
                )

        elif event in ['ShipyardNew', 'ShipyardSwap']:
            ship_type = entry.get('ShipType')
            record = (
                f'\t{k_s}{k_c}Ship: {v_s}{v_c}{ship_type.title()}'
            )

        elif event == 'Scan':
            scan_type = entry['ScanType']
            body_name = entry['BodyName']
            body_type = None
            radius = entry['Radius']
            rotation_period = entry.get('RotationPeriod')
            axial_tilt = entry.get('AxialTilt')
            orbital_period = entry.get('OrbitalPeriod')
            if orbital_period:
                orbital_period = datetime.timedelta(seconds=int(orbital_period))

            if 'StarType' in entry:
                body_type = 'Star'
            else:
                if 'Planet' in entry['Parents'][0]:
                    body_type = 'Moon'
                else:
                    body_type = 'Planet'

            if body_type == 'Star':
                star_type = entry['StarType']
                stellar_mass = entry['StellarMass']
                solar_radius = radius / 695508000
                absolute_magnitude = entry['AbsoluteMagnitude']
                surface_temp = entry['SurfaceTemperature']
                luminosity = entry['Luminosity']
                luminosity_desc = self.get_star_lum_desc(luminosity)
                age = entry['Age_MY']
                rings = 'N/A'
                if scan_type == 'Detailed':
                    rings = entry.get('Rings')
                star_desc = self.get_star_desc(star_type)
                record = (
                    f'\t{k_s}{k_c}{body_type}: {v_s}{v_c}{body_name} '
                    f'{k_s}{k_c}Class: {v_s}{v_c}{star_type} ({star_desc})\n'
                    f'\t{k_s}{k_c}Luminosity: {v_s}{v_c}{luminosity} ({luminosity_desc})\n'
                    f'\t{k_s}{k_c}Solar mass: {v_s}{v_c}{stellar_mass:.5f} '
                    f'{k_s}{k_c}Solar radius: {v_s}{v_c}{solar_radius:.5f}\n'
                    f'\t{k_s}{k_c}Surface temp.: {v_s}{v_c}{surface_temp:.2f} K\n'
                    f'\t{k_s}{k_c}Age: {v_s}{v_c}{age} million years\n'
                    f'\t{k_s}{k_c}Absolute magnitude: {v_s}{v_c}{absolute_magnitude:.3f}'
                )
                if orbital_period:
                    record += (
                        f'\n\t{k_s}{k_c}Orbital period: {v_s}{v_c}{orbital_period}'
                    )

            elif body_type in ['Planet', 'Moon']:
                tidal_lock = 'N/A'
                terraform_state = 'N/A'
                planet_class = entry['PlanetClass']
                mass = entry['MassEM']
                radius = radius / 1000
                radius_e = (radius / 6371)
                atmosphere = 'N/A'
                atmosphere_type = None
                atmosphere_composition = None
                volcanism = 'N/A'
                surface_gravity = entry['SurfaceGravity'] / 10
                surface_temp = 'N/A'
                surface_pressure = 'N/A'
                surface_temperature = 'N/A'
                landable = 'N/A'
                materials = None
                composition = None
                rings = 'N/A'
                reserve_level = None

                if scan_type == 'Detailed':
                    tidal_lock = entry.get('TidalLock', False)
                    terraform_state = entry['TerraformState']
                    atmosphere = entry['Atmosphere']
                    atmosphere_type = entry.get('AtmosphereType')
                    atmosphere_composition = entry.get('AtmosphereComposition')
                    composition = entry.get('Composition')
                    volcanism = entry['Volcanism']
                    surface_temperature = entry['SurfaceTemperature']
                    surface_temperature_с = surface_temperature - 273.15
                    surface_pressure = entry['SurfacePressure'] / 101325  # The standard atmosphere is a unit of pressure defined as 101325 Pa
                    landable = entry['Landable']
                    materials = entry.get('Materials')
                    rings = entry.get('Rings')

                record = (
                    f'\t{k_s}{k_c}{body_type}: {v_s}{v_c}{body_name} '
                    f'{k_s}{k_c}Landable: {v_s}{v_c}{landable}\n'
                    f'\t{k_s}{k_c}Class: {v_s}{v_c}{planet_class} '
                )

                if composition:
                    record += '('
                    for i, (element, percent) in enumerate(composition.items()):
                        percent = percent * 100
                        if percent < 0.009:
                            continue
                        record += f'{element}: {percent:.1f}%'
                        if i+1 < len(composition):
                            record += ', '
                    record += ')'

                record += (
                    f'\n\t{k_s}{k_c}Gravity: {v_s}{v_c}{surface_gravity:.2f}G '
                    f'{k_s}{k_c}EMass: {v_s}{v_c}{mass:.4f} '
                    f'{k_s}{k_c}Radius: {v_s}{v_c}{radius:.2f} km ({radius_e:.2f} of Earth)'
                )

                if rotation_period and axial_tilt:
                    rotation_period = datetime.timedelta(seconds=int(rotation_period))
                    axial_tilt = axial_tilt * (180 / pi)
                    record += (
                        f'\n\t{k_s}{k_c}Rotation period: {v_s}{v_c}{rotation_period} '
                        f'{k_s}{k_c}Axial tilt: {v_s}{v_c}{axial_tilt:.2f} deg. '
                        f'{k_s}{k_c}Tidal lock: {v_s}{v_c}{tidal_lock}'
                    )

                record += (
                    f'\n\t{k_s}{k_c}Orbital period: {v_s}{v_c}{orbital_period}'
                )

                if atmosphere or atmosphere_composition:
                    if atmosphere:
                        record += (
                            f'\n\t{k_s}{k_c}Atmosphere: {v_s}{v_c}{atmosphere} '
                        )

                    if atmosphere_composition:
                        if not atmosphere:
                            record += f'\n\t{k_s}{k_c}Atmosphere composition: {v_s}{v_c}'
                        record += '('
                        for i, element in enumerate(atmosphere_composition):
                            element_name = element['Name']
                            percent = float(element['Percent'])
                            if percent == 0.0:
                                continue
                            record += f'{element_name} - {percent:.1f}%'
                            if i+1 < len(atmosphere_composition):
                                record += ', '
                        record += ')'
                else:
                    record += (
                        f'\n\t{k_s}{k_c}No atmosphere'
                    )

                if volcanism:
                    record += (
                        f'\n\t{k_s}{k_c}Volcanism: {v_s}{v_c}{volcanism}'
                    )
                else:
                    record += (
                        f'\n\t{k_s}{k_c}No volcanism'
                    )

                if surface_temperature and surface_pressure:
                    if scan_type == 'Detailed':
                        surface_temperature = f'{surface_temperature:.0f}K ({surface_temperature_с:.1f}C)'
                        surface_pressure = f'{surface_pressure:.2f} atmospheres'
                    record += (
                        f'\n\t{k_s}{k_c}Temperature: {v_s}{v_c}{surface_temperature} '
                        f'{k_s}{k_c}Pressure: {v_s}{v_c}{surface_pressure}'
                    )

                if terraform_state:
                    record += (
                        f'\n\t{k_s}{k_c}Terraform state: {v_s}{v_c}{terraform_state}'
                    )

                if materials:
                    record += (
                        f'\n\t{k_s}{k_c}Materials:\n'
                    )
                    for i, material in enumerate(materials):
                        name = material['Name']
                        percent = material['Percent']
                        record += (
                            f'\t\t{v_s}{v_c}{name} - {percent:.2f}%'
                        )
                        if i+1 < len(materials):
                            record += '\n'

            if isinstance(rings, list):
                reserve_level = entry.get('ReserveLevel')
                record += (
                    f'\n\t{k_s}{k_c}Rings ({reserve_level}):\n'
                )
                for i, ring in enumerate(rings):
                    ring_name = ring['Name']
                    if ring_name.startswith(body_name):
                        ring_name = ring_name.replace(body_name, '')
                    ring_class = ring['RingClass'].split('_')[-1]
                    record += (
                        f'\t\t{v_s}{v_c}{ring_name} - {ring_class}'
                    )
                    if i+1 < len(rings):
                        record += '\n'
            else:
                record += (f'\n\t{k_s}{k_c}Rings: {rings}')

        elif event == 'Screenshot':
            filename = entry['Filename']
            width = entry['Width']
            height = entry['Height']
            star_system = entry['System']
            body = entry['Body']
            latitude = entry.get('Latitude')
            longitude = entry.get('Longitude')
            altitude = entry.get('Altitude')
            heading = entry.get('Heading')
            newfilename = screenshot.rename(filename, body, timestamp, latitude=latitude, longitude=longitude)
            if not newfilename:
                newfilename = f'Unable to rename file: {filename}'
            record = (
                f'\t{k_s}{k_c}Filename: {v_s}{v_c}{newfilename}\n'
                f'\t{k_s}{k_c}Resolution: {v_s}{v_c}{width}x{height}\n'
                f'\t{k_s}{k_c}Star system: {v_s}{v_c}{star_system} '
                f'{k_s}{k_c}Body: {v_s}{v_c}{body} '
            )
            if latitude and longitude:
                record += (
                    f'\n\t{k_s}{k_c}Coordinates: {v_s}{v_c}{latitude}, {longitude}\n'
                    f'\t{k_s}{k_c}Altitude: {v_s}{v_c}{altitude}\n'
                    f'\t{k_s}{k_c}Heading: {v_s}{v_c}{heading}'
                )

        if record:
            print(record)

    def get_fuel_level(self, fuel_level=None):
        if not fuel_level:
            fuel_capacity = monitor.state['FuelCapacity']
            fuel_level = monitor.state['FuelLevel']
            try:
                fuel_level = (fuel_level / fuel_capacity) * 100
            except ZeroDivisionError:
                fuel_level = 0

        k_s = self.key_style
        k_c = self.key_color
        v_s = self.value_style
        v_c = self.value_color

        if fuel_level < 30:
            v_c = colorama.Fore.RED
        elif fuel_level < 50:
            v_c = colorama.Fore.YELLOW

        return f'{k_s}{k_c}Fuel: {v_s}{v_c}{fuel_level:.2f}% '

    @staticmethod
    def get_star_desc(star_class):
        description = None
        for desc, sc in STAR_DESC.items():
            if star_class in sc:
                description = desc
                break

        return description

    @staticmethod
    def get_star_lum_desc(luminosity):
        description = None
        for desc, sl in STAR_LUM_DESC.items():
            if luminosity in sl:
                description = desc
                break

        return description


printer = LogPrinter()
