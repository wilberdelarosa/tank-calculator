"""
Aplicación Kivy para cálculo de combustible en tanques cilíndricos horizontales
Compatible con Android mediante Buildozer
Versión mejorada con UI/UX Moderna y Profesional
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line, RoundedRectangle
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
import calculo
import math

# Colores del tema (Moderno Profesional - Dark Mode)
BG_COLOR = (0.05, 0.06, 0.08, 1)       # Fondo casi negro
CARD_COLOR = (0.11, 0.12, 0.15, 1)     # Gris oscuro azulado para tarjetas
ACCENT_COLOR = (0.0, 0.48, 1.0, 1)     # Azul vibrante (Primary)
ACCENT_HOVER = (0.0, 0.58, 1.0, 1)     # Azul más claro
GREEN_COLOR = (0.0, 0.8, 0.5, 1)       # Verde menta moderno
ORANGE_COLOR = (1.0, 0.6, 0.0, 1)      # Naranja intenso (Combustible)
RED_COLOR = (1.0, 0.25, 0.25, 1)       # Rojo suave
TEXT_COLOR = (0.95, 0.95, 0.95, 1)     # Blanco humo
TEXT_GRAY = (0.6, 0.63, 0.68, 1)       # Gris texto secundario
INPUT_BG = (0.08, 0.09, 0.11, 1)       # Fondo de inputs

class Card(BoxLayout):
    """Contenedor con fondo redondeado y estilo de tarjeta"""
    def __init__(self, bg_color=CARD_COLOR, radius=16, **kwargs):
        super().__init__(**kwargs)
        self.padding = kwargs.get('padding', 20)
        self.spacing = kwargs.get('spacing', 10)
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ModernButton(Button):
    """Botón moderno con animaciones y estados"""
    def __init__(self, btn_color=ACCENT_COLOR, text_color=TEXT_COLOR, radius=12, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.base_color = btn_color
        self.text_color = text_color
        self.radius = radius
        self.color = text_color
        self.font_size = '14sp'
        self.bold = True
        
        with self.canvas.before:
            self.bg_color_instr = Color(*self.base_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_press(self):
        self.bg_color_instr.rgba = tuple(c * 0.8 for c in self.base_color[:3]) + (1,)
    
    def on_release(self):
        self.bg_color_instr.rgba = self.base_color
        # Animación de rebote sutil
        anim = Animation(size=(self.width * 1.02, self.height * 1.02), duration=0.05) + \
               Animation(size=(self.width, self.height), duration=0.05)
        anim.start(self)

class ModernTextInput(TextInput):
    """Input de texto con estilo moderno"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = INPUT_BG
        self.foreground_color = TEXT_COLOR
        self.cursor_color = ACCENT_COLOR
        self.padding = [15, 15, 15, 15]
        self.font_size = '16sp'
        self.multiline = False
        self.hint_text_color = TEXT_GRAY
        
        # Borde inferior o contorno
        with self.canvas.after:
            self.line_color = Color(*ACCENT_COLOR)
            self.line = Line(points=[self.x, self.y, self.right, self.y], width=1)
        
        self.bind(pos=self._update_line, size=self._update_line, focus=self._on_focus)
        
    def _update_line(self, *args):
        self.line.points = [self.x, self.y, self.right, self.y]
        
    def _on_focus(self, instance, value):
        if value:
            self.line_color.rgba = (*ACCENT_COLOR[:3], 1)
        else:
            self.line_color.rgba = (*ACCENT_COLOR[:3], 0)


class TankCanvas(FloatLayout):
    """Canvas mejorado para dibujar el tanque 3D con animaciones"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height_value = 0
        self.diameter = 45.0
        self.length = 71.0
        self.animated_height = 0
        self.bind(size=self.update_canvas, pos=self.update_canvas)
        
    def set_tank_dimensions(self, diameter, length):
        self.diameter = diameter
        self.length = length
        self.update_canvas()
    
    def set_height(self, height):
        """Animar el cambio de altura"""
        anim = Animation(animated_height=height, duration=0.3, transition='out_cubic')
        anim.bind(on_progress=lambda *args: self.update_canvas())
        anim.start(self)
        self.height_value = height
    
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Fondo con gradiente simulado
            Color(*CARD_COLOR)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            
            # Calcular dimensiones del tanque
            w, h = self.size
            cx, cy = w / 2, h / 2
            
            # Escalar tanque (más grande)
            scale = min(w * 0.95 / self.length, h * 0.85 / self.diameter)
            tank_length = self.length * scale
            tank_height = self.diameter * scale
            
            # Posición del tanque
            tank_x = cx - tank_length / 2
            tank_y = cy - tank_height / 2
            
            # Sombra del tanque
            Color(0, 0, 0, 0.3)
            RoundedRectangle(
                pos=(tank_x + 5, tank_y - 5),
                size=(tank_length, tank_height),
                radius=[tank_height / 2]
            )
            
            # Dibujar líquido primero (diesel naranja con gradiente)
            if self.animated_height > 0:
                fill_ratio = min(1.0, self.animated_height / self.diameter)
                liquid_height = tank_height * fill_ratio
                
                # Gradiente simulado con múltiples capas
                for i in range(5):
                    alpha = 0.9 - (i * 0.1)
                    offset = i * 2
                    Color(0.98, 0.57 - (i * 0.05), 0.24, alpha)
                    RoundedRectangle(
                        pos=(tank_x + offset, tank_y + offset),
                        size=(tank_length - offset * 2, liquid_height - offset),
                        radius=[min(liquid_height / 2, tank_height / 2)]
                    )
            
            # Dibujar tanque (cuerpo semi-transparente)
            Color(0.35, 0.37, 0.42, 0.4)
            RoundedRectangle(
                pos=(tank_x, tank_y),
                size=(tank_length, tank_height),
                radius=[tank_height / 2]
            )
            
            # Bordes del tanque con efecto metálico
            Color(0.6, 0.65, 0.7, 1)
            Line(
                rounded_rectangle=(tank_x, tank_y, tank_length, tank_height, tank_height / 2),
                width=2.5
            )
            
            # Detalles: líneas de medición
            Color(0.4, 0.45, 0.5, 0.4)
            for i in range(5):
                y_pos = tank_y + (tank_height / 4) * i
                Line(points=[tank_x, y_pos, tank_x + tank_length, y_pos], width=0.5)


class TankApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_tank_id = None
        
    def build(self):
        # Cargar configuración de tanques
        calculo.load_tanks_config()
        self.current_tank_id = calculo._current_tank_id
        
        # Layout principal con padding mejorado
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Header mejorado
        header = BoxLayout(size_hint_y=0.07, spacing=10)
        
        # Card para el header
        header_card = BoxLayout()
        with header_card.canvas.before:
            Color(*CARD_COLOR)
            self.header_bg = RoundedRectangle(size=header_card.size, pos=header_card.pos, radius=[15])
        header_card.bind(size=self._update_header_bg, pos=self._update_header_bg)
        
        header_content = BoxLayout(padding=10, spacing=8)
        title_box = BoxLayout(orientation='vertical', size_hint_x=0.5)
        title_label = Label(
            text='🛢️ Fuel Tank',
            font_size='18sp',
            bold=True,
            color=TEXT_COLOR,
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        subtitle_label = Label(
            text='Calculadora de Combustible',
            font_size='10sp',
            color=TEXT_GRAY,
            halign='left',
            valign='middle'
        )
        subtitle_label.bind(size=subtitle_label.setter('text_size'))
        
        title_box.add_widget(title_label)
        title_box.add_widget(subtitle_label)
        
        # Botón agregar tanque (mejorado)
        add_tank_btn = ModernButton(
            text='+ Nuevo',
            size_hint_x=0.22,
            btn_color=GREEN_COLOR,
            font_size='11sp',
            bold=True
        )
        add_tank_btn.bind(on_press=self.show_add_tank_dialog)
        
        # Selector de tanques (mejorado)
        self.tank_spinner = Spinner(
            text='Seleccionar...',
            values=self.get_tank_names(),
            size_hint_x=0.28,
            background_color=ACCENT_COLOR,
            background_normal='',
            font_size='11sp'
        )
        
        header_card.add_widget(title_box)
        header_card.add_widget(add_tank_btn)
        header_card.add_widget(self.tank_spinner)
        
        header.add_widget(header_card)
        
        # Canvas del tanque mejorado
        self.tank_canvas = TankCanvas(size_hint_y=0.52)
        
        # Porcentaje de llenado superpuesto
        tank_overlay = FloatLayout(size_hint_y=0.04)
        self.fill_percent_label = Label(
            text='0%',
            font_size='38sp',
            bold=True,
            color=ORANGE_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        tank_overlay.add_widget(self.fill_percent_label)
        
        # Info del tanque mejorada
        info_card = BoxLayout(orientation='vertical', size_hint_y=0.09, padding=8, spacing=2)
        with info_card.canvas.before:
            Color(*CARD_COLOR)
            self.info_bg = RoundedRectangle(size=info_card.size, pos=info_card.pos, radius=[15])
        info_card.bind(size=self._update_info_bg, pos=self._update_info_bg)
        
        self.tank_info_label = Label(
            text='Cargando...',
            font_size='11sp',
            color=TEXT_GRAY,
            halign='center'
        )
        
        self.volume_label = Label(
            text='0.00 gal',
            font_size='30sp',
            bold=True,
            color=ACCENT_COLOR,
            halign='center'
        )
        
        info_card.add_widget(self.tank_info_label)
        info_card.add_widget(self.volume_label)
        
        # Slider mejorado con card
        slider_card = BoxLayout(orientation='vertical', size_hint_y=0.11, padding=8, spacing=5)
        with slider_card.canvas.before:
            Color(*CARD_COLOR)
            self.slider_bg = RoundedRectangle(size=slider_card.size, pos=slider_card.pos, radius=[15])
        slider_card.bind(size=self._update_slider_bg, pos=self._update_slider_bg)
        
        slider_header = BoxLayout(size_hint_y=0.35)
        slider_label = Label(
            text='Altura de Vara',
            font_size='12sp',
            color=TEXT_COLOR,
            halign='left',
            size_hint_x=0.45
        )
        slider_label.bind(size=slider_label.setter('text_size'))
        
        # Campo de texto para ingresar altura
        self.height_input = ModernTextInput(
            text='0.0',
            multiline=False,
            input_filter='float',
            size_hint_x=0.25,
            font_size='16sp',
            padding=[10, 8]
        )
        self.height_input.bind(text=self.on_height_input_change)
        
        self.height_value_label = Label(
            text='0.0"',
            font_size='18sp',
            bold=True,
            color=GREEN_COLOR,
            halign='right',
            size_hint_x=0.3
        )
        self.height_value_label.bind(size=self.height_value_label.setter('text_size'))
        
        slider_header.add_widget(slider_label)
        slider_header.add_widget(self.height_input)
        slider_header.add_widget(self.height_value_label)
        
        self.height_slider = Slider(
            min=0,
            max=45,
            value=0,
            step=0.1,
            size_hint_y=0.7,
            cursor_size=(20, 20)
        )
        self.height_slider.bind(value=self.on_slider_change)
        
        slider_card.add_widget(slider_header)
        slider_card.add_widget(self.height_slider)
        
        # Botones de acción mejorados
        action_layout = BoxLayout(size_hint_y=0.09, spacing=10)
        
        calibrate_btn = ModernButton(
            text='📊 Calibrar',
            btn_color=ACCENT_COLOR,
            font_size='14sp',
            bold=True
        )
        calibrate_btn.bind(on_press=self.show_calibrate_dialog)
        
        manage_tanks_btn = ModernButton(
            text='⚙️ Gestión',
            btn_color=(0.39, 0.45, 0.55, 1),
            font_size='14sp',
            bold=True
        )
        manage_tanks_btn.bind(on_press=self.show_manage_tanks)
        
        action_layout.add_widget(calibrate_btn)
        action_layout.add_widget(manage_tanks_btn)
        
        # Agregar todo al layout principal
        main_layout.add_widget(header)
        main_layout.add_widget(self.tank_canvas)
        main_layout.add_widget(tank_overlay)
        main_layout.add_widget(info_card)
        main_layout.add_widget(slider_card)
        main_layout.add_widget(action_layout)
        
        # Vincular eventos y actualizar
        self.tank_spinner.bind(text=self.on_tank_selected)
        self.update_tank_spinner()
        self.on_tank_changed()
        
        return main_layout
    
    def _update_header_bg(self, instance, value):
        self.header_bg.pos = instance.pos
        self.header_bg.size = instance.size
    
    def _update_info_bg(self, instance, value):
        self.info_bg.pos = instance.pos
        self.info_bg.size = instance.size
    
    def _update_slider_bg(self, instance, value):
        self.slider_bg.pos = instance.pos
        self.slider_bg.size = instance.size
    
    def get_tank_names(self):
        tank_list = calculo.get_tank_list()
        return [f"{t['name']}" for t in tank_list]
    
    def update_tank_spinner(self):
        self.tank_spinner.values = self.get_tank_names()
        current_tank = calculo._tanks.get(self.current_tank_id)
        if current_tank:
            self.tank_spinner.text = f"{current_tank['name']}"
    
    def on_tank_selected(self, spinner, text):
        # Encontrar el tank_id correspondiente
        for tank_id, tank in calculo._tanks.items():
            if tank['name'] == text:
                calculo.set_current_tank(tank_id)
                self.current_tank_id = tank_id
                self.on_tank_changed()
                break
    
    def on_tank_changed(self):
        tank = calculo._tanks.get(self.current_tank_id)
        if not tank:
            return
        
        # Actualizar info con animación
        self.tank_info_label.text = f"⌀{tank['D']:.1f}\" × L{tank['L']:.1f}\" • {len(tank['_training_heights'])} pts"
        
        # Actualizar slider
        self.height_slider.max = tank['D']
        self.height_slider.value = 0
        
        # Actualizar canvas
        self.tank_canvas.set_tank_dimensions(tank['D'], tank['L'])
        self.tank_canvas.set_height(0)
        
        # Actualizar volumen
        self.update_volume(0)
    
    def on_slider_change(self, slider, value):
        self.height_value_label.text = f'{value:.1f}"'
        self.height_input.text = f'{value:.1f}'
        self.tank_canvas.set_height(value)
        self.update_volume(value)
        
        # Actualizar porcentaje
        tank = calculo._tanks.get(self.current_tank_id)
        if tank:
            percent = min(100, (value / tank['D']) * 100)
            self.fill_percent_label.text = f'{percent:.0f}%'
    
    def on_height_input_change(self, instance, value):
        try:
            height = float(value) if value else 0.0
            tank = calculo._tanks.get(self.current_tank_id)
            if tank:
                # Limitar al máximo del tanque
                height = max(0, min(height, tank['D']))
                self.height_slider.value = height
        except ValueError:
            pass
    
    def update_volume(self, height):
        volume = calculo.galones_por_altura(height)
        
        # Animar cambio de volumen
        self.volume_label.text = f'{volume:.2f} gal'
    
    def show_add_tank_dialog(self, instance):
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Título mejorado
        title = Label(
            text='➕ Crear Nuevo Tanque',
            font_size='24sp',
            bold=True,
            color=GREEN_COLOR,
            size_hint_y=0.15
        )
        content.add_widget(title)
        
        # Subtítulo
        subtitle = Label(
            text='Ingresa las dimensiones del tanque cilíndrico horizontal',
            font_size='12sp',
            color=TEXT_GRAY,
            size_hint_y=0.1
        )
        content.add_widget(subtitle)
        
        # Campos con mejor diseño
        fields_layout = BoxLayout(orientation='vertical', spacing=12, size_hint_y=0.5)
        
        # Nombre
        name_label = Label(text='📝 Nombre:', font_size='13sp', size_hint_y=0.2, halign='left')
        name_label.bind(size=name_label.setter('text_size'))
        name_input = ModernTextInput(
            hint_text='Ej: Tanque Principal',
            multiline=False,
            size_hint_y=0.25,
            font_size='14sp',
            padding=[15, 15]
        )
        name_input.text = 'Tanque Nuevo'
        
        # Diámetro
        diameter_label = Label(text='⌀ Diámetro (pulgadas):', font_size='13sp', size_hint_y=0.2, halign='left')
        diameter_label.bind(size=diameter_label.setter('text_size'))
        diameter_input = ModernTextInput(
            hint_text='45.0',
            multiline=False,
            input_filter='float',
            size_hint_y=0.25,
            font_size='14sp',
            padding=[15, 15]
        )
        diameter_input.text = '45.0'
        
        # Longitud
        length_label = Label(text='📏 Longitud (pulgadas):', font_size='13sp', size_hint_y=0.2, halign='left')
        length_label.bind(size=length_label.setter('text_size'))
        length_input = ModernTextInput(
            hint_text='71.0',
            multiline=False,
            input_filter='float',
            size_hint_y=0.25,
            font_size='14sp',
            padding=[15, 15]
        )
        length_input.text = '71.0'
        
        fields_layout.add_widget(name_label)
        fields_layout.add_widget(name_input)
        fields_layout.add_widget(diameter_label)
        fields_layout.add_widget(diameter_input)
        fields_layout.add_widget(length_label)
        fields_layout.add_widget(length_input)
        
        content.add_widget(fields_layout)
        
        # Botones mejorados
        btn_layout = BoxLayout(size_hint_y=0.25, spacing=15)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.75),
            background_color=CARD_COLOR,
            separator_color=ACCENT_COLOR
        )
        
        def create_tank(btn):
            try:
                name = name_input.text.strip() or 'Tanque Nuevo'
                diameter = float(diameter_input.text)
                length = float(length_input.text)
                
                if diameter <= 0 or length <= 0:
                    self.show_error('Error', 'Las dimensiones deben ser positivas')
                    return
                
                tank_id = calculo.create_tank(name, diameter, length)
                calculo.set_current_tank(tank_id)
                self.current_tank_id = tank_id
                
                self.update_tank_spinner()
                self.on_tank_changed()
                
                popup.dismiss()
                self.show_info('✅ Éxito', f'Tanque "{name}" creado correctamente\n\n⌀ {diameter:.1f}" × 📏 {length:.1f}"')
            except ValueError as e:
                self.show_error('❌ Error', f'Valores inválidos:\n{str(e)}')
        
        save_btn = ModernButton(
            text='💾 CREAR TANQUE',
            btn_color=GREEN_COLOR,
            font_size='16sp',
            bold=True
        )
        save_btn.bind(on_press=create_tank)
        
        cancel_btn = ModernButton(
            text='✕ Cancelar',
            btn_color=RED_COLOR,
            font_size='15sp'
        )
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def show_calibrate_dialog(self, instance):
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        content.add_widget(Label(
            text='📊 Calibrar Tanque',
            font_size='22sp',
            bold=True,
            color=ACCENT_COLOR,
            size_hint_y=0.15
        ))
        
        content.add_widget(Label(
            text='Ingresa un par altura-galones para mejorar la precisión',
            font_size='12sp',
            color=TEXT_GRAY,
            size_hint_y=0.1
        ))
        
        # Campos
        fields_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.45)
        
        height_label = Label(text='📏 Altura (pulgadas):', font_size='13sp', size_hint_y=0.25, halign='left')
        height_label.bind(size=height_label.setter('text_size'))
        height_input = ModernTextInput(
            hint_text='Ej: 22.5',
            multiline=False,
            input_filter='float',
            size_hint_y=0.35,
            font_size='16sp',
            padding=[15, 15]
        )
        
        gallons_label = Label(text='⛽ Galones:', font_size='13sp', size_hint_y=0.25, halign='left')
        gallons_label.bind(size=gallons_label.setter('text_size'))
        gallons_input = ModernTextInput(
            hint_text='Ej: 150.0',
            multiline=False,
            input_filter='float',
            size_hint_y=0.35,
            font_size='16sp',
            padding=[15, 15]
        )
        
        fields_layout.add_widget(height_label)
        fields_layout.add_widget(height_input)
        fields_layout.add_widget(gallons_label)
        fields_layout.add_widget(gallons_input)
        content.add_widget(fields_layout)
        
        # Info actual
        tank = calculo._tanks.get(self.current_tank_id)
        info_text = f"Puntos actuales: {len(tank['_training_heights'])}"
        info_label = Label(
            text=info_text,
            font_size='11sp',
            color=TEXT_GRAY,
            size_hint_y=0.1
        )
        content.add_widget(info_label)
        
        # Botones
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=15)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.65),
            background_color=CARD_COLOR
        )
        
        def add_point(btn):
            try:
                h = float(height_input.text)
                g = float(gallons_input.text)
                
                if h < 0 or g < 0:
                    self.show_error('Error', 'Los valores deben ser positivos')
                    return
                
                calculo.append_training_points([h], [g])
                
                popup.dismiss()
                self.show_info('✅ Calibrado', f'Punto agregado:\n{h:.1f}" = {g:.2f} gal\n\nTotal puntos: {len(tank["_training_heights"]) + 1}')
                self.on_tank_changed()
            except ValueError:
                self.show_error('❌ Error', 'Valores inválidos')
        
        save_btn = ModernButton(
            text='✅ AGREGAR PUNTO',
            btn_color=GREEN_COLOR,
            font_size='16sp',
            bold=True
        )
        save_btn.bind(on_press=add_point)
        
        cancel_btn = ModernButton(
            text='✕ Cerrar',
            btn_color=(0.39, 0.45, 0.55, 1),
            font_size='15sp'
        )
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def show_load_csv_dialog(self, instance):
        self.show_info('ℹ️ Información', 'En Android:\nUsa el selector de archivos del sistema\n\nEn desarrollo:\nColoca el CSV en la carpeta de la app')
    
    def show_manage_tanks(self, instance):
        content = BoxLayout(orientation='vertical', spacing=12, padding=20)
        
        content.add_widget(Label(
            text='🔧 Gestión de Tanques',
            font_size='22sp',
            bold=True,
            color=TEXT_COLOR,
            size_hint_y=0.12
        ))
        
        # Lista de tanques con scroll
        scroll = ScrollView(size_hint_y=0.68)
        tank_list_layout = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, padding=[5, 5])
        tank_list_layout.bind(minimum_height=tank_list_layout.setter('height'))
        
        for tank_id, tank in calculo._tanks.items():
            tank_card = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=5)
            
            # Nombre y dimensiones
            info_line = Label(
                text=f"{tank['name']}",
                font_size='16sp',
                bold=True,
                color=TEXT_COLOR,
                halign='left'
            )
            info_line.bind(size=info_line.setter('text_size'))
            
            details_line = Label(
                text=f"⌀ {tank['D']:.1f}\" × 📏 {tank['L']:.1f}\" | 📊 {len(tank['_training_heights'])} puntos",
                font_size='12sp',
                color=TEXT_GRAY,
                halign='left'
            )
            details_line.bind(size=details_line.setter('text_size'))
            
            btn_box = BoxLayout(spacing=5, size_hint_y=0.5)
            
            # Botón seleccionar
            is_current = tank_id == self.current_tank_id
            select_btn = ModernButton(
                text='✓ ACTIVO' if is_current else 'Usar',
                btn_color=GREEN_COLOR if is_current else ACCENT_COLOR,
                font_size='12sp',
                size_hint_x=0.6
            )
            
            def switch_tank(btn, tid=tank_id):
                calculo.set_current_tank(tid)
                self.current_tank_id = tid
                self.update_tank_spinner()
                self.on_tank_changed()
                popup.dismiss()
                self.show_info('✅ Cambiado', f'Tanque activo:\n{calculo._tanks[tid]["name"]}')
            
            select_btn.bind(on_press=switch_tank)
            
            # Botón eliminar
            if tank_id != "default":
                def delete_tank(btn, tid=tank_id, tname=tank['name']):
                    self.confirm_delete_tank(tid, tname, popup)
                
                delete_btn = ModernButton(
                    text='🗑️',
                    btn_color=RED_COLOR,
                    font_size='14sp',
                    size_hint_x=0.4
                )
                delete_btn.bind(on_press=delete_tank)
                btn_box.add_widget(select_btn)
                btn_box.add_widget(delete_btn)
            else:
                btn_box.add_widget(select_btn)
            
            tank_card.add_widget(info_line)
            tank_card.add_widget(details_line)
            tank_card.add_widget(btn_box)
            
            # Separador
            sep = BoxLayout(size_hint_y=None, height=1)
            with sep.canvas:
                Color(0.2, 0.22, 0.3, 1)
                Rectangle(pos=sep.pos, size=sep.size)
            
            tank_list_layout.add_widget(tank_card)
            tank_list_layout.add_widget(sep)
        
        scroll.add_widget(tank_list_layout)
        content.add_widget(scroll)
        
        # Botón cerrar
        close_btn = ModernButton(
            text='✕ Cerrar',
            size_hint_y=0.2,
            btn_color=(0.39, 0.45, 0.55, 1),
            font_size='16sp'
        )
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.95, 0.85),
            background_color=CARD_COLOR
        )
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def confirm_delete_tank(self, tank_id, tank_name, parent_popup):
        """Diálogo de confirmación para eliminar tanque"""
        content = BoxLayout(orientation='vertical', spacing=20, padding=25)
        
        content.add_widget(Label(
            text='⚠️ Eliminar Tanque',
            font_size='20sp',
            bold=True,
            color=RED_COLOR,
            size_hint_y=0.25
        ))
        
        content.add_widget(Label(
            text=f'¿Estás seguro de eliminar:\n\n"{tank_name}"?\n\nEsta acción no se puede deshacer.',
            font_size='14sp',
            color=TEXT_COLOR,
            size_hint_y=0.5,
            halign='center'
        ))
        
        btn_layout = BoxLayout(size_hint_y=0.25, spacing=15)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.85, 0.45),
            background_color=CARD_COLOR
        )
        
        def do_delete(btn):
            try:
                calculo.delete_tank(tank_id)
                self.update_tank_spinner()
                self.on_tank_changed()
                popup.dismiss()
                parent_popup.dismiss()
                self.show_info('✅ Eliminado', f'Tanque "{tank_name}" eliminado')
            except Exception as e:
                self.show_error('Error', str(e))
        
        delete_btn = ModernButton(
            text='🗑️ ELIMINAR',
            btn_color=RED_COLOR,
            font_size='15sp',
            bold=True
        )
        delete_btn.bind(on_press=do_delete)
        
        cancel_btn = ModernButton(
            text='Cancelar',
            btn_color=(0.39, 0.45, 0.55, 1),
            font_size='15sp'
        )
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def show_info(self, title, message):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=title,
            font_size='20sp',
            bold=True,
            color=ACCENT_COLOR,
            size_hint_y=0.25
        ))
        
        content.add_widget(Label(
            text=message,
            font_size='14sp',
            color=TEXT_COLOR,
            size_hint_y=0.5,
            halign='center'
        ))
        
        btn = ModernButton(
            text='OK',
            size_hint_y=0.25,
            btn_color=ACCENT_COLOR,
            font_size='16sp'
        )
        content.add_widget(btn)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.4),
            background_color=CARD_COLOR
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_error(self, title, message):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=title,
            font_size='20sp',
            bold=True,
            color=RED_COLOR,
            size_hint_y=0.25
        ))
        
        content.add_widget(Label(
            text=message,
            font_size='14sp',
            color=TEXT_COLOR,
            size_hint_y=0.5,
            halign='center'
        ))
        
        btn = ModernButton(
            text='OK',
            size_hint_y=0.25,
            btn_color=RED_COLOR,
            font_size='16sp'
        )
        content.add_widget(btn)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.4),
            background_color=CARD_COLOR
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    Window.clearcolor = BG_COLOR
    TankApp().run()
