import flet as ft
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import getpass

# Папка, где хранятся отметки и отчёт о работе.
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
STATE_FILE = DATA_DIR / "checklist_state.txt"
REPORT_FILE = DATA_DIR / "session_report.txt"
TIME_FORMAT = "%d.%m.%Y %H:%M:%S"



# Общий класс для объектов программы.
class Entity(ABC):

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r})"

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash((type(self).__name__, self.name))



# Коллекция объектов. Она нужна вместо обычного словаря.
class EntityCollection:

    def __init__(self, items = ()):
        self._items = list(items)

    @property
    def items(self):
        return tuple(self._items)

    def add(self, item):
        self._items.append(item)

    def find_by_name(self, name):
        for item in self._items:
            if item.name == name:
                return item
        return None

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)



class Manufacturer(Entity):
    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = value.strip()
        if not value:
            raise ValueError("Название производителя не может быть пустым")
        self._name = value


class Aircraft(Entity):
    def __init__(self, manufacturer, model, engine):
        self.manufacturer = manufacturer
        self.model = model
        self.engine = engine

    @property
    def name(self):
        return self._model

    @property
    def manufacturer(self):
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        if not isinstance(value, Manufacturer):
            raise TypeError("manufacturer должен быть объектом Manufacturer")
        self._manufacturer = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        value = value.strip()
        if not value:
            raise ValueError("Модель не может быть пустой")
        self._model = value

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        value = value.strip()
        if not value:
            raise ValueError("Название двигателя не может быть пустым")
        self._engine = value

    def __repr__(self):
        return f"Aircraft(manufacturer={self.manufacturer.name!r}, model={self.model!r})"

    def __str__(self):
        return f"{self.manufacturer.name} {self.model}"


class ChecklistItem(Entity):
    def __init__(self, title, action, description):
        self.title = title
        self.action = action
        self.description = description

    @property
    def name(self):
        return self._title

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        value = value.strip()
        if not value:
            raise ValueError("Название пункта не может быть пустым")
        self._title = value

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value.strip()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value.strip()

    def __repr__(self):
        return f"ChecklistItem(title={self.title!r}, action={self.action!r})"

    def __str__(self):
        return f"{self.title} — {self.action}"


class ChecklistStage(Entity):
    def __init__(self, name, items):
        self.name = name
        self.items = items

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = value.strip()
        if not value:
            raise ValueError("Название этапа не может быть пустым")
        self._name = value

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        self._items = tuple(value)

    def __repr__(self):
        return f"ChecklistStage(name={self.name!r}, items={len(self.items)})"

    def __str__(self):
        return f"{self.name} ({len(self.items)} пунктов)"


class AircraftChecklist(Entity):
    def __init__(self, aircraft, stages):
        self.aircraft = aircraft
        self.stages = stages

    @property
    def name(self):
        return self.aircraft.model

    @property
    def aircraft(self):
        return self._aircraft

    @aircraft.setter
    def aircraft(self, value):
        if not isinstance(value, Aircraft):
            raise TypeError("aircraft должен быть объектом Aircraft")
        self._aircraft = value

    @property
    def stages(self):
        return self._stages

    @stages.setter
    def stages(self, value):
        self._stages = tuple(value)

    def __repr__(self):
        return f"AircraftChecklist(model={self.name!r}, stages={len(self.stages)})"

    def __str__(self):
        return f"Чек-лист {self.name}"


class AppText(ft.Text):
    def __init__(self, value, size = 14, color = "#E7EEF5", **kwargs):
        super().__init__(value=value, size=size, color=color, **kwargs)


class PageHeading(ft.Text):
    def __init__(self, value):
        super().__init__(value=value, size=28, weight=ft.FontWeight.BOLD, color="#F4F7FB")


class MutedText(ft.Text):
    def __init__(self, value, size = 12):
        super().__init__(value=value, size=size, color="#9EADBD")


class ActionButton(ft.Button):
    def __init__(self, label, on_click, icon=None):
        super().__init__(content=ft.Text(label), on_click=on_click, icon=icon)


class BackActionButton(ft.IconButton):
    def __init__(self, on_click):
        super().__init__(icon=ft.Icons.ARROW_BACK, tooltip="Назад", on_click=on_click)


class PanelCard(ft.Card):
    def __init__(self, content, **kwargs):
        super().__init__(content=content, **kwargs)


class AircraftTile(ft.Container):
    def __init__(self, content, on_click, **kwargs):
        super().__init__(content=content, on_click=on_click, padding=18, border_radius=14,
                         bgcolor="#1A2937", border=ft.border.all(1, "#2D4356"), **kwargs)


class ChecklistTile(ft.Container):
    def __init__(self, content, **kwargs):
        super().__init__(content=content, padding=12, border_radius=10,
                         bgcolor="#172532", **kwargs)


class ProgressPanel(ft.Container):
    def __init__(self, content):
        super().__init__(content=content, padding=16, border_radius=12, bgcolor="#1A2937")


class StageSeparator(ft.Divider):
    def __init__(self):
        super().__init__(height=1, color="#2D4356", thickness=1)


class InfoPanel(ft.Container):
    def __init__(self, content):
        super().__init__(content=content, padding=16, border_radius=12, bgcolor="#203444")


class AppIcon(ft.Icon):
    def __init__(self, name, size = 22, color = "#64D6C4"):
        super().__init__(name=name, size=size, color=color)



MANUFACTURERS = EntityCollection()
AIRCRAFTS = EntityCollection()
CHECKLISTS = EntityCollection()


def register_aircraft(manufacturer_name, model, engine):
    manufacturer = MANUFACTURERS.find_by_name(manufacturer_name)
    if manufacturer is None:
        manufacturer = Manufacturer(manufacturer_name)
        MANUFACTURERS.add(manufacturer)
    aircraft = Aircraft(manufacturer, model, engine)
    AIRCRAFTS.add(aircraft)
    return aircraft


def register_checklist(aircraft, stages):
    CHECKLISTS.add(AircraftChecklist(aircraft, stages))


register_aircraft('Airbus', 'A320neo', 'LEAP-1A')
register_aircraft('Airbus', 'A350-900', 'Trent XWB')
register_aircraft('Airbus', 'A380-800', 'Trent 900')
register_aircraft('Boeing', '737-800', 'CFM56-7B')
register_aircraft('Boeing', '737 MAX 8', 'LEAP-1B')
register_aircraft('Boeing', '777-300ER', 'GE90')
register_aircraft('Cessna', 'C172 Skyhawk', 'Lycoming IO-360')
register_aircraft('ATR', 'ATR 72-600', 'PW127M')
register_aircraft('Embraer', 'E190-E2', 'PW1900G')

_aircraft = AIRCRAFTS.find_by_name('A320neo')
if not isinstance(_aircraft, Aircraft):
    raise RuntimeError('Не найдена модель A320neo')
_stages = (
    ChecklistStage('COCKPIT PREPARATION', (
        ChecklistItem('BATTERY', 'ON', 'Aircraft electrical power'),
        ChecklistItem('EXT PWR', 'ON', 'External power'),
        ChecklistItem('APU', 'START / ON', 'Auxiliary Power Unit (ВСУ)'),
        ChecklistItem('ADIRS', 'ALIGN', 'Air Data Inertial Reference System'),
        ChecklistItem('OXYGEN', 'CHECK', 'Crew oxygen system'),
        ChecklistItem('FIRE TEST', 'TEST', 'Fire detection system'),
        ChecklistItem('FUEL', 'CHECK', 'Fuel quantity and pumps'),
        ChecklistItem('HYDRAULICS', 'CHECK', 'Hydraulic system'),
        ChecklistItem('MCDU', 'SET', 'Flight management system'),
    )),
    ChecklistStage('BEFORE START', (
        ChecklistItem('DOORS', 'CLOSED', 'Aircraft doors'),
        ChecklistItem('BEACON', 'ON', 'Anti-collision light'),
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('PUSHBACK', 'CLEAR', 'Pushback clearance'),
    )),
    ChecklistStage('ENGINE START', (
        ChecklistItem('ENGINE 2', 'START', 'Engine start sequence'),
        ChecklistItem('ENGINE 1', 'START', 'Engine start sequence'),
        ChecklistItem('OIL PRESSURE', 'CHECK', 'Engine oil pressure'),
        ChecklistItem('EGT', 'MONITOR', 'Exhaust gas temperature'),
        ChecklistItem('GENERATORS', 'ON', 'Electrical generators'),
    )),
    ChecklistStage('AFTER START', (
        ChecklistItem('PACKS', 'ON', 'Air conditioning packs'),
        ChecklistItem('BLEED AIR', 'SET', 'Pneumatic system'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Engine anti-ice'),
        ChecklistItem('FLIGHT CONTROLS', 'CHECK', 'Flight controls'),
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
    )),
    ChecklistStage('TAXI', (
        ChecklistItem('BRAKES', 'CHECK', 'Brake system'),
        ChecklistItem('FLIGHT INSTRUMENTS', 'CHECK', 'Flight instruments'),
        ChecklistItem('TAKEOFF BRIEFING', 'COMPLETE', 'Crew briefing'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Exterior lights'),
    )),
    ChecklistStage('BEFORE TAKEOFF', (
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
        ChecklistItem('SPOILERS', 'ARM', 'Automatic spoiler system'),
        ChecklistItem('AUTOTHRUST', 'ARM', 'Automatic thrust system'),
        ChecklistItem('TCAS', 'TA/RA', 'Traffic collision avoidance'),
        ChecklistItem('CABIN', 'READY', 'Cabin ready'),
    )),
    ChecklistStage('AFTER TAKEOFF', (
        ChecklistItem('GEAR', 'UP', 'Landing gear'),
        ChecklistItem('FLAPS', 'RETRACT', 'Flap retraction'),
        ChecklistItem('CLIMB POWER', 'SET', 'Engine thrust'),
    )),
    ChecklistStage('CLIMB', (
        ChecklistItem('ENGINE PARAMETERS', 'MONITOR', 'Engine monitoring'),
        ChecklistItem('PRESSURIZATION', 'CHECK', 'Cabin pressure'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Ice protection'),
    )),
    ChecklistStage('CRUISE', (
        ChecklistItem('FUEL', 'MONITOR', 'Fuel monitoring'),
        ChecklistItem('SYSTEMS', 'CHECK', 'Aircraft systems'),
        ChecklistItem('WEATHER RADAR', 'SET', 'Weather radar'),
    )),
    ChecklistStage('DESCENT', (
        ChecklistItem('DESCENT BRIEFING', 'COMPLETE', 'Approach briefing'),
        ChecklistItem('LANDING DATA', 'SET', 'Landing performance'),
        ChecklistItem('AUTOBRAKE', 'SET', 'Automatic braking'),
    )),
    ChecklistStage('APPROACH', (
        ChecklistItem('LANDING GEAR', 'DOWN', 'Landing gear'),
        ChecklistItem('FLAPS', 'SET', 'Landing configuration'),
        ChecklistItem('LANDING LIGHTS', 'ON', 'Landing lights'),
        ChecklistItem('CABIN', 'READY', 'Cabin preparation'),
    )),
    ChecklistStage('LANDING', (
        ChecklistItem('REVERSE THRUST', 'AS REQUIRED', 'Reverse thrust'),
        ChecklistItem('BRAKES', 'APPLY', 'Wheel brakes'),
        ChecklistItem('SPOILERS', 'CHECK', 'Ground spoilers'),
    )),
    ChecklistStage('AFTER LANDING', (
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('SPOILERS', 'DISARM', 'Spoilers'),
        ChecklistItem('APU', 'START', 'Auxiliary Power Unit'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Taxi lights'),
    )),
    ChecklistStage('PARKING / SHUTDOWN', (
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('ENGINES', 'OFF', 'Engine shutdown'),
        ChecklistItem('FUEL PUMPS', 'OFF', 'Fuel system'),
        ChecklistItem('BEACON', 'OFF', 'Anti-collision light'),
        ChecklistItem('BATTERY', 'OFF', 'Electrical system'),
    )),
)
register_checklist(_aircraft, _stages)

_aircraft = AIRCRAFTS.find_by_name('A350-900')
if not isinstance(_aircraft, Aircraft):
    raise RuntimeError('Не найдена модель A350-900')
_stages = (
    ChecklistStage('COCKPIT PREPARATION', (
        ChecklistItem('BATTERY', 'ON', 'Aircraft electrical power'),
        ChecklistItem('EXT PWR', 'ON', 'External power'),
        ChecklistItem('APU', 'START / ON', 'Auxiliary Power Unit (ВСУ)'),
        ChecklistItem('ADIRS', 'ALIGN', 'Air Data Inertial Reference System'),
        ChecklistItem('FMS', 'SET', 'Flight management system'),
        ChecklistItem('FUEL', 'CHECK', 'Fuel system'),
        ChecklistItem('HYDRAULICS', 'CHECK', 'Hydraulic system'),
    )),
    ChecklistStage('BEFORE START', (
        ChecklistItem('DOORS', 'CLOSED', 'Aircraft doors'),
        ChecklistItem('BEACON', 'ON', 'Anti-collision light'),
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('PUSHBACK', 'CLEAR', 'Pushback clearance'),
    )),
    ChecklistStage('ENGINE START', (
        ChecklistItem('ENGINE 1', 'START', 'Trent XWB engine start'),
        ChecklistItem('ENGINE 2', 'START', 'Trent XWB engine start'),
        ChecklistItem('ENGINE PARAMETERS', 'CHECK', 'Engine indications'),
        ChecklistItem('GENERATORS', 'ON', 'Electrical generators'),
    )),
    ChecklistStage('AFTER START', (
        ChecklistItem('PACKS', 'ON', 'Air conditioning'),
        ChecklistItem('BLEED AIR', 'SET', 'Pneumatic system'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Engine anti-ice'),
        ChecklistItem('FLIGHT CONTROLS', 'CHECK', 'Flight controls'),
    )),
    ChecklistStage('TAXI', (
        ChecklistItem('BRAKES', 'CHECK', 'Brake system'),
        ChecklistItem('TAKEOFF BRIEFING', 'COMPLETE', 'Crew briefing'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Exterior lights'),
    )),
    ChecklistStage('BEFORE TAKEOFF', (
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
        ChecklistItem('SPOILERS', 'ARM', 'Ground spoilers'),
        ChecklistItem('AUTOTHROTTLE', 'ARM', 'Automatic thrust'),
        ChecklistItem('TCAS', 'TA/RA', 'Collision avoidance'),
        ChecklistItem('CABIN', 'READY', 'Cabin ready'),
    )),
    ChecklistStage('AFTER TAKEOFF', (
        ChecklistItem('GEAR', 'UP', 'Landing gear'),
        ChecklistItem('FLAPS', 'RETRACT', 'Flap retraction'),
        ChecklistItem('CLIMB POWER', 'SET', 'Engine thrust'),
    )),
    ChecklistStage('CLIMB', (
        ChecklistItem('ENGINE PARAMETERS', 'MONITOR', 'Engine monitoring'),
        ChecklistItem('PRESSURIZATION', 'CHECK', 'Cabin pressure'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Ice protection'),
    )),
    ChecklistStage('CRUISE', (
        ChecklistItem('FUEL', 'MONITOR', 'Fuel monitoring'),
        ChecklistItem('SYSTEMS', 'CHECK', 'Aircraft systems'),
        ChecklistItem('WEATHER RADAR', 'SET', 'Weather radar'),
    )),
    ChecklistStage('DESCENT', (
        ChecklistItem('DESCENT BRIEFING', 'COMPLETE', 'Approach briefing'),
        ChecklistItem('LANDING DATA', 'SET', 'Landing performance'),
        ChecklistItem('AUTOBRAKE', 'SET', 'Automatic braking'),
    )),
    ChecklistStage('APPROACH', (
        ChecklistItem('LANDING GEAR', 'DOWN', 'Landing gear'),
        ChecklistItem('FLAPS', 'SET', 'Landing configuration'),
        ChecklistItem('LANDING LIGHTS', 'ON', 'Landing lights'),
        ChecklistItem('CABIN', 'READY', 'Cabin preparation'),
    )),
    ChecklistStage('LANDING', (
        ChecklistItem('REVERSE THRUST', 'AS REQUIRED', 'Reverse thrust'),
        ChecklistItem('BRAKES', 'APPLY', 'Wheel brakes'),
        ChecklistItem('SPOILERS', 'CHECK', 'Ground spoilers'),
    )),
    ChecklistStage('AFTER LANDING', (
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('SPOILERS', 'DISARM', 'Spoilers'),
        ChecklistItem('APU', 'START', 'Auxiliary Power Unit'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Taxi lights'),
    )),
    ChecklistStage('PARKING / SHUTDOWN', (
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('ENGINES', 'OFF', 'Engine shutdown'),
        ChecklistItem('FUEL PUMPS', 'OFF', 'Fuel system'),
        ChecklistItem('BEACON', 'OFF', 'Anti-collision light'),
        ChecklistItem('BATTERY', 'OFF', 'Electrical system'),
    )),
)
register_checklist(_aircraft, _stages)

_aircraft = AIRCRAFTS.find_by_name('A380-800')
if not isinstance(_aircraft, Aircraft):
    raise RuntimeError('Не найдена модель A380-800')
_stages = (
    ChecklistStage('COCKPIT PREPARATION', (
        ChecklistItem('BATTERY', 'ON', 'Aircraft electrical power'),
        ChecklistItem('EXT PWR', 'ON', 'External power'),
        ChecklistItem('APU', 'START / ON', 'Auxiliary Power Unit (ВСУ)'),
        ChecklistItem('ADIRS', 'ALIGN', 'Air Data Inertial Reference System'),
        ChecklistItem('FMS', 'SET', 'Flight management system'),
        ChecklistItem('FUEL', 'CHECK', 'Fuel system'),
        ChecklistItem('HYDRAULICS', 'CHECK', 'Hydraulic system'),
    )),
    ChecklistStage('BEFORE START', (
        ChecklistItem('DOORS', 'CLOSED', 'Aircraft doors'),
        ChecklistItem('BEACON', 'ON', 'Anti-collision light'),
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('PUSHBACK', 'CLEAR', 'Pushback clearance'),
    )),
    ChecklistStage('ENGINE START', (
        ChecklistItem('ENGINE 1', 'START', 'Engine start sequence'),
        ChecklistItem('ENGINE 2', 'START', 'Engine start sequence'),
        ChecklistItem('ENGINE 3', 'START', 'Engine start sequence'),
        ChecklistItem('ENGINE 4', 'START', 'Engine start sequence'),
        ChecklistItem('GENERATORS', 'ON', 'Electrical generators'),
    )),
    ChecklistStage('AFTER START', (
        ChecklistItem('PACKS', 'ON', 'Air conditioning'),
        ChecklistItem('BLEED AIR', 'SET', 'Pneumatic system'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Engine anti-ice'),
        ChecklistItem('FLIGHT CONTROLS', 'CHECK', 'Flight controls'),
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
    )),
    ChecklistStage('TAXI', (
        ChecklistItem('BRAKES', 'CHECK', 'Brake system'),
        ChecklistItem('TAKEOFF BRIEFING', 'COMPLETE', 'Crew briefing'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Exterior lights'),
    )),
    ChecklistStage('BEFORE TAKEOFF', (
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
        ChecklistItem('SPOILERS', 'ARM', 'Ground spoilers'),
        ChecklistItem('AUTOTHRUST', 'ARM', 'Automatic thrust'),
        ChecklistItem('TCAS', 'TA/RA', 'Collision avoidance'),
        ChecklistItem('CABIN', 'READY', 'Cabin ready'),
    )),
    ChecklistStage('AFTER TAKEOFF', (
        ChecklistItem('GEAR', 'UP', 'Landing gear'),
        ChecklistItem('FLAPS', 'RETRACT', 'Flap retraction'),
    )),
    ChecklistStage('CLIMB', (
        ChecklistItem('ENGINE PARAMETERS', 'MONITOR', 'Engine monitoring'),
        ChecklistItem('PRESSURIZATION', 'CHECK', 'Cabin pressure'),
    )),
    ChecklistStage('CRUISE', (
        ChecklistItem('FUEL', 'MONITOR', 'Fuel monitoring'),
        ChecklistItem('SYSTEMS', 'CHECK', 'Aircraft systems'),
    )),
    ChecklistStage('DESCENT', (
        ChecklistItem('LANDING DATA', 'SET', 'Landing performance'),
        ChecklistItem('AUTOBRAKE', 'SET', 'Automatic braking'),
    )),
    ChecklistStage('APPROACH', (
        ChecklistItem('GEAR', 'DOWN', 'Landing gear'),
        ChecklistItem('FLAPS', 'SET', 'Landing configuration'),
        ChecklistItem('CABIN', 'READY', 'Cabin ready'),
    )),
    ChecklistStage('LANDING', (
        ChecklistItem('REVERSE THRUST', 'AS REQUIRED', 'Reverse thrust'),
        ChecklistItem('BRAKES', 'APPLY', 'Wheel brakes'),
    )),
    ChecklistStage('AFTER LANDING', (
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('SPOILERS', 'DISARM', 'Spoilers'),
        ChecklistItem('APU', 'START', 'Auxiliary Power Unit'),
    )),
    ChecklistStage('PARKING / SHUTDOWN', (
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('ENGINES', 'OFF', 'Engine shutdown'),
        ChecklistItem('BATTERY', 'OFF', 'Electrical system'),
    )),
)
register_checklist(_aircraft, _stages)

_aircraft = AIRCRAFTS.find_by_name('737 MAX 8')
if not isinstance(_aircraft, Aircraft):
    raise RuntimeError('Не найдена модель 737 MAX 8')
_stages = (
    ChecklistStage('COCKPIT PREPARATION', (
        ChecklistItem('BATTERY', 'ON', 'Aircraft electrical system'),
        ChecklistItem('GROUND POWER', 'ON', 'External electrical power'),
        ChecklistItem('APU', 'START / ON', 'Auxiliary Power Unit (ВСУ)'),
        ChecklistItem('IRS', 'ALIGN', 'Inertial Reference System'),
        ChecklistItem('FMC', 'SET', 'Flight Management Computer'),
        ChecklistItem('FUEL', 'CHECK', 'Fuel quantity'),
        ChecklistItem('HYDRAULICS', 'CHECK', 'Hydraulic system'),
    )),
    ChecklistStage('BEFORE START', (
        ChecklistItem('DOORS', 'CLOSED', 'Aircraft doors'),
        ChecklistItem('BEACON', 'ON', 'Anti-collision light'),
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('PUSHBACK', 'CLEAR', 'Pushback clearance'),
    )),
    ChecklistStage('ENGINE START', (
        ChecklistItem('ENGINE 2', 'START', 'LEAP-1B engine start'),
        ChecklistItem('ENGINE 1', 'START', 'LEAP-1B engine start'),
        ChecklistItem('N1/N2', 'CHECK', 'Engine rotation'),
        ChecklistItem('EGT', 'MONITOR', 'Exhaust temperature'),
        ChecklistItem('GENERATORS', 'ON', 'Electrical generators'),
    )),
    ChecklistStage('AFTER START', (
        ChecklistItem('PACKS', 'ON', 'Air conditioning'),
        ChecklistItem('BLEEDS', 'ON', 'Pneumatic system'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Engine anti-ice'),
        ChecklistItem('FLIGHT CONTROLS', 'CHECK', 'Flight controls'),
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
    )),
    ChecklistStage('TAXI', (
        ChecklistItem('BRAKES', 'CHECK', 'Brake system'),
        ChecklistItem('TAKEOFF BRIEFING', 'COMPLETE', 'Crew briefing'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Exterior lights'),
    )),
    ChecklistStage('BEFORE TAKEOFF', (
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
        ChecklistItem('SPEED BRAKE', 'ARM', 'Speed brake'),
        ChecklistItem('AUTOTHROTTLE', 'ARM', 'Automatic thrust'),
        ChecklistItem('TCAS', 'TA/RA', 'Traffic avoidance'),
        ChecklistItem('CABIN', 'READY', 'Cabin ready'),
    )),
    ChecklistStage('AFTER TAKEOFF', (
        ChecklistItem('GEAR', 'UP', 'Landing gear'),
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('CLIMB POWER', 'SET', 'Engine thrust'),
    )),
    ChecklistStage('CLIMB', (
        ChecklistItem('ENGINE PARAMETERS', 'MONITOR', 'Engine monitoring'),
        ChecklistItem('PRESSURIZATION', 'CHECK', 'Cabin pressure'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Ice protection'),
    )),
    ChecklistStage('CRUISE', (
        ChecklistItem('FUEL', 'MONITOR', 'Fuel monitoring'),
        ChecklistItem('SYSTEMS', 'CHECK', 'Aircraft systems'),
        ChecklistItem('WEATHER RADAR', 'SET', 'Weather radar'),
    )),
    ChecklistStage('DESCENT', (
        ChecklistItem('DESCENT BRIEFING', 'COMPLETE', 'Approach briefing'),
        ChecklistItem('LANDING DATA', 'SET', 'Landing performance'),
        ChecklistItem('AUTOBRAKE', 'SET', 'Automatic braking'),
    )),
    ChecklistStage('APPROACH', (
        ChecklistItem('GEAR', 'DOWN', 'Landing gear'),
        ChecklistItem('FLAPS', 'SET', 'Landing configuration'),
        ChecklistItem('LANDING LIGHTS', 'ON', 'Landing lights'),
        ChecklistItem('CABIN', 'READY', 'Cabin ready'),
    )),
    ChecklistStage('LANDING', (
        ChecklistItem('REVERSE THRUST', 'AS REQUIRED', 'Reverse thrust'),
        ChecklistItem('BRAKES', 'APPLY', 'Wheel brakes'),
        ChecklistItem('SPOILERS', 'CHECK', 'Ground spoilers'),
    )),
    ChecklistStage('AFTER LANDING', (
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('SPEED BRAKE', 'DOWN', 'Speed brake'),
        ChecklistItem('APU', 'START', 'Auxiliary Power Unit'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Taxi lights'),
    )),
    ChecklistStage('PARKING / SHUTDOWN', (
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('ENGINES', 'OFF', 'Engine shutdown'),
        ChecklistItem('FUEL PUMPS', 'OFF', 'Fuel system'),
        ChecklistItem('BEACON', 'OFF', 'Anti-collision light'),
        ChecklistItem('BATTERY', 'OFF', 'Electrical system'),
    )),
)
register_checklist(_aircraft, _stages)

_aircraft = AIRCRAFTS.find_by_name('777-300ER')
if not isinstance(_aircraft, Aircraft):
    raise RuntimeError('Не найдена модель 777-300ER')
_stages = (
    ChecklistStage('COCKPIT PREPARATION', (
        ChecklistItem('BATTERY', 'ON', 'Aircraft electrical system'),
        ChecklistItem('GROUND POWER', 'ON', 'External electrical power'),
        ChecklistItem('APU', 'START / ON', 'Auxiliary Power Unit (ВСУ)'),
        ChecklistItem('IRS', 'ALIGN', 'Inertial Reference System'),
        ChecklistItem('FMS', 'SET', 'Flight Management System'),
        ChecklistItem('OXYGEN', 'CHECK', 'Crew oxygen system'),
        ChecklistItem('FIRE TEST', 'TEST', 'Fire warning system'),
        ChecklistItem('FUEL', 'CHECK', 'Fuel quantity and pumps'),
        ChecklistItem('HYDRAULICS', 'CHECK', 'Hydraulic system'),
    )),
    ChecklistStage('BEFORE START', (
        ChecklistItem('DOORS', 'CLOSED', 'Aircraft doors'),
        ChecklistItem('BEACON', 'ON', 'Anti-collision light'),
        ChecklistItem('PACKS', 'OFF', 'Engine start configuration'),
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('PUSHBACK', 'CLEAR', 'Pushback clearance'),
    )),
    ChecklistStage('ENGINE START', (
        ChecklistItem('ENGINE 2', 'START', 'GE90 engine start'),
        ChecklistItem('ENGINE 1', 'START', 'GE90 engine start'),
        ChecklistItem('N1/N2', 'MONITOR', 'Engine rotation'),
        ChecklistItem('EGT', 'CHECK', 'Exhaust gas temperature'),
        ChecklistItem('OIL PRESSURE', 'CHECK', 'Engine oil pressure'),
        ChecklistItem('GENERATORS', 'ON', 'Electrical generators'),
    )),
    ChecklistStage('AFTER START', (
        ChecklistItem('PACKS', 'ON', 'Air conditioning system'),
        ChecklistItem('BLEEDS', 'ON', 'Pneumatic system'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Engine anti-ice'),
        ChecklistItem('FLIGHT CONTROLS', 'CHECK', 'Flight controls'),
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
    )),
    ChecklistStage('TAXI', (
        ChecklistItem('BRAKES', 'CHECK', 'Brake system'),
        ChecklistItem('FLIGHT INSTRUMENTS', 'CHECK', 'Flight instruments'),
        ChecklistItem('TAKEOFF BRIEFING', 'COMPLETE', 'Crew briefing'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Exterior lights'),
    )),
    ChecklistStage('BEFORE TAKEOFF', (
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
        ChecklistItem('SPEED BRAKE', 'ARM', 'Speed brake system'),
        ChecklistItem('AUTOTHROTTLE', 'ARM', 'Automatic thrust'),
        ChecklistItem('TRANSPONDER', 'TA/RA', 'Traffic avoidance system'),
        ChecklistItem('CABIN', 'READY', 'Cabin ready'),
        ChecklistItem('TAKEOFF WARNING', 'TEST', 'Warning system'),
    )),
    ChecklistStage('AFTER TAKEOFF', (
        ChecklistItem('GEAR', 'UP', 'Landing gear'),
        ChecklistItem('FLAPS', 'RETRACT', 'Flap retraction'),
        ChecklistItem('CLIMB POWER', 'SET', 'Engine thrust'),
    )),
    ChecklistStage('CLIMB', (
        ChecklistItem('ENGINE PARAMETERS', 'MONITOR', 'Engine monitoring'),
        ChecklistItem('PRESSURIZATION', 'CHECK', 'Cabin pressure'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Ice protection'),
        ChecklistItem('FUEL BALANCE', 'CHECK', 'Fuel system'),
    )),
    ChecklistStage('CRUISE', (
        ChecklistItem('FUEL', 'MONITOR', 'Fuel monitoring'),
        ChecklistItem('SYSTEMS', 'CHECK', 'Aircraft systems'),
        ChecklistItem('WEATHER RADAR', 'SET', 'Weather radar'),
        ChecklistItem('ETOPS', 'CHECK', 'Long range operations'),
    )),
    ChecklistStage('DESCENT', (
        ChecklistItem('DESCENT BRIEFING', 'COMPLETE', 'Approach briefing'),
        ChecklistItem('LANDING DATA', 'SET', 'Landing performance'),
        ChecklistItem('AUTOBRAKE', 'SET', 'Automatic braking'),
        ChecklistItem('APPROACH SETUP', 'COMPLETE', 'Navigation setup'),
    )),
    ChecklistStage('APPROACH', (
        ChecklistItem('LANDING GEAR', 'DOWN', 'Landing gear'),
        ChecklistItem('FLAPS', 'SET', 'Landing configuration'),
        ChecklistItem('LANDING LIGHTS', 'ON', 'Landing lights'),
        ChecklistItem('CABIN', 'READY', 'Cabin preparation'),
        ChecklistItem('SPEED BRAKE', 'ARM', 'Speed brake'),
    )),
    ChecklistStage('LANDING', (
        ChecklistItem('REVERSE THRUST', 'AS REQUIRED', 'Reverse thrust'),
        ChecklistItem('BRAKES', 'APPLY', 'Wheel brakes'),
        ChecklistItem('SPOILERS', 'CHECK', 'Ground spoilers'),
        ChecklistItem('CENTERLINE', 'MAINTAIN', 'Runway tracking'),
    )),
    ChecklistStage('AFTER LANDING', (
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('SPEED BRAKE', 'DOWN', 'Speed brake'),
        ChecklistItem('APU', 'START', 'Auxiliary Power Unit'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Taxi lights'),
        ChecklistItem('TRANSPONDER', 'STANDBY', 'Traffic system'),
    )),
    ChecklistStage('PARKING / SHUTDOWN', (
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('ENGINES', 'OFF', 'Engine shutdown'),
        ChecklistItem('FUEL PUMPS', 'OFF', 'Fuel system'),
        ChecklistItem('BEACON', 'OFF', 'Anti-collision light'),
        ChecklistItem('EXTERNAL POWER', 'ON', 'Ground power'),
        ChecklistItem('BATTERY', 'OFF', 'Electrical system'),
    )),
)
register_checklist(_aircraft, _stages)

_aircraft = AIRCRAFTS.find_by_name('737-800')
if not isinstance(_aircraft, Aircraft):
    raise RuntimeError('Не найдена модель 737-800')
_stages = (
    ChecklistStage('COCKPIT PREPARATION', (
        ChecklistItem('BATTERY', 'ON', 'Aircraft electrical system'),
        ChecklistItem('GROUND POWER', 'ON', 'External power'),
        ChecklistItem('APU', 'START / ON', 'Auxiliary Power Unit'),
        ChecklistItem('IRS', 'ALIGN', 'Inertial Reference System'),
        ChecklistItem('FMC', 'SET', 'Flight Management Computer'),
        ChecklistItem('FUEL', 'CHECK', 'Fuel quantity'),
        ChecklistItem('HYDRAULICS', 'CHECK', 'Hydraulic system'),
    )),
    ChecklistStage('BEFORE START', (
        ChecklistItem('DOORS', 'CLOSED', 'Aircraft doors'),
        ChecklistItem('BEACON', 'ON', 'Anti-collision light'),
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('PUSHBACK', 'CLEAR', 'Pushback clearance'),
    )),
    ChecklistStage('ENGINE START', (
        ChecklistItem('ENGINE 2', 'START', 'CFM56 engine start'),
        ChecklistItem('ENGINE 1', 'START', 'CFM56 engine start'),
        ChecklistItem('N1/N2', 'CHECK', 'Engine rotation'),
        ChecklistItem('EGT', 'MONITOR', 'Exhaust gas temperature'),
        ChecklistItem('GENERATORS', 'ON', 'Electrical generators'),
    )),
)
register_checklist(_aircraft, _stages)

_aircraft = AIRCRAFTS.find_by_name('C172 Skyhawk')
if not isinstance(_aircraft, Aircraft):
    raise RuntimeError('Не найдена модель C172 Skyhawk')
_stages = (
    ChecklistStage('COCKPIT PREPARATION', (
        ChecklistItem('DOCUMENTS', 'CHECK', 'Aircraft documents'),
        ChecklistItem('BATTERY', 'ON', 'Electrical system'),
        ChecklistItem('FUEL SELECTOR', 'BOTH', 'Fuel selector'),
        ChecklistItem('FUEL QUANTITY', 'CHECK', 'Fuel quantity'),
        ChecklistItem('OIL LEVEL', 'CHECK', 'Engine oil'),
        ChecklistItem('MASTER SWITCH', 'ON', 'Electrical power'),
        ChecklistItem('MIXTURE', 'RICH', 'Engine mixture'),
        ChecklistItem('CARB HEAT', 'COLD', 'Carburetor heat'),
    )),
    ChecklistStage('BEFORE START', (
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('AREA', 'CLEAR', 'Propeller area'),
        ChecklistItem('BEACON', 'ON', 'Anti-collision light'),
        ChecklistItem('PRIMER', 'AS REQUIRED', 'Engine priming'),
    )),
    ChecklistStage('ENGINE START', (
        ChecklistItem('STARTER', 'ENGAGE', 'Engine start'),
        ChecklistItem('RPM', 'CHECK', 'Engine RPM'),
        ChecklistItem('OIL PRESSURE', 'CHECK', 'Engine oil pressure'),
        ChecklistItem('ALTERNATOR', 'ON', 'Electrical charging'),
    )),
    ChecklistStage('AFTER START', (
        ChecklistItem('AVIONICS', 'ON', 'Avionics system'),
        ChecklistItem('RADIOS', 'SET', 'Communication radios'),
        ChecklistItem('FLIGHT CONTROLS', 'CHECK', 'Control surfaces'),
        ChecklistItem('TRIM', 'SET', 'Aircraft trim'),
    )),
    ChecklistStage('TAXI', (
        ChecklistItem('BRAKES', 'CHECK', 'Brake system'),
        ChecklistItem('COMPASS', 'CHECK', 'Heading indication'),
        ChecklistItem('INSTRUMENTS', 'CHECK', 'Flight instruments'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Exterior lights'),
    )),
    ChecklistStage('BEFORE TAKEOFF', (
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
        ChecklistItem('MIXTURE', 'RICH', 'Engine mixture'),
        ChecklistItem('CARB HEAT', 'COLD', 'Carburetor heat'),
        ChecklistItem('ENGINE INSTRUMENTS', 'CHECK', 'Engine parameters'),
        ChecklistItem('RUNWAY', 'CLEAR', 'Runway check'),
    )),
    ChecklistStage('AFTER TAKEOFF', (
        ChecklistItem('CLIMB POWER', 'SET', 'Engine power'),
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('GEAR', 'UP', 'Landing gear if installed'),
    )),
    ChecklistStage('CLIMB', (
        ChecklistItem('ENGINE PARAMETERS', 'MONITOR', 'Engine monitoring'),
        ChecklistItem('ALTIMETER', 'CHECK', 'Altitude'),
        ChecklistItem('TRIM', 'ADJUST', 'Aircraft trim'),
    )),
    ChecklistStage('CRUISE', (
        ChecklistItem('POWER', 'SET', 'Cruise power'),
        ChecklistItem('FUEL', 'MONITOR', 'Fuel monitoring'),
        ChecklistItem('ENGINE', 'MONITOR', 'Engine condition'),
    )),
    ChecklistStage('DESCENT', (
        ChecklistItem('DESCENT BRIEFING', 'COMPLETE', 'Landing preparation'),
        ChecklistItem('POWER', 'REDUCE', 'Engine power'),
        ChecklistItem('ALTITUDE', 'CHECK', 'Altitude control'),
    )),
    ChecklistStage('APPROACH', (
        ChecklistItem('LANDING LIGHTS', 'ON', 'Landing lights'),
        ChecklistItem('MIXTURE', 'RICH', 'Engine mixture'),
        ChecklistItem('FLAPS', 'SET', 'Landing configuration'),
    )),
    ChecklistStage('LANDING', (
        ChecklistItem('TOUCHDOWN', 'COMPLETE', 'Landing'),
        ChecklistItem('BRAKES', 'APPLY', 'Wheel brakes'),
        ChecklistItem('FLAPS', 'AS REQUIRED', 'Flap setting'),
    )),
    ChecklistStage('AFTER LANDING', (
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('TRANSPONDER', 'STANDBY', 'Transponder'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Taxi lights'),
    )),
    ChecklistStage('PARKING / SHUTDOWN', (
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('AVIONICS', 'OFF', 'Avionics'),
        ChecklistItem('MASTER SWITCH', 'OFF', 'Electrical system'),
        ChecklistItem('FUEL SELECTOR', 'OFF', 'Fuel system'),
    )),
)
register_checklist(_aircraft, _stages)

_aircraft = AIRCRAFTS.find_by_name('ATR 72-600')
if not isinstance(_aircraft, Aircraft):
    raise RuntimeError('Не найдена модель ATR 72-600')
_stages = (
    ChecklistStage('COCKPIT PREPARATION', (
        ChecklistItem('BATTERY', 'ON', 'Electrical system'),
        ChecklistItem('EXT PWR', 'ON', 'External power'),
        ChecklistItem('APU', 'START / ON', 'Auxiliary Power Unit'),
        ChecklistItem('FUEL', 'CHECK', 'Fuel system'),
        ChecklistItem('HYDRAULICS', 'CHECK', 'Hydraulic system'),
        ChecklistItem('FMS', 'SET', 'Flight management system'),
    )),
    ChecklistStage('BEFORE START', (
        ChecklistItem('DOORS', 'CLOSED', 'Aircraft doors'),
        ChecklistItem('BEACON', 'ON', 'Anti-collision light'),
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('PUSHBACK', 'CLEAR', 'Pushback clearance'),
    )),
    ChecklistStage('ENGINE START', (
        ChecklistItem('ENGINE 2', 'START', 'PW127 engine start'),
        ChecklistItem('ENGINE 1', 'START', 'PW127 engine start'),
        ChecklistItem('ENGINE PARAMETERS', 'CHECK', 'Engine indications'),
        ChecklistItem('GENERATORS', 'ON', 'Electrical generators'),
    )),
    ChecklistStage('AFTER START', (
        ChecklistItem('BLEEDS', 'SET', 'Pneumatic system'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Ice protection'),
        ChecklistItem('FLIGHT CONTROLS', 'CHECK', 'Flight controls'),
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
    )),
    ChecklistStage('TAXI', (
        ChecklistItem('BRAKES', 'CHECK', 'Brake system'),
        ChecklistItem('INSTRUMENTS', 'CHECK', 'Flight instruments'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Exterior lights'),
    )),
    ChecklistStage('BEFORE TAKEOFF', (
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
        ChecklistItem('POWER LEVERS', 'SET', 'Engine power'),
        ChecklistItem('TAKEOFF WARNING', 'TEST', 'Warning system'),
        ChecklistItem('CABIN', 'READY', 'Cabin ready'),
    )),
    ChecklistStage('AFTER TAKEOFF', (
        ChecklistItem('GEAR', 'UP', 'Landing gear'),
        ChecklistItem('FLAPS', 'RETRACT', 'Flap retraction'),
    )),
    ChecklistStage('CLIMB', (
        ChecklistItem('ENGINE PARAMETERS', 'MONITOR', 'Engine monitoring'),
        ChecklistItem('PRESSURIZATION', 'CHECK', 'Cabin pressure'),
    )),
    ChecklistStage('CRUISE', (
        ChecklistItem('FUEL', 'MONITOR', 'Fuel monitoring'),
        ChecklistItem('SYSTEMS', 'CHECK', 'Aircraft systems'),
    )),
    ChecklistStage('DESCENT', (
        ChecklistItem('LANDING DATA', 'SET', 'Landing performance'),
        ChecklistItem('APPROACH', 'BRIEF', 'Approach briefing'),
    )),
    ChecklistStage('APPROACH', (
        ChecklistItem('GEAR', 'DOWN', 'Landing gear'),
        ChecklistItem('FLAPS', 'SET', 'Landing configuration'),
        ChecklistItem('CABIN', 'READY', 'Cabin preparation'),
    )),
    ChecklistStage('LANDING', (
        ChecklistItem('REVERSE', 'AS REQUIRED', 'Reverse thrust'),
        ChecklistItem('BRAKES', 'APPLY', 'Wheel brakes'),
    )),
    ChecklistStage('AFTER LANDING', (
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('APU', 'START', 'Auxiliary Power Unit'),
    )),
    ChecklistStage('PARKING / SHUTDOWN', (
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('ENGINES', 'OFF', 'Engine shutdown'),
        ChecklistItem('BATTERY', 'OFF', 'Electrical system'),
    )),
)
register_checklist(_aircraft, _stages)

_aircraft = AIRCRAFTS.find_by_name('E190-E2')
if not isinstance(_aircraft, Aircraft):
    raise RuntimeError('Не найдена модель E190-E2')
_stages = (
    ChecklistStage('COCKPIT PREPARATION', (
        ChecklistItem('BATTERY', 'ON', 'Aircraft electrical system'),
        ChecklistItem('EXT PWR', 'ON', 'External power'),
        ChecklistItem('APU', 'START / ON', 'Auxiliary Power Unit'),
        ChecklistItem('IRS', 'ALIGN', 'Inertial Reference System'),
        ChecklistItem('FMS', 'SET', 'Flight management system'),
        ChecklistItem('FUEL', 'CHECK', 'Fuel quantity'),
        ChecklistItem('HYDRAULICS', 'CHECK', 'Hydraulic system'),
    )),
    ChecklistStage('BEFORE START', (
        ChecklistItem('DOORS', 'CLOSED', 'Aircraft doors'),
        ChecklistItem('BEACON', 'ON', 'Anti-collision light'),
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('PUSHBACK', 'CLEAR', 'Pushback clearance'),
    )),
    ChecklistStage('ENGINE START', (
        ChecklistItem('ENGINE 2', 'START', 'PW1900G engine start'),
        ChecklistItem('ENGINE 1', 'START', 'PW1900G engine start'),
        ChecklistItem('ENGINE PARAMETERS', 'CHECK', 'Engine indications'),
        ChecklistItem('GENERATORS', 'ON', 'Electrical generators'),
    )),
    ChecklistStage('AFTER START', (
        ChecklistItem('PACKS', 'ON', 'Air conditioning'),
        ChecklistItem('BLEEDS', 'SET', 'Pneumatic system'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Ice protection'),
        ChecklistItem('FLIGHT CONTROLS', 'CHECK', 'Flight controls'),
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
    )),
    ChecklistStage('TAXI', (
        ChecklistItem('BRAKES', 'CHECK', 'Brake system'),
        ChecklistItem('FLIGHT INSTRUMENTS', 'CHECK', 'Flight instruments'),
        ChecklistItem('TAKEOFF BRIEFING', 'COMPLETE', 'Crew briefing'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Exterior lights'),
    )),
    ChecklistStage('BEFORE TAKEOFF', (
        ChecklistItem('FLAPS', 'SET', 'Takeoff configuration'),
        ChecklistItem('SPOILERS', 'ARM', 'Ground spoilers'),
        ChecklistItem('AUTOTHROTTLE', 'ARM', 'Automatic thrust'),
        ChecklistItem('TCAS', 'TA/RA', 'Traffic avoidance'),
        ChecklistItem('CABIN', 'READY', 'Cabin ready'),
    )),
    ChecklistStage('AFTER TAKEOFF', (
        ChecklistItem('GEAR', 'UP', 'Landing gear'),
        ChecklistItem('FLAPS', 'RETRACT', 'Flap retraction'),
        ChecklistItem('CLIMB POWER', 'SET', 'Engine thrust'),
    )),
    ChecklistStage('CLIMB', (
        ChecklistItem('ENGINE PARAMETERS', 'MONITOR', 'Engine monitoring'),
        ChecklistItem('PRESSURIZATION', 'CHECK', 'Cabin pressure'),
        ChecklistItem('ANTI-ICE', 'AS REQUIRED', 'Ice protection'),
    )),
    ChecklistStage('CRUISE', (
        ChecklistItem('FUEL', 'MONITOR', 'Fuel monitoring'),
        ChecklistItem('SYSTEMS', 'CHECK', 'Aircraft systems'),
        ChecklistItem('WEATHER RADAR', 'SET', 'Weather radar'),
    )),
    ChecklistStage('DESCENT', (
        ChecklistItem('DESCENT BRIEFING', 'COMPLETE', 'Approach briefing'),
        ChecklistItem('LANDING DATA', 'SET', 'Landing performance'),
        ChecklistItem('AUTOBRAKE', 'SET', 'Automatic braking'),
    )),
    ChecklistStage('APPROACH', (
        ChecklistItem('LANDING GEAR', 'DOWN', 'Landing gear'),
        ChecklistItem('FLAPS', 'SET', 'Landing configuration'),
        ChecklistItem('LANDING LIGHTS', 'ON', 'Landing lights'),
        ChecklistItem('CABIN', 'READY', 'Cabin preparation'),
    )),
    ChecklistStage('LANDING', (
        ChecklistItem('REVERSE THRUST', 'AS REQUIRED', 'Reverse thrust'),
        ChecklistItem('BRAKES', 'APPLY', 'Wheel brakes'),
        ChecklistItem('SPOILERS', 'CHECK', 'Ground spoilers'),
    )),
    ChecklistStage('AFTER LANDING', (
        ChecklistItem('FLAPS', 'UP', 'Flap retraction'),
        ChecklistItem('SPOILERS', 'DISARM', 'Spoilers'),
        ChecklistItem('APU', 'START', 'Auxiliary Power Unit'),
        ChecklistItem('LIGHTS', 'AS REQUIRED', 'Taxi lights'),
    )),
    ChecklistStage('PARKING / SHUTDOWN', (
        ChecklistItem('PARKING BRAKE', 'SET', 'Parking brake'),
        ChecklistItem('ENGINES', 'OFF', 'Engine shutdown'),
        ChecklistItem('FUEL PUMPS', 'OFF', 'Fuel system'),
        ChecklistItem('BEACON', 'OFF', 'Anti-collision light'),
        ChecklistItem('BATTERY', 'OFF', 'Electrical system'),
    )),
)
register_checklist(_aircraft, _stages)


# Здесь находится основная работа окна.
class SkyBookApp:
    def __init__(self, page):
        self.page = page
        self.current_manufacturer= None
        self.current_aircraft= None
        self.current_checklist= None
        self._checkboxes= []
        self._session_start = datetime.now()
        self._login = getpass.getuser() or "UserName"
        self._saved_keys = self._read_saved_keys()

        self.page.title = "SkyBook EFB"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#101820"
        self.page.padding = 22
        self.page.window.width = 1200
        self.page.window.height = 820
        self.page.window.min_width = 760
        self.page.window.min_height = 600
        self.page.on_close = self.close_app
        self.show_manufacturers()

    def _read_saved_keys(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        saved= set()
        if not STATE_FILE.exists():
            return saved
        for line in STATE_FILE.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) == 2 and parts[1] == "1":
                saved.add(parts[0])
        return saved

    def _save_state(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        checked_keys = set(self._saved_keys)
        for key, checkbox in self._checkboxes:
            if checkbox.value:
                checked_keys.add(key)
            else:
                checked_keys.discard(key)
        STATE_FILE.write_text("".join(f"{key}\t1\n" for key in sorted(checked_keys)), encoding="utf-8")
        self._saved_keys = checked_keys

    def close_app(self, event=None):
        self._save_state()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not REPORT_FILE.exists():
            REPORT_FILE.write_text("login | time_in | time_out\n", encoding="utf-8")
        time_out = datetime.now()
        with REPORT_FILE.open("a", encoding="utf-8") as report:
            report.write(f"{self._login} | {self._session_start.strftime(TIME_FORMAT)} | {time_out.strftime(TIME_FORMAT)}\n")

    def _refresh(self, controls):
        self.page.controls.clear()
        self.page.controls.append(controls)
        self.page.update()

    def _shell(self, title, body, back_action=None):
        header_controls = []
        if back_action is not None:
            header_controls.append(BackActionButton(back_action))
        header_controls.extend([
            ft.Column([PageHeading(title), MutedText("Electronic Flight Bag · учебный интерфейс")], spacing=2, expand=True),
            AppIcon(ft.Icons.FLIGHT_TAKEOFF, 30),
        ])
        header = ft.Row(header_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        return ft.Column([header, StageSeparator(), body], spacing=18, expand=True, scroll=ft.ScrollMode.AUTO)

    def show_manufacturers(self, event=None):
        self.current_manufacturer = None
        self.current_aircraft = None
        self.current_checklist = None
        manufacturer_cards = []
        descriptions = (
            ("Airbus", "Commercial aircraft", ft.Icons.FLIGHT),
            # Для Boeing не показываем иконку или картинку.
            ("Boeing", "Commercial aircraft", None),
            ("Cessna", "General aviation", ft.Icons.AIRPLANEMODE_ACTIVE),
            ("ATR", "Regional turboprop", ft.Icons.FLIGHT),
            ("Embraer", "Regional aircraft", ft.Icons.FLIGHT),
        )
        for manufacturer_name, description, icon_name in descriptions:
            manufacturer = MANUFACTURERS.find_by_name(manufacturer_name)
            if not isinstance(manufacturer, Manufacturer):
                continue
            card_controls = []
            if icon_name is not None:
                card_controls.append(AppIcon(icon_name, 34))
            card_controls.extend([
                AppText(manufacturer.name, 20, weight=ft.FontWeight.BOLD),
                MutedText(description),
                ActionButton("Открыть модели", lambda e, m=manufacturer: self.show_aircraft(m)),
            ])
            card_body = ft.Column(card_controls, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.START)
            manufacturer_cards.append(PanelCard(content=AircraftTile(card_body, on_click=lambda e, m=manufacturer: self.show_aircraft(m))))
        body = ft.Column([
            InfoPanel(ft.Row([
                AppIcon(ft.Icons.CHECKLIST, 30),
                ft.Column([AppText("Предполётные процедуры в одном месте", 18, weight=ft.FontWeight.BOLD),
                           MutedText("Выберите производителя, модель и этап чек-листа.")], spacing=4, expand=True)
            ], spacing=14)),
            ft.GridView(controls=manufacturer_cards, runs_count=2, max_extent=520, child_aspect_ratio=2.4, spacing=14, run_spacing=14, expand=True),
            MutedText("Учебный проект. Не использовать вместо утверждённой эксплуатационной документации.")
        ], spacing=18, expand=True)
        self._refresh(self._shell("SkyBook EFB", body))

    def show_aircraft(self, manufacturer, event=None):
        self.current_manufacturer = manufacturer
        cards = []
        for aircraft in AIRCRAFTS:
            if isinstance(aircraft, Aircraft) and aircraft.manufacturer == manufacturer:
                body = ft.Column([
                    AppText(aircraft.model, 20, weight=ft.FontWeight.BOLD),
                    MutedText(f"Двигатель: {aircraft.engine}"),
                    ActionButton("Открыть чек-лист", lambda e, a=aircraft: self.open_checklist(a)),
                ], spacing=10)
                cards.append(PanelCard(content=AircraftTile(body, on_click=lambda e, a=aircraft: self.open_checklist(a))))
        content = ft.GridView(controls=cards, runs_count=2, max_extent=560, child_aspect_ratio=2.6, spacing=14, run_spacing=14, expand=True)
        self._refresh(self._shell(manufacturer.name, content, self.show_manufacturers))

    def _state_key(self, aircraft, stage, index):
        return f"{aircraft.model}|{stage.name}|{index}"

    def open_checklist(self, aircraft, event=None):
        self.current_aircraft = aircraft
        found = CHECKLISTS.find_by_name(aircraft.model)
        if not isinstance(found, AircraftChecklist):
            info = InfoPanel(AppText("Для этой модели чек-лист пока не добавлен."))
            self._refresh(self._shell(aircraft.model, info, lambda e: self.show_aircraft(aircraft.manufacturer)))
            return
        self.current_checklist = found
        self._checkboxes = []
        stage_controls = []
        for stage in found.stages:
            item_controls = []
            for index, item in enumerate(stage.items):
                key = self._state_key(aircraft, stage, index)
                checkbox = ft.Checkbox(value=key in self._saved_keys, on_change=self._on_check_change)
                self._checkboxes.append((key, checkbox))
                item_controls.append(ChecklistTile(ft.Row([
                    checkbox,
                    ft.Column([
                        AppText(item.title, 15, weight=ft.FontWeight.BOLD),
                        AppText(f"Действие: {item.action}", 13, color="#64D6C4"),
                        MutedText(item.description),
                    ], spacing=3, expand=True)
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)))
            stage_controls.append(ft.Column([
                AppText(stage.name, 17, weight=ft.FontWeight.BOLD, color="#64D6C4"),
                ft.Column(item_controls, spacing=7),
            ], spacing=9))
        self.progress_text = AppText("", 14, weight=ft.FontWeight.BOLD)
        self.progress_bar = ft.ProgressBar(value=0, color="#64D6C4", bgcolor="#2D4356", bar_height=7)
        progress_panel = ProgressPanel(ft.Column([self.progress_text, self.progress_bar], spacing=10))
        reset_button = ActionButton("Сбросить отметки", self.reset_checklist, icon=ft.Icons.RESTART_ALT)
        top = ft.Column([
            AppText(f"{aircraft.manufacturer.name} {aircraft.model}", 22, weight=ft.FontWeight.BOLD),
            MutedText(f"Двигатель: {aircraft.engine} · {len(found.stages)} этапов"),
            progress_panel,
            ft.Row([reset_button], alignment=ft.MainAxisAlignment.END),
        ], spacing=10)
        checklist_content = ft.Column(stage_controls, spacing=18, expand=True, scroll=ft.ScrollMode.AUTO)
        body = ft.Column([top, checklist_content], spacing=16, expand=True)
        self._refresh(self._shell(f"Чек-лист · {aircraft.model}", body, lambda e: self.show_aircraft(aircraft.manufacturer)))
        self._update_progress()

    def _on_check_change(self, event):
        self._save_state()
        self._update_progress()

    def _update_progress(self):
        if not self._checkboxes:
            done = 0
            total = 0
        else:
            total = len(self._checkboxes)
            done = sum(1 for _, checkbox in self._checkboxes if checkbox.value)
        ratio = done / total if total else 0
        if hasattr(self, "progress_text"):
            self.progress_text.value = f"Выполнено: {done} из {total} · {round(ratio * 100)}%"
            self.progress_bar.value = ratio
            self.page.update()

    def reset_checklist(self, event=None):
        for key, checkbox in self._checkboxes:
            checkbox.value = False
            self._saved_keys.discard(key)
        self._save_state()
        self._update_progress()


def main(page):
    SkyBookApp(page)


if __name__ == "__main__":
    ft.run(main)
