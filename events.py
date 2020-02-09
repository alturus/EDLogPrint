import datetime
import math
from math import pi

import colorama

import screenshot
from config import config
from interests import Interest


class ColorMixin:
    def __init__(self):
        colors = config['colors']
        self.k_s = getattr(colorama.Style, colors['key'][1])
        self.k_c = getattr(colorama.Fore, colors['key'][0])
        self.v_s = getattr(colorama.Style, colors['value'][1])
        self.v_c = getattr(colorama.Fore, colors['value'][0])
        # interest color
        self.i_s = getattr(colorama.Style, colors['interest'][1])
        self.i_c = getattr(colorama.Fore, colors['interest'][0])


class Fuel(ColorMixin):
    warning_threshold = 50
    critical_threshold = 30
    warning_color = colorama.Fore.YELLOW
    critical_color = colorama.Fore.RED

    def __init__(self, level=0.0, capacity=0.0):
        super().__init__()
        self.level = level
        self.capacity = capacity

    @property
    def level_percent(self):
        try:
            percent = (self.level / self.capacity) * 100
        except ZeroDivisionError:
            percent = 0

        return percent

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        level_percent = self.level_percent

        if level_percent < self.critical_threshold:
            v_c = self.critical_color
        elif level_percent < self.warning_threshold:
            v_c = self.warning_color

        return f'{k_s}{k_c}Fuel: {v_s}{v_c}{level_percent:.2f}% '


class LoadGame(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.cmdr = entry.get('Commander', 'ERROR')
        self.ship = entry.get('Ship_Localised', 'ERROR')
        self.ship_name = entry.get('ShipName', 'ERROR')
        self.ship_ident = entry.get('ShipIdent', 'ERROR')
        self.fuel_level = entry.get('FuelLevel', 0)
        self.fuel_capacity = entry.get('FuelCapacity', 0)

    @property
    def schema(self):
        schema = (
            f'\t{self.k_s}{self.k_c}CMDR: {self.v_s}{self.v_c}{self.cmdr}\n'
            f'\t{self.k_s}{self.k_c}Ship: {self.v_s}{self.v_c}{self.ship} "{self.ship_name}" {self.ship_ident} '
        )
        schema += f'{Fuel(self.fuel_level, self.fuel_capacity).schema}'

        return schema


class Location(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.star_system = entry.get('StarSystem', 'ERROR')
        self.system_sec = entry.get('SystemSecurity_Localised', 'ERROR')
        self.population = entry.get('Population', 0)
        self.docked = entry.get('Docked', False)
        self.station_type = entry.get('StationType')
        self.station_name = entry.get('StationName')
        self.body_name = entry.get('Body', '-')
        self.body_type = entry.get('BodyType', 'ERROR')

        if self.body_type == 'Null':
            self.body_type = 'In space'

        self.latitude = entry.get('Latitude', None)
        self.longitude = entry.get('Longitude', None)

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}System: {v_s}{v_c}{self.star_system} '
            f'{k_s}{k_c}Sec.: {v_s}{v_c}{self.system_sec} '
            f'{k_s}{k_c}Population: {v_s}{v_c}{self.population:,d}\n'
            f'\t{k_s}{k_c}{self.body_type}: {v_s}{v_c}{self.body_name}'
        )

        if self.docked:
            schema += (
                f'\n\t{k_s}{k_c}Docked at {self.station_type}: {v_s}{v_c}{self.station_name}'
            )

        if self.latitude is not None and self.longitude is not None:
            schema += (
                f'\n\t{k_s}{k_c}Landed in coordinates: {v_s}{v_c}{self.latitude}, {self.longitude}'
            )

        return schema


class FSSDiscoveryScan(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.progress = entry.get('Progress', 0) * 100
        self.body_count = entry.get('BodyCount', 0)
        self.non_body_count = entry.get('NonBodyCount', 0)

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}Progress: {v_s}{v_c}{self.progress:.0f}%\n'
            f'\t{k_s}{k_c}Bodies: {v_s}{v_c}{self.body_count} '
            f'{k_s}{k_c}Non bodies: {v_s}{v_c}{self.non_body_count}'
        )
        return schema


class ApproachBody(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.body_name = entry.get('Body', 'ERROR')
        self.star_system = entry.get('StarSystem', 'ERROR')

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}Planet: {v_s}{v_c}{self.body_name} '
            f'{k_s}{k_c}System: {v_s}{v_c}{self.star_system}'
        )
        return schema


class LeaveBody(ApproachBody):
    pass


class FSSAllBodiesFound(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.system_name = entry.get('SystemName', 'ERROR')
        self.body_count = entry.get('Count', -1)

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}System: {v_s}{v_c}{self.system_name} '
            f'{k_s}{k_c}Bodies: {v_s}{v_c}{self.body_count}'
        )
        return schema


class ScanStar(ColorMixin):
    STAR_DESC = {
        'Main sequance': ('O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'T', 'Y'),
        'Proto star': ('TTS', 'AeBe'),
        'Wolf-Rayet': ('W', 'WN', 'WNC', 'WC', 'WO'),
        'Carbon star': ('CS', 'C', 'CN', 'CJ', 'CH', 'CHd'),
        'White dwarf': ('D', 'DA', 'DAB', 'DAO', 'DAZ', 'DAV', 'DB', 'DBZ', 'DBV', 'DO', 'DOV', 'DQ', 'DC', 'DCV', 'DX'),
        'Neutron': ('N', ),
        'Black hole': ('H', ),
        'Exotic': ('X', ),
    }

    STAR_LUM_DESC = {
        'Super-supergiants': ('0', '0Ia', 'Ia0'),
        'Supergiants': ('Ia', 'Iab', 'Ib'),
        'Bright giants': ('IIa', 'IIab', 'IIb'),
        'Giants': ('IIIa', 'IIIab', 'IIIb'),
        'Subgiants': ('IVa', 'IVab', 'IVb'),
        'Main sequence stars': ('Va', 'Vab', 'Vb'),
        'Subdwarfs': ('VI', ),
        'White dwarf': ('VIII', ),
    }

    def __init__(self, entry, scan_type):
        super().__init__()
        self.id = entry['BodyID']
        self.body_type = 'Star'
        self.parents = entry.get('Parents', [])
        self.scan_type = scan_type
        self.body_name = entry.get('BodyName', 'ERROR')
        self.star_type = entry.get('StarType', 'ERROR')
        self.star_desc = self.get_star_desc(self.star_type)
        self.sub_class = entry.get('Subclass', 'ERROR')
        self.stellar_mass = entry.get('StellarMass', -1)
        self.radius = entry.get('Radius', -1) / 1000
        self.solar_radius = self.radius / 695508
        self.absolute_magnitude = entry.get('AbsoluteMagnitude', -1)
        self.age = entry.get('Age_MY', -1)
        self.surface_temp = entry.get('SurfaceTemperature', -1)
        self.luminosity = entry.get('Luminosity', 'ERROR')
        self.luminosity_desc = self.get_star_lum_desc(self.luminosity)
        self.rings = entry.get('Rings', None)
        self.was_discovered = entry.get('WasDiscovered', None)
        self.was_mapped = entry.get('WasMapped', None)
        self.orbital_period = entry.get('OrbitalPeriod', None)
        if self.orbital_period:
            self.orbital_period = datetime.timedelta(seconds=int(self.orbital_period))

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}{self.body_type}: {v_s}{v_c}{self.body_name} '
            f'{k_s}{k_c}Class: {v_s}{v_c}{self.star_type} ({self.star_desc}) '
            f'{k_s}{k_c}Subclass: {v_s}{v_c}{self.sub_class} ({self.sub_class})\n'
            f'\t{k_s}{k_c}Luminosity: {v_s}{v_c}{self.luminosity} ({self.luminosity_desc})\n'
            f'\t{k_s}{k_c}Solar mass: {v_s}{v_c}{self.stellar_mass:.5f} '
            f'{k_s}{k_c}Solar radius: {v_s}{v_c}{self.solar_radius:.5f}\n'
            f'\t{k_s}{k_c}Surface temp.: {v_s}{v_c}{self.surface_temp:.2f} K\n'
            f'\t{k_s}{k_c}Age: {v_s}{v_c}{self.age} million years\n'
            f'\t{k_s}{k_c}Absolute magnitude: {v_s}{v_c}{self.absolute_magnitude:.3f}'
        )
        if self.orbital_period:
            schema += (
                f'\n\t{k_s}{k_c}Orbital period: {v_s}{v_c}{self.orbital_period}'
            )

        return schema

    @classmethod
    def get_star_desc(cls, star_class):
        description = None
        for desc, sc in cls.STAR_DESC.items():
            if star_class in sc:
                description = desc
                break

        return description

    @classmethod
    def get_star_lum_desc(cls, luminosity):
        description = None
        for desc, sl in cls.STAR_LUM_DESC.items():
            if luminosity in sl:
                description = desc
                break

        return description


class ScanPlanet(ColorMixin):
    def __init__(self, entry, scan_type):
        super().__init__()
        self.id = entry['BodyID']
        self.body_type = 'Planet'
        self.parents = entry.get('Parents', [])
        self.scan_type = scan_type
        self.body_name = entry.get('BodyName', 'ERROR')
        self.planet_class = entry.get('PlanetClass', 'ERROR')
        self.mass = entry.get('MassEM', -1)
        self.radius = entry.get('Radius') / 1000
        self.radius_e = (self.radius / 6371)
        self.surface_gravity = entry.get('SurfaceGravity', -1) / 10

        self.rotation_period = entry.get('RotationPeriod', None)
        self.orbital_period = entry.get('OrbitalPeriod', None)
        self.axial_tilt = entry.get('AxialTilt', None)
        self.semi_major_axis = entry.get('SemiMajorAxis', 0) / 1000
        self.eccentricity = entry.get('Eccentricity', None)

        self.tidal_lock = entry.get('TidalLock', False)
        self.terraform_state = entry.get('TerraformState', None)
        self.atmosphere = entry.get('Atmosphere', 'ERROR').capitalize()
        self.atmosphere_type = entry.get('AtmosphereType', None)
        self.atmosphere_composition = entry.get('AtmosphereComposition', None)
        self.volcanism = entry.get('Volcanism', None)

        self.surface_temperature = entry.get('SurfaceTemperature', 0)
        self.surface_temperature_c = self.surface_temperature - 273.15
        self.surface_pressure = entry.get('SurfacePressure', -1) / 101325
        self.landable = entry.get('Landable', 'N/A')
        self.materials = entry.get('Materials', None)
        self.composition = entry.get('Composition', None)
        self.rings = entry.get('Rings', None)

        self.was_discovered = entry.get('WasDiscovered', None)
        self.was_mapped = entry.get('WasMapped', None)

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}{self.body_type}: {v_s}{v_c}{self.body_name} '
            f'{k_s}{k_c}Landable: {v_s}{v_c}{self.landable}\n'
            f'\t{k_s}{k_c}Class: {v_s}{v_c}{self.planet_class} '
        )

        if self.composition:
            schema += '('
            for i, (element, percent) in enumerate(self.composition.items()):
                percent = percent * 100
                if percent < 0.009:
                    continue
                schema += f'{element}: {percent:.1f}%'
                if i + 1 < len(self.composition):
                    schema += ', '
            schema += ')'

        schema += (
            f'\n\t{k_s}{k_c}Gravity: {v_s}{v_c}{self.surface_gravity:.2f}G '
            f'{k_s}{k_c}EMass: {v_s}{v_c}{self.mass:.4f} '
            f'{k_s}{k_c}Radius: {v_s}{v_c}{self.radius:.2f} km ({self.radius_e:.2f} of Earth)'
        )

        if self.rotation_period and self.axial_tilt:
            rotation_period = datetime.timedelta(seconds=int(self.rotation_period))
            axial_tilt = self.axial_tilt * (180 / pi)
            schema += (
                f'\n\t{k_s}{k_c}Rotation period: {v_s}{v_c}{rotation_period} '
                f'{k_s}{k_c}Axial tilt: {v_s}{v_c}{axial_tilt:.2f} deg. '
                f'{k_s}{k_c}Tidal lock: {v_s}{v_c}{self.tidal_lock}'
            )

        if self.orbital_period:
            orbital_period = datetime.timedelta(seconds=int(self.orbital_period))
            schema += (
                f'\n\t{k_s}{k_c}Orbital period: {v_s}{v_c}{orbital_period}'
            )

        if self.atmosphere or self.atmosphere_composition:
            if self.atmosphere:
                schema += (
                    f'\n\t{k_s}{k_c}Atmosphere: {v_s}{v_c}{self.atmosphere} '
                )

            if self.atmosphere_composition:
                if not self.atmosphere:
                    schema += f'\n\t{k_s}{k_c}Atmosphere composition: {v_s}{v_c}'
                schema += '('
                for i, element in enumerate(self.atmosphere_composition):
                    element_name = element['Name']
                    percent = float(element['Percent'])
                    if percent == 0.0:
                        continue
                    schema += f'{element_name} - {percent:.1f}%'
                    if i + 1 < len(self.atmosphere_composition):
                        schema += ', '
                schema += ')'
        else:
            schema += (
                f'\n\t{k_s}{k_c}No atmosphere'
            )

        if self.volcanism:
            schema += (
                f'\n\t{k_s}{k_c}Volcanism: {v_s}{v_c}{self.volcanism.capitalize()}'
            )
        else:
            schema += (
                f'\n\t{k_s}{k_c}No volcanism'
            )

        if self.surface_temperature or self.surface_pressure:
            surface_temperature = f'{self.surface_temperature:.0f}K ({self.surface_temperature_c:.1f}C)'
            surface_pressure = f'{self.surface_pressure:.2f} atmospheres'
            schema += (
                f'\n\t{k_s}{k_c}Temperature: {v_s}{v_c}{surface_temperature} '
                f'{k_s}{k_c}Pressure: {v_s}{v_c}{surface_pressure}'
            )

        if self.terraform_state:
            schema += (
                f'\n\t{k_s}{k_c}Terraform state: {v_s}{v_c}{self.terraform_state}'
            )

        if self.was_discovered:
            schema += (
                f'\n\t{k_s}{k_c}Discovered'
            )
            if self.was_mapped:
                schema += (
                    f'{k_s}{k_c} and mapped'
                )

        if self.materials:
            schema += (
                f'\n\t{k_s}{k_c}Materials:\n'
            )
            ident = ' ' * 3
            columns = 3
            rows = math.ceil(len(self.materials) / columns)
            for index in range(rows):
                name = self.materials[index]['Name'].capitalize()
                percent = self.materials[index]['Percent']

                schema += (
                    f'\t{ident}{v_s}{v_c}{name:10} -{percent:6.2f}%'
                )

                for column in range(1, columns):
                    try:
                        name = self.materials[index+(column * rows)]['Name'].capitalize()
                        percent = self.materials[index+(column * rows)]['Percent']

                        schema += (
                            f'{ident}{name:10} -{percent:6.2f}%'
                        )
                    except IndexError:
                        pass

                if index + 1 < rows:
                    schema += '\n'

        return schema


class ScanMoon(ScanPlanet):
    def __init__(self, entry, scan_type):
        super().__init__(entry, scan_type)
        self.body_type = 'Moon'


class ScanBeltCluster(ColorMixin):
    def __init__(self, entry, scan_type):
        super().__init__()
        self.id = entry['BodyID']
        self.body_type = 'Belt Cluster'
        self.parents = entry.get('Parents', [])
        self.scan_type = scan_type
        self.body_name = entry.get('BodyName', 'ERROR')
        self.was_discovered = entry.get('WasDiscovered', None)
        self.was_mapped = entry.get('WasMapped', None)

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}Name: {v_s}{v_c}{self.body_name} '
        )
        if self.was_discovered:
            schema += f'{k_s}{k_c}(Discovered)'

        return schema


class ScanRing(ScanBeltCluster):
    pass


class Scan(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.entry = entry
        self.scan_type = entry.get('ScanType', None)
        self.body_scan = self.get_body_scan()
        self.body_name = entry.get('BodyName', 'ERROR')

        self.rings = entry.get('Rings', None)
        self.reserve_level = entry.get('ReserveLevel', None)

    def get_body_scan(self):
        if 'StarType' in self.entry:
            body_scan = ScanStar(self.entry, self.scan_type)
        elif 'Belt Cluster' in self.entry.get('BodyName'):
            body_scan = ScanBeltCluster(self.entry, self.scan_type)
        elif 'Ring' in self.entry.get('BodyName'):
            body_scan = ScanRing(self.entry, self.scan_type)
        elif 'Planet' in self.entry['Parents'][0]:
            body_scan = ScanMoon(self.entry, self.scan_type)
        elif 'MassEM' in self.entry:
            body_scan = ScanPlanet(self.entry, self.scan_type)
        else:
            body_scan = None

        return body_scan

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}Scan type: {v_s}{v_c}{self.scan_type}\n'
        )

        if self.body_scan and self.scan_type in ('AutoScan', 'Detailed'):
            schema += self.body_scan.schema

        if self.rings and isinstance(self.rings, list):
            schema += (
                f'\n\t{k_s}{k_c}Rings ({self.reserve_level}):\n'
            )
            for i, ring in enumerate(self.rings):
                ring_name = ring['Name']
                if ring_name.startswith(self.body_name):
                    ring_name = ring_name.replace(self.body_name, '')
                ring_class = ring['RingClass'].split('_')[-1]
                schema += (
                    f'\t\t{v_s}{v_c}{ring_name} - {ring_class}'
                )
                if i + 1 < len(self.rings):
                    schema += '\n'

        interests = Interest(self.body_scan).get_interests()
        if interests:
            schema += (
                f'\n\t{k_s}{k_c}Interests:'
            )
            for interest in interests:
                schema += (
                    f'\n\t{self.i_s}{self.i_c}{interest}'
                )

        return schema


class Touchdown(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.player_controlled = entry.get('PlayerControlled', None)
        self.latitude = entry.get('Latitude', None)
        self.longitude = entry.get('Longitude', None)

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        if self.player_controlled:
            schema = (
                f'\t{k_s}{k_c}Lat.: {v_s}{v_c}{self.latitude:.4f} '
                f'{k_s}{k_c}Long.: {v_s}{v_c}{self.longitude:.4f}'
            )
        else:
            schema = (
                f'\tAutopilot'
            )

        return schema


class Liftoff(Touchdown):
    pass


class MaterialCollected(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.category = entry.get('Category', 'ERROR')
        self.count = entry.get('Count', -1)
        self.total = entry.get('Total', -1)
        self.operation = 'Collected'
        self.name = entry.get('Name_Localised')
        if not self.name:
            self.name = entry.get('Name', 'ERROR')

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}{self.category}: {v_s}{v_c}{self.name.capitalize()}\n'
            f'\t{k_s}{k_c}{self.operation}: {v_s}{v_c}{self.count} '
            f'{k_s}{k_c}Total: {v_s}{v_c}{self.total}'
        )

        return schema


class MaterialDiscarded(MaterialCollected):
    def __init__(self, entry):
        super().__init__(entry)
        self.operation = 'Discarded'


class StartJump(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.jump_type = entry.get('JumpType', None)
        self.star_system = entry.get('StarSystem', None)
        self.star_class = entry.get('StarClass', None)
        self.star_desc = None
        if self.star_class:
            self.star_desc = ScanStar.get_star_desc(self.star_class)

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        if self.jump_type == 'Hyperspace':
            schema = (
                f'\t{k_s}{k_c}Jump to system: {v_s}{v_c}{self.star_system} '
                f'{k_s}{k_c}Class: {v_s}{v_c}{self.star_class} ({self.star_desc})'
            )
        else:
            schema = None

        return schema


class FSDJump(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.star_system = entry.get('StarSystem', 'ERROR')
        self.jump_dist = entry.get('JumpDist', -1)
        self.system_sec = entry.get('SystemSecurity_Localised', None)
        self.population = entry.get('Population', 0)

        self.fuel_used = entry.get('FuelUsed', 0)
        self.fuel_level = entry.get('FuelLevel', 0)
        self.fuel_capacity = entry.get('FuelCapacity', 0)

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}System: {v_s}{v_c}{self.star_system} '
            f'{k_s}{k_c}Sec.: {v_s}{v_c}{self.system_sec} '
            f'{k_s}{k_c}Population: {v_s}{v_c}{self.population:,d}\n'
            f'\t{k_s}{k_c}Jump distance: {v_s}{v_c}{self.jump_dist:.1f} ly'
        )

        try:
            fuel_used = (float(self.fuel_used) / float(self.fuel_capacity)) * 100
            schema += f'\n\t{k_s}{k_c}Fuel used: {v_s}{v_c}{fuel_used:.1f}% '
            schema += f'{Fuel(self.fuel_level, self.fuel_capacity).schema}'
        except ZeroDivisionError:
            schema += (
                f'\n\t{k_s}{k_c}Fuel: {v_s}{v_c}N/A '
            )

        return schema


class FuelScoop(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.scooped = float(entry.get('Scooped', 0))
        self.fuel_capacity = float(entry.get('FuelCapacity', 0))
        self.total = float(entry.get('Total', 0))

    @property
    def schema(self):
        schema = f'\t{Fuel(self.total, self.fuel_capacity).schema}'
        return schema


class SupercruiseEntry(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.star_system = entry.get('StarSystem', 'ERROR')

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = f'\t{k_s}{k_c}System: {v_s}{v_c}{self.star_system}'

        return schema


class SupercruiseExit(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.body = entry.get('Body', 'ERROR')
        self.body_type = entry.get('BodyType', 'ERROR')
        if self.body_type == 'Null':
            self.body_type = 'In space'

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = f'\t{k_s}{k_c}{self.body_type}: {v_s}{v_c}{self.body}'

        return schema


class DiscoveryScan(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.bodies = entry.get('Bodies', -1)

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = f'\t{k_s}{k_c}New bodies discovered: {v_s}{v_c}{self.bodies} '

        return schema


class Docked(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.station_name = entry.get('StationName', 'ERROR')
        self.station_type = entry.get('StationType', 'ERROR')
        self.station_faction = entry.get('StationFaction', 'ERROR')
        self.faction_state = self.station_faction.get('FactionState', 'None')

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = (
            f'\t{k_s}{k_c}Docked at {self.station_type}: {v_s}{v_c}{self.station_name}\n'
            f'\t{k_s}{k_c}Faction: {v_s}{v_c}{self.station_faction.get("Name")} '
            f'{k_s}{k_c}State: {v_s}{v_c}{self.faction_state}'
        )

        return schema


class ShipyardNew(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.ship_type = entry.get('ShipType_Localised', 'ERROR')

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        schema = f'\t{k_s}{k_c}Ship: {v_s}{v_c}{self.ship_type.title()}'

        return schema


class ShipyardSwap(ShipyardNew):
    pass


class Screenshot(ColorMixin):
    def __init__(self, entry):
        super().__init__()
        self.timestamp = entry['timestamp']
        self.filename = entry['Filename']
        self.width = entry['Width']
        self.height = entry['Height']
        self.star_system = entry['System']
        self.body = entry['Body']
        self.latitude = entry.get('Latitude')
        self.longitude = entry.get('Longitude')
        self.altitude = entry.get('Altitude')
        self.heading = entry.get('Heading')

    @property
    def schema(self):
        k_c, v_c = self.k_c, self.v_c
        k_s, v_s = self.k_s, self.v_s

        new_filename = screenshot.rename(
            self.filename,
            self.body,
            self.timestamp,
            latitude=self.latitude,
            longitude=self.longitude,
        )
        if not new_filename:
            new_filename = f'Unable to rename file: {self.filename}'

        schema = (
            f'\t{k_s}{k_c}Filename: {v_s}{v_c}{new_filename}\n'
            f'\t{k_s}{k_c}Resolution: {v_s}{v_c}{self.width}x{self.height}\n'
            f'\t{k_s}{k_c}Star system: {v_s}{v_c}{self.star_system} '
            f'{k_s}{k_c}Body: {v_s}{v_c}{self.body} '
        )
        if self.latitude and self.longitude:
            schema += (
                f'\n\t{k_s}{k_c}Coordinates: {v_s}{v_c}{self.latitude}, {self.longitude}\n'
                f'\t{k_s}{k_c}Altitude: {v_s}{v_c}{self.altitude}\n'
                f'\t{k_s}{k_c}Heading: {v_s}{v_c}{self.heading}'
            )

        return schema
