from monitor import monitor


class Interest:
    def __init__(self, body_scan):
        self.body_scan = body_scan
        self.interests = []

    def get_interests(self):
        body = self.body_scan
        current_starsystem = body.star_system
        starsystem_bodies = monitor.state['StarSystemBodies']
        parent_body_type = list(body.parents[0].keys())[0] if body.parents else None
        parent_body_id = list(body.parents[0].values())[0] if body.parents else None

        if body.body_type in ('Planet', 'Moon'):
            if body.landable and body.surface_gravity > 2.0:
                self.interests.append('Landable with high gravity')

            if body.landable and body.radius > 18000:
                self.interests.append('Landable large planet')

            if body.landable and body.rings:
                self.interests.append('Ringed landable body')

            if body.landable and body.terraform_state:
                self.interests.append(f'Landable and {body.terraform_state}')

            if body.radius < 300:
                self.interests.append('Small body')

            if body.parents and 'Null' in body.parents[0] and (body.radius / body.semi_major_axis > 0.4):
                binary_body_id = body.parents[0]['Null']
                first_body_id = body.id
                binary_partner = None
                for starsystem, body_ in starsystem_bodies.items():
                    if (starsystem == current_starsystem
                            and body_.id != first_body_id
                            and body_.parents and 'Null' in body_.parents[0]
                            and body_.parents[0]['Null'] == binary_body_id):
                        binary_partner = body_
                        break
                self.interests.append(f'Close binary relative to body size.')

            if body.rotation_period and not body.tidal_lock and abs(body.rotation_period) < 28800:
                self.interests.append('Non-locked body with fast rotation')

            if body.orbital_period and abs(body.orbital_period) < 28800:
                self.interests.append('Fast orbit')

            if body.eccentricity > 0.9:
                self.interests.append('Highly eccentric orbit')

            if body.parents and parent_body_type in ['Planet', 'Star']:
                if (current_starsystem, parent_body_id) in starsystem_bodies:

                    parent_body = starsystem_bodies[(current_starsystem, parent_body_id)]
                    if parent_body.radius * 3 > body.semi_major_axis:
                        self.interests.append('Close orbit relative to parent body size')

                    if parent_body.rings:
                        for ring in parent_body.rings:
                            separation = min(
                                abs(body.semi_major_axis - (ring['OuterRad'] / 1000)),
                                abs((ring['InnerRad'] / 1000) - body.semi_major_axis)
                            )
                            if separation < body.radius * 20:
                                self.interests.append('Close ring proximity')
                            if parent_body.body_type is 'Planet':
                                orbital_inclination_diff = abs(
                                    parent_body.orbital_inclination - body.orbital_inclination
                                )
                                if orbital_inclination_diff > 10 and separation < body.radius * 400:
                                    self.interests.append('Close ring proximity with different orbital inclination')

            if not body.landable and not body.atmosphere_composition:
                self.interests.append('Not landable without atmosphere')

        return self.interests
