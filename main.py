from kivy.storage.jsonstore import JsonStore
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 20

    MDLabel:
        text: "Gold Price Calculator"
        halign: "center"
        font_style: "H4"

    MDRaisedButton:
        text: "Set Gold Price per Gram"
        pos_hint: {"center_x": 0.5}
        on_release: app.show_set_price_dialog()

    MDCard:
        orientation: 'vertical'
        padding: 20
        size_hint: None, None
        size: "300dp", "400dp"
        pos_hint: {"center_x": 0.5}

        MDLabel:
            text: "Weight in Grams:"
            halign: "left"
        MDTextField:
            id: weight_input
            hint_text: "Enter weight"

        MDLabel:
            text: "Making Charge (%):"
            halign: "left"
        MDTextField:
            id: making_charge_input
            hint_text: "Enter making charge"

        MDRaisedButton:
            text: "Calculate Price"
            pos_hint: {"center_x": 0.5}
            on_release: app.calculate_price()

        MDLabel:
            id: result_label
            halign: "center"
            theme_text_color: "Secondary"
'''

class GoldPriceApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('gold_price.json')
        self.gold_price = self.store.get('price')['value'] if self.store.exists('price') else None
        self.dialog = None

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        if self.gold_price is None:
            self.show_set_price_dialog()

    def show_set_price_dialog(self, *args):
        # Dialog to set or update gold price
        if not self.dialog:
            self.dialog = MDDialog(
                title="Set Gold Price per Gram",
                type="custom",
                content_cls=MDTextField(
                    hint_text="Enter gold price per gram",
                    text=str(self.gold_price) if self.gold_price else ""
                ),
                buttons=[
                    MDFlatButton(text="CANCEL", on_release=self.close_dialog),
                    MDFlatButton(text="SAVE", on_release=self.save_gold_price),
                ],
            )
        self.dialog.content_cls.text = str(self.gold_price) if self.gold_price else ""
        self.dialog.open()

    def close_dialog(self, *args):
        self.dialog.dismiss()

    def save_gold_price(self, *args):
        try:
            gold_price_input = self.dialog.content_cls.text
            self.gold_price = float(gold_price_input)
            self.store.put('price', value=self.gold_price)
            self.close_dialog()
        except ValueError:
            self.dialog.content_cls.helper_text = "Please enter a valid number"
            self.dialog.content_cls.helper_text_mode = "on_error"

    def calculate_price(self):
        try:
            weight = float(self.root.ids.weight_input.text)
            making_charge_percent = float(self.root.ids.making_charge_input.text)

            # Calculate gold price based on weight
            gold_price = self.gold_price * weight

            # Calculate making charges
            making_charge = gold_price * (making_charge_percent / 100)

            # Subtotal before GST
            subtotal = gold_price + making_charge

            # GST of 3% on subtotal
            gst = subtotal * 0.03

            # Final price after adding GST
            total_price = subtotal + gst

            # Display the result
            self.root.ids.result_label.text = f'Total Price: ₹{total_price:.2f} (incl. GST)'

        except ValueError:
            self.root.ids.result_label.text = "Please enter valid numbers!"

GoldPriceApp().run()
