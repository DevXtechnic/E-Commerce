from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "full_name", "email", "phone", "address",
            "city", "state", "zipcode", "payment_method", "notes",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})

        self.fields["notes"].widget = forms.Textarea(
            attrs={"class": "form-input", "rows": 3, "placeholder": "Any special instructions..."}
        )

        if user and user.is_authenticated:
            self.fields["full_name"].initial = user.get_full_name()
            self.fields["email"].initial = user.email
            default_address = user.addresses.filter(is_default=True).first()
            if default_address:
                self.fields["phone"].initial = default_address.phone
                self.fields["address"].initial = default_address.street
                self.fields["city"].initial = default_address.city
                self.fields["state"].initial = default_address.state
                self.fields["zipcode"].initial = default_address.zipcode
