import datetime
import json
from time import sleep

import colorama

import events
from config import config
from monitor import monitor


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
        'FSSDiscoveryScan',
        'FSSAllBodiesFound',
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

        entry['timestamp'] = timestamp

        evt_k_s = self.event_key_style
        evt_v_s = self.event_value_style
        evt_k_c = self.event_key_color
        evt_v_c = self.event_value_color

        default_color = self.default_color

        print(f'{evt_k_c}{evt_k_s}{timestamp}: {evt_v_s}{evt_v_c}{event}{default_color}')

        record = ''

        if event == 'LoadGame':
            record = events.LoadGame(entry).schema

        elif event == 'FSSDiscoveryScan':
            record = events.FSSDiscoveryScan(entry).schema

        elif event == 'FSSAllBodiesFound':
            record = events.FSSAllBodiesFound(entry).schema

        elif event == 'Scan':
            record = events.Scan(entry).schema

        elif event == 'Screenshot':
            screenshot_event = events.Screenshot(entry)
            is_renamed = screenshot_event.rename()
            if is_renamed and config.get('convert_screenshots', False):
                screenshot_event.convert_to_png()
            record = screenshot_event.schema

        elif event == 'Location':
            record = events.Location(entry).schema

        elif event == 'ApproachBody':
            record = events.ApproachBody(entry).schema

        elif event == 'LeaveBody':
            record = events.LeaveBody(entry).schema

        elif event == 'Touchdown':
            record = events.Touchdown(entry).schema

        elif event == 'Liftoff':
            record = events.Liftoff(entry).schema

        elif event == 'FSDJump':
            record = events.FSDJump(entry).schema

        elif event == 'SupercruiseEntry':
            record = events.SupercruiseEntry(entry).schema

        elif event == 'SupercruiseExit':
            record = events.SupercruiseExit(entry).schema

        elif event == 'DiscoveryScan':
            record = events.DiscoveryScan(entry).schema

        elif event == 'MaterialCollected':
            record = events.MaterialCollected(entry).schema

        elif event == 'MaterialDiscarded':
            record = events.MaterialDiscarded(entry).schema

        elif event == 'FuelScoop':
            entry['FuelCapacity'] = monitor.state['FuelCapacity']
            record = events.FuelScoop(entry).schema

        elif event == 'Docked':
            record = events.Docked(entry).schema

        elif event == 'StartJump':
            record = events.StartJump(entry).schema

        elif event == 'ShipyardNew':
            record = events.ShipyardNew(entry).schema

        elif event == 'ShipyardSwap':
            record = events.ShipyardSwap(entry).schema

        if record:
            print(record)


printer = LogPrinter()
