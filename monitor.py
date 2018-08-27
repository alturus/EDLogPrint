import time
import json
import threading
from os import listdir, SEEK_CUR
from os.path import join, isdir, basename
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import config


class JournalHandler(FileSystemEventHandler):

    def __init__(self):
        self.journal_dir = config['journal_dir']
        self.logfile = None
        self.loghandle = None
        self.observer = None
        self.thread = None
        self.event_queue = []
        self.state = {
            'Commander': None,
            'Ship_Localised': None,
            'ShipName': None,
            'ShipIdent': None,
            'FuelLevel': None,
            'FuelCapacity': None,
            'GameMode': None,
            'Credits': None,

            'Docked': None,
            'StarSystem': None,
            'SystemSecurity_Localised': None,
            'Population': 0,
            'Body': None,
            'BodyType': None,

            'Latitude': None,
            'Longitude': None,

            'StationName': None,
            'StationType': None,

            'Raw': {},
            'Manufactured': {},
            'Encoded': {},
        }

    def start(self):
        if not self.journal_dir or not isdir(self.journal_dir):
            self.stop()
            return False

        try:
            logfiles = sorted(
                [f for f in listdir(self.journal_dir)
                 if f.startswith('Journal') and f.endswith('.log')],
                key=lambda x: x.split('.')[1:]
            )
            if logfiles:
                self.logfile = join(self.journal_dir, logfiles[-1]) or None
        except OSError:
            self.logfile = None
            return False

        self.observer = Observer()
        self.observer.daemon = True
        self.observer.schedule(self, self.journal_dir)
        self.observer.start()

        if not self.running():
            self.thread = threading.Thread(
                target=self.worker,
                name='Journal worker')
            self.thread.daemon = True
            self.thread.start()

        return True

    def stop(self):
        self.thread = None
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

    def running(self):
        return self.thread and self.thread.is_alive()

    def on_created(self, event):
        cond1 = not event.is_directory
        cond2 = basename(event.src_path).startswith('Journal')
        cond3 = basename(event.src_path).endswith('.log')
        if cond1 and cond2 and cond3:
            newlogfile = event.src_path

            if self.loghandle:
                self.loghandle.close()

            self.logfile = newlogfile
            self.loghandle = open(newlogfile, 'r')

            print(self.logfile)

    def worker(self):
        if not self.logfile:
            return
        self.loghandle = open(join(self.journal_dir, self.logfile), 'r')

        while True:
            loghandle = self.loghandle
            if loghandle:
                loghandle.seek(0, SEEK_CUR)
                for line in loghandle:
                    self.parse(line)

            time.sleep(1)

            if threading.current_thread() != self.thread:
                return

    def parse(self, line):
        entry = json.loads(line)
        event = entry['event']

        if event == 'Commander':
            self.state['Commander'] = entry['Name']

        elif event == 'NewCommander':
            self.state['Commander'] = entry['Name']

        elif event in ['LoadGame', 'Location']:
            for k, v in entry.items():
                if k in self.state:
                    self.state[k] = v

        elif (event == 'Loadout' and
              not entry['Ship'].lower().endswith('fighter')):
            self.state['ShipName'] = entry['ShipName']
            self.state['ShipIdent'] = entry['ShipIdent']
            fuel_capacity = 0
            for module in entry['Modules']:
                if module['Item'].lower().find('fueltank') > -1:
                    item = module['Item'].split('_')
                    size = int(item[2][-1])
                    fuel_capacity += 2 ** size
            self.state['FuelCapacity'] = fuel_capacity

        elif event == 'Docked':
            self.state['Docked'] = True
            self.state['StationName'] = entry['StationName']
            self.state['StationType'] = entry['StationType']

        elif event == 'Undocked':
            self.state['Docked'] = False
            self.state['StationName'] = None
            self.state['StationType'] = None

        elif event == 'FSDJump':
            self.state['BodyType'] = 'Star'
            for k, v in entry.items():
                if k in self.state:
                    self.state[k] = v
            entry.update({'FuelCapacity': self.state['FuelCapacity']})
            line = json.dumps(entry, separators=(', ', ':'))

        elif event == 'Materials':
            for category in ['Raw', 'Manufactured', 'Encoded']:
                for material in entry.get(category, []):
                    count = material['Count']
                    name = material.get('Name_Localised')
                    if not name:
                        name = material['Name']
                    self.state[category].update({name: count})

        elif event in ['MaterialCollected', 'MaterialDiscarded']:
            category = entry['Category']
            count = entry['Count']
            name = entry.get('Name_Localised')
            if not name:
                name = entry['Name']

            if event == 'MaterialCollected':
                total = self.state[category][name] + count
            elif event == 'MaterialDiscarded':
                total = self.state[category][name] - count

            self.state[category].update({name: total})
            
            entry.update({'Total': total})
            line = json.dumps(entry, separators=(', ', ':'))

        elif event == 'ApproachBody':
            self.state['BodyType'] = 'Planet'
            for k, v in entry.items():
                if k in self.state:
                    self.state[k] = v

        elif event == 'LeaveBody':
            self.state['BodyType'] = 'Null'
            for k, v in entry.items():
                if k in self.state:
                    self.state[k] = v

        elif event == 'Touchdown':
            self.state['Latitude'] = entry.get('Latitude')
            self.state['Longitude'] = entry.get('Longitude')

        elif event == 'Liftoff':
            self.state['Latitude'] = None
            self.state['Longitude'] = None

        elif event == 'SupercruiseEntry':
            self.state['BodyType'] = 'Null'

        elif event == 'SupercruiseExit':
            for k, v in entry.items():
                if k in self.state:
                    self.state[k] = v

        elif event == 'FuelScoop':
            self.state['FuelLevel'] = entry['Total']

        elif event in ['RefuelAll', 'RefuelPartial']:
            self.state['FuelLevel'] += entry['Amount']

        elif event == 'SetUserShipName':
            self.state['ShipName'] = entry['UserShipName']
            self.state['ShipIdent'] = entry['UserShipId']

        elif event in ['ShipyardNew', 'ShipyardSwap']:
            self.state['Ship_Localised'] = entry['ShipType_Localised']
            self.state['ShipName'] = None
            self.state['ShipIdent'] = None

        self.event_queue.append(line)

    def get_entry(self):
        if not self.event_queue:
            return None

        entry = self.event_queue.pop(0)

        return entry


monitor = JournalHandler()
