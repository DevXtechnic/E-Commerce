class SearchIndex:
    def __init__(self):
        self.entries = []

    def build(self):
        from .models import Product, Brand, Category

        self.entries = []

        for p in Product.objects.filter(is_active=True).select_related("category", "brand"):
            score = 15 if p.is_featured else 10
            self._add(p.name, "product", p.get_absolute_url(), score, p.category.name)

        for b in Brand.objects.all():
            self._add(b.name, "brand", f"/products/?brand={b.slug}", 5)

        for c in Category.objects.all():
            self._add(c.name, "category", c.get_absolute_url(), 5)

    def _add(self, text, type_, url, score, category=None):
        self.entries.append({
            "text": text,
            "text_lower": text.lower(),
            "type": type_,
            "url": url,
            "score": score,
            "category": category,
        })

    def search(self, query, limit=8):
        q = query.lower().strip()
        if len(q) < 2:
            return []

        matches = []
        for entry in self.entries:
            if q in entry["text_lower"]:
                matches.append(entry)

        matches.sort(key=lambda x: (-x["score"], x["text"]))
        return matches[:limit]

    def search_by_category(self, query, limit_per_cat=5, total_limit=20):
        q = query.lower().strip()
        if len(q) < 2:
            return []

        cat_groups = {}
        for e in self.entries:
            if e["type"] == "product" and q in e["text_lower"]:
                cat = e.get("category") or "Other"
                cat_groups.setdefault(cat, []).append(e)

        sorted_cats = sorted(cat_groups.items(), key=lambda x: -len(x[1]))
        results = []
        for cat, products in sorted_cats:
            results.append({"category_header": cat})
            results.extend(products[:limit_per_cat])

        return results[:total_limit]

    def add_entry(self, text, type_, url, score=10, category=None):
        self.entries.append({
            "text": text,
            "text_lower": text.lower(),
            "type": type_,
            "url": url,
            "score": score,
            "category": category,
        })

    def remove_entry(self, text, type_):
        text_lower = text.lower()
        self.entries = [
            e for e in self.entries
            if not (e["text_lower"] == text_lower and e["type"] == type_)
        ]


search_index = SearchIndex()
