
class CraftingManager:
    
    def __init__(self):
        self.recipes = {
            'Ramuan': {
                'bahan': {'Rumput': 3, 'Bunga': 2},
                'desc': 'Membuat ramuan dari rumput dan bunga (beli rumput & bunga di pedagang)'
            },
            'Roti': {
                'bahan': {'Gandum': 2, 'Telur': 1},
                'desc': 'Memanggang roti dari gandum dan telur (beli gandum & telur di pedagang ramuan)'
            },
            'Pedang Kayu': {
                'bahan': {'Kayu': 5, 'Batu': 3},
                'desc': 'Pedang sederhana untuk bertahan (beli kayu & batu di pedagang tanaman)'
            },
            'Beliung': {
                'bahan': {'Kayu': 5, 'Besi': 2},
                'desc': 'Beliung sederhana untuk menambang (beli kayu & besi di pedagang tanaman)'
            },
            'Jala Ikan': {
                'bahan': {'Tali': 3, 'Kayu': 4},
                'desc': 'Alat untuk menangkap ikan (beli tali & kayu di pedagang tanaman)'
            },
            'Obat Herbal': {
                'bahan': {'Herba': 4, 'Air': 2},
                'desc': 'Obat penyembuh yang kuat (beli herba & air di pedagang ramuan)'
            },
            'Pancing': {
                'bahan': {'Kayu': 3, 'Tali': 2, 'Besi': 1},
                'desc': 'Pancing untuk memancing ikan (beli kayu, tali, besi dari pedagang)'
            },
        }
        
    def can_craft(self, inventory, item_name):
        if item_name not in self.recipes:
            return False, "Resep tidak ditemukan"
        
        recipe = self.recipes[item_name]
        bahan_kurang = []
        for bahan, jumlah in recipe['bahan'].items():
            if inventory.get(bahan, 0) < jumlah:
                bahan_kurang.append(f"{bahan} (butuh {jumlah}, punya {inventory.get(bahan, 0)})")
        
        if bahan_kurang:
            return False, f"Kurang: {', '.join(bahan_kurang)}"
        
        return True, "Bahan mencukupi"
    
    def craft(self, inventory, item_name):
        can, message = self.can_craft(inventory, item_name)
        if not can:
            return False, message
        
        recipe = self.recipes[item_name]
        
        for bahan, jumlah in recipe['bahan'].items():
            inventory[bahan] -= jumlah
            if inventory[bahan] <= 0:
                del inventory[bahan]
        inventory[item_name] = inventory.get(item_name, 0) + 1
        
        return True, f"Berhasil membuat {item_name}!"
    
    def get_recipe_info(self, item_name):
        """Dapatkan info resep"""
        if item_name in self.recipes:
            recipe = self.recipes[item_name]
            bahan_list = ', '.join([f"{bahan} x{jumlah}" for bahan, jumlah in recipe['bahan'].items()])
            return f"{recipe['desc']}\nBahan: {bahan_list}"
        return "Resep tidak ditemukan"
    