"""Seed script — run with: python manage.py shell < seed_data.py"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ecommerce.settings")
django.setup()

from django.contrib.auth.models import User
from shop.models import Category, Brand, Product, ProductImage, Review
from mystore.models import FAQ, SiteSettings

# ── Superuser ──
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@devxtechnic.com", "admin")
    print("✓ Superuser created (admin/admin)")

# ── Categories ──
cats = {}
for i, name in enumerate(["Laptops", "Smartphones", "Accessories", "Audio", "Gaming", "Networking"]):
    c, _ = Category.objects.get_or_create(name=name, defaults={"order": i})
    cats[name] = c
print(f"✓ {len(cats)} categories")

# ── Brands ──
brands = {}
for name in ["Apple", "Samsung", "Dell", "HP", "Sony", "Razer", "Logitech", "Xiaomi"]:
    b, _ = Brand.objects.get_or_create(name=name)
    brands[name] = b
print(f"✓ {len(brands)} brands")

# ── Products ──
products_data = [
    {"name":"MacBook Air M3","category":"Laptops","brand":"Apple","price":189999,"discount_price":179999,"stock":15,"is_featured":True,
     "description":"The thinnest, lightest laptop with the blazing-fast M3 chip. All-day battery life, stunning Liquid Retina display, and fanless design.",
     "specifications":"Processor: Apple M3\nRAM: 16GB Unified\nStorage: 512GB SSD\nDisplay: 13.6\" Liquid Retina\nBattery: Up to 18 hours\nWeight: 1.24 kg"},
    {"name":"Samsung Galaxy S25 Ultra","category":"Smartphones","brand":"Samsung","price":164999,"discount_price":None,"stock":20,"is_featured":True,
     "description":"The ultimate Galaxy experience. Titanium frame, S Pen built-in, 200MP camera, and Galaxy AI features.",
     "specifications":"Display: 6.8\" Dynamic AMOLED 2X\nProcessor: Snapdragon 8 Gen 4\nRAM: 12GB\nStorage: 256GB\nCamera: 200MP + 50MP + 10MP + 12MP\nBattery: 5000mAh"},
    {"name":"Dell XPS 15","category":"Laptops","brand":"Dell","price":175999,"discount_price":159999,"stock":8,"is_featured":True,
     "description":"Stunning InfinityEdge display in a compact design. Perfect for creators and professionals.",
     "specifications":"Processor: Intel Core i7-13700H\nRAM: 16GB DDR5\nStorage: 512GB NVMe SSD\nDisplay: 15.6\" OLED 3.5K\nGPU: NVIDIA RTX 4050\nWeight: 1.86 kg"},
    {"name":"AirPods Pro 3","category":"Audio","brand":"Apple","price":34999,"discount_price":31999,"stock":50,"is_featured":True,
     "description":"Active Noise Cancellation, Adaptive Transparency, and Personalized Spatial Audio with head tracking.",
     "specifications":"Driver: Custom high-excursion\nANC: Active Noise Cancellation\nBattery: 6 hours (30 with case)\nConnectivity: Bluetooth 5.3\nWater Resistance: IPX4"},
    {"name":"Razer DeathAdder V3","category":"Gaming","brand":"Razer","price":8999,"discount_price":7499,"stock":30,"is_featured":False,
     "description":"Ultra-lightweight ergonomic esports mouse. Focus Pro 30K sensor with 90-hour battery.",
     "specifications":"Sensor: Razer Focus Pro 30K\nSwitches: Optical Gen-3\nWeight: 63g\nBattery: 90 hours\nPolling Rate: 4000Hz\nGrip: Ergonomic"},
    {"name":"Sony WH-1000XM6","category":"Audio","brand":"Sony","price":44999,"discount_price":39999,"stock":25,"is_featured":True,
     "description":"Industry-leading noise cancellation with exceptional sound quality. 40-hour battery.",
     "specifications":"Driver: 40mm\nANC: Adaptive\nBattery: 40 hours\nCodecs: LDAC, AAC, SBC\nWeight: 252g\nFolding: Yes"},
    {"name":"Xiaomi Pad 7 Pro","category":"Accessories","brand":"Xiaomi","price":42999,"discount_price":38999,"stock":12,"is_featured":False,
     "description":"Premium tablet with a brilliant 11.2\" 144Hz display, Snapdragon 8s Gen 3 processor and massive battery.",
     "specifications":"Display: 11.2\" IPS 144Hz\nProcessor: Snapdragon 8s Gen 3\nRAM: 8GB\nStorage: 256GB\nBattery: 10000mAh\nCharging: 67W"},
    {"name":"Logitech MX Mechanical","category":"Accessories","brand":"Logitech","price":19999,"discount_price":17999,"stock":18,"is_featured":False,
     "description":"Wireless mechanical keyboard with smart backlighting and multi-device connectivity.",
     "specifications":"Switches: Tactile Quiet\nBacklight: Smart Illumination\nBattery: Up to 15 months\nConnectivity: Bluetooth + USB Receiver\nLayout: Full Size"},
    {"name":"HP Pavilion Gaming Desktop","category":"Gaming","brand":"HP","price":125999,"discount_price":109999,"stock":5,"is_featured":True,
     "description":"Powerful gaming desktop with RTX 4060. Handles the latest AAA titles with ease.",
     "specifications":"Processor: AMD Ryzen 7 7700X\nGPU: NVIDIA RTX 4060 8GB\nRAM: 16GB DDR5\nStorage: 1TB NVMe SSD\nPSU: 500W\nOS: Windows 11"},
    {"name":"Samsung T7 Shield SSD 2TB","category":"Accessories","brand":"Samsung","price":16999,"discount_price":14999,"stock":40,"is_featured":False,
     "description":"Portable SSD with rugged design. IP65 rated, USB 3.2 Gen 2 speeds up to 1,050MB/s.",
     "specifications":"Capacity: 2TB\nInterface: USB 3.2 Gen 2\nRead Speed: 1050 MB/s\nWrite Speed: 1000 MB/s\nDurability: IP65, 3m Drop\nWeight: 98g"},
    {"name":"iPhone 16 Pro Max","category":"Smartphones","brand":"Apple","price":199999,"discount_price":194999,"stock":10,"is_featured":True,
     "description":"The most advanced iPhone ever. A18 Pro chip, 48MP Fusion camera, titanium design, and all-day battery life.",
     "specifications":"Display: 6.9\" Super Retina XDR OLED\nChip: A18 Pro\nRAM: 8GB\nStorage: 256GB\nCamera: 48MP Fusion + 48MP Ultra Wide + 12MP Telephoto\nBattery: Up to 33 hours video"},
    {"name":"Xiaomi Smart Band 9","category":"Accessories","brand":"Xiaomi","price":3999,"discount_price":3499,"stock":100,"is_featured":False,
     "description":"1.62\" AMOLED display, 150+ sport modes, SpO2 monitoring, and up to 21 days battery life.",
     "specifications":"Display: 1.62\" AMOLED\nBattery: 21 days\nWater Resistance: 5ATM\nSensors: Heart Rate, SpO2, Accelerometer\nWeight: 15.8g"},
]

for pd in products_data:
    cat = cats[pd.pop("category")]
    brand = brands[pd.pop("brand")]
    p, created = Product.objects.get_or_create(
        name=pd["name"],
        defaults={**pd, "category": cat, "brand": brand}
    )
    if created:
        print(f"  + {p.name}")

print(f"✓ {Product.objects.count()} products total")

# ── FAQs ──
faqs = [
    ("Do you deliver outside Kathmandu?", "Yes! We deliver nationwide across Nepal. Delivery inside Kathmandu Valley is free, and nominal charges apply for other locations."),
    ("What payment methods do you accept?", "We currently accept Cash on Delivery (COD), eSewa, Khalti, and Bank Transfer."),
    ("Do your products come with warranty?", "All products sold on DevXtechnic come with the manufacturer's official warranty. Extended warranty options are available on select products."),
    ("Can I return a product?", "Yes, we offer a 7-day return policy for unused and undamaged products in original packaging. Please contact us within 7 days of delivery."),
    ("How long does delivery take?", "Orders inside Kathmandu Valley are delivered within 1-2 business days. For other locations, delivery takes 3-7 business days."),
]
for i, (q, a) in enumerate(faqs):
    FAQ.objects.get_or_create(question=q, defaults={"answer": a, "order": i})
print(f"✓ {FAQ.objects.count()} FAQs")

# ── Site Settings ──
SiteSettings.objects.get_or_create(
    site_name="DevXtechnic",
    defaults={
        "tagline": "Premium Tech, Nepali Pride",
        "about_text": "Nepal's trusted destination for premium tech products.",
        "phone": "+977-1-XXXXXXX",
        "email": "hello@devxtechnic.com",
        "address": "Kathmandu, Nepal",
    }
)
print("✓ Site settings created")
print("\n🎉 Seed complete! Login: admin / admin")
