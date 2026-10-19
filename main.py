import flet as ft
import getpass
import os
from datetime import datetime

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "state.txt")
REPORT_FILE = os.path.join(DATA_DIR, "report.txt")

data = [
    ("Airbus", "A320neo", "LEAP-1A", [
        ("COCKPIT PREP", [("BATTERY", "ON", "Питание"), ("APU", "START", "ВСУ")]),
        ("BEFORE START", [("DOORS", "CLOSED", "Двери"), ("BEACON", "ON", "Маяк")]),
        ("ENGINE START", [("ENG 2", "START", "Запуск"), ("OIL", "CHECK", "Масло")]),
        ("TAXI", [("BRAKES", "CHECK", "Тормоза")]),
        ("TAKEOFF", [("FLAPS", "SET", "Закрылки")]),
        ("LANDING", [("GEAR", "DOWN", "Шасси")]),
    ]),
    ("Cessna", "C172", "IO-360", [
        ("COCKPIT", [("BATTERY", "ON", "Питание"), ("FUEL", "BOTH", "Топливо")]),
        ("START", [("STARTER", "ENGAGE", "Запуск")]),
        ("TAKEOFF", [("FLAPS", "SET", "Закрылки")]),
        ("LANDING", [("BRAKES", "APPLY", "Тормоза")]),
    ]),
    # TODO: добавить ещё модели
]

class Plane:
    def __init__(self, maker, model, engine):
        self.maker = maker
        self.model = model
        self.engine = engine

class Item:
    def __init__(self, name, action, desc):
        self.name = name
        self.action = action
        self.desc = desc

class Stage:
   def __init__(self, name, items):
        self.name = name
        self.items = items

planes = []
stages = {}

for maker, model, engine, raw in data:
    planes.append(Plane(maker, model, engine))
    st_list = []
    for st_name, items_raw in raw:
        items = [Item(n, a, d) for n, a, d in items_raw]
        st_list.append(Stage(st_name, items))
    stages[model] = st_list


def read_keys():
    if not os.path.exists(STATE_FILE):
        return []
    res = []
    f = open(STATE_FILE, encoding="utf-8")
    for line in f:
        if line.strip().endswith("1"):
            res.append(line.split("\t")[0])
    f.close()
    return res


def save_keys(keys):
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    txt = ""
    for k in keys:
        txt = txt + k + "\t1\n"
    open(STATE_FILE, "w", encoding="utf-8").write(txt)


def save_report(login, start):
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if not os.path.exists(REPORT_FILE):
        open(REPORT_FILE, "w", encoding="utf-8").write("login|in|out\n")
    f = open(REPORT_FILE, "a", encoding="utf-8")
    f.write(login + "|" + start + "|" + datetime.now().strftime("%d.%m.%Y %H:%M:%S") + "\n")
    f.close()


class App:
    def __init__(self, page):
        self.page = page
        self.maker = None
        self.plane = None
        self.boxes = []
        self.start = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.login = getpass.getuser()
        self.keys = read_keys()

        page.title = "SkyBook"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#101820"
        page.padding = 20
        page.window.width = 1000
        page.window.height = 750
        page.on_close = self.close
        self.makers()

    def close(self, e=None):
        save_keys(self.keys)
        save_report(self.login, self.start)

    def show(self, col):
        self.page.controls.clear()
        self.page.controls.append(col)
        self.page.update()

    def frame(self, title, body, back=None):
        row = []
        if back:
            row.append(ft.IconButton(ft.Icons.ARROW_BACK, on_click=back))
        row.append(ft.Text(title, size=24, color="white", weight=ft.FontWeight.BOLD))
        return ft.Column([ft.Row(row), ft.Divider(color="#2D4356"), body], spacing=12, expand=True)

    def makers(self, e=None):
        seen = []
        for p in planes:
            if p.maker not in seen:
                seen.append(p.maker)

        cards = []
        for m in seen:
            cards.append(ft.Container(
                content=ft.Column([
                    ft.Text(m, size=16, color="white"),
                    # ft.Button(text="Открыть", on_click=...)
                    ft.Button("Открыть", on_click=lambda e, m=m: self.show_planes(m)),
                ], spacing=6),
                padding=12, bgcolor="#1A2937", border_radius=8,
            ))

        body = ft.Column([
            ft.Text("Выберите производителя", color="#9EADBD"),
            ft.GridView(cards, runs_count=2, spacing=10, expand=True),
        ], spacing=10, expand=True)
        self.show(self.frame("SkyBook EFB", body))

    def show_planes(self, maker, e=None):
        self.maker = maker
        cards = []
        for p in planes:
            if p.maker != maker:
                continue
            cards.append(ft.Container(
                content=ft.Column([
                    ft.Text(p.maker + " " + p.model, size=14, color="white"),
                    ft.Text(f"Двигатель: {p.engine}", size=11, color="#9EADBD"),
                    ft.Button("Чек-лист", on_click=lambda e, p=p: self.open(p)),
                ], spacing=4),
                padding=12, bgcolor="#1A2937", border_radius=8,
            ))
        body = ft.Column([ft.GridView(cards, runs_count=2, spacing=10, expand=True)], expand=True)
        self.show(self.frame(maker, body, self.makers))

    def open(self, plane, e=None):
        self.plane = plane
        self.boxes = []
        if plane.model not in stages:
            self.show(self.frame(plane.model, ft.Text("Нет данных", color="white"), self.back))
            return

        cols = []
        for st in stages[plane.model]:
            rows = []
            for i, item in enumerate(st.items):
                key = plane.model + "|" + st.name + "|" + str(i)
                cb = ft.Checkbox(value=key in self.keys, on_change=self.changed)
                self.boxes.append((key, cb))
                rows.append(ft.Row([
                    cb,
                    ft.Column([
                        ft.Text(item.name, size=13, color="white"),
                        ft.Text(item.action, size=11, color="#64D6C4"),
                    ], spacing=1),
                ], spacing=6))
            cols.append(ft.Column([ft.Text(st.name, color="#64D6C4", size=13)] + rows, spacing=4))

        self.prog = ft.Text("", color="white", size=12)
        self.bar = ft.ProgressBar(value=0, color="#64D6C4")
        body = ft.Column([
            ft.Text(plane.model, size=18, color="white", weight=ft.FontWeight.BOLD),
            self.prog, self.bar,
            ft.Button("Сбросить", on_click=self.reset),
        ] + cols, spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)

        self.show(self.frame("Чек-лист", body, self.back))
        self.refresh()

    def back(self, e=None):
        if self.maker:
            self.show_planes(self.maker)
        else:
            self.makers()

    def changed(self, e):
        for key, cb in self.boxes:
            if cb.value:
                self.keys.append(key)
            else:
                if key in self.keys:
                    self.keys.remove(key)
        save_keys(self.keys)
        self.refresh()

    def refresh(self):
        total = len(self.boxes)
        done = 0
        for key, cb in self.boxes:
            if cb.value:
                done = done + 1
        if total > 0:
            percent = round(done * 100 / total)
        else:
            percent = 0
        self.prog.value = str(done) + "/" + str(total) + " (" + str(percent) + "%)"
        self.bar.value = done / total if total else 0
        print("прогресс:", done, total)

    def reset(self, e=None):
        for key, cb in self.boxes:
            cb.value = False
            if key in self.keys:
                self.keys.remove(key)
        save_keys(self.keys)
        self.refresh()

def main(page):
    App(page)

if __name__ == "__main__":
    ft.run(main)