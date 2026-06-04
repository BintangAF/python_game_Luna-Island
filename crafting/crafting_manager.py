from inventories.inventory import Inventory
from items.item import Item
class CraftingManager:
    
    def __init__(self):
        self.recipes = {
            'Ramuan': {
                'bahan': {'Rumput': 3, 'Bunga': 2},
                'desc': 'Membuat ramuan dari rumput dan bunga',
                'image': 'assets/images/items/water.png',  # Gambar hasil
            },
            'Roti': {
                'bahan': {'Gandum': 2, 'Telur': 1},
                'desc': 'Memanggang roti dari gandum dan telur',
                'image': 'assets/images/items/bread.png',
            },
            'Pedang Kayu': {
                'bahan': {'Kayu': 5, 'Batu': 3},
                'desc': 'Pedang sederhana untuk bertahan',
                'image': 'assets/images/items/wooden_sword.png',

            },
            'Beliung': {
                'bahan': {'Kayu': 5, 'Besi': 2},
                'desc': 'Beliung sederhana untuk menambang',
                'image': 'assets/images/items/pickaxe.png',
                
            },
            'Obat Herbal': {
                'bahan': {'Herba': 4, 'Air': 2},
                'desc': 'Obat penyembuh yang kuat',
                'image': 'assets/images/items/herbal_medicine.png',
                
            },
            'Pancing': {
                'bahan': {'Kayu': 3, 'Tali': 2, 'Besi': 1},
                'desc': 'Pancing untuk memancing ikan',
                'image': 'assets/images/items/fishing_rod.png',
              
            },
        }
    
    def get_recipe_image(self, item_name):
        """Dapatkan gambar untuk item hasil crafting"""
        recipe = self.recipes.get(item_name, {})
        return recipe.get('image', None)

    def get_bahan_image(self, item_name, bahan_name):
        """Dapatkan gambar untuk bahan tertentu"""
        recipe = self.recipes.get(item_name, {})
        bahan_images = recipe.get('bahan_images', {})
        return bahan_images.get(bahan_name, None)
    
    def can_craft(self, inventory: Inventory, item_name: str):
        """Cek apakah bahan mencukupi untuk crafting"""
        if item_name not in self.recipes:
            return False, "Resep tidak ditemukan"
        
        recipe = self.recipes[item_name]
        bahan_kurang = []
        for bahan, jumlah in recipe['bahan'].items():
            if not inventory.has_item(bahan, jumlah):
                stok = inventory.get_item_count(bahan)
                bahan_kurang.append(f"{bahan} (butuh {jumlah}, punya {stok})")
        
        if bahan_kurang:
            return False, f"Kurang: {', '.join(bahan_kurang)}"
        
        return True, "Bahan mencukupi"
        
    def craft(self, inventory: Inventory, item_name: str):
        """Lakukan crafting, kurangi bahan dan tambah hasil"""
        can, message = self.can_craft(inventory, item_name)
        if not can:
            return False, message
        
        recipe = self.recipes[item_name]
        
        # Kurangi bahan
        for bahan, jumlah in recipe['bahan'].items():
            inventory.remove_item(bahan, jumlah)
        
        # Tambah hasil (create item object)
        result_item = self._create_item_object(item_name)
        if result_item:
            inventory.add_item(result_item)
        
        return True, f"Berhasil membuat {item_name}!"
    
    def _create_item_object(self, item_name: str) -> Item:
        """Buat object Item berdasarkan nama item hasil crafting"""
        from items.weapon import Weapon
        from items.food_item import FoodItem
        from items.material_item import MaterialItem
        
        if item_name == "Pedang Kayu":
            return Weapon("Pedang Kayu", damage=15, durability=50, icon_path="assets/images/items/wooden_sword.png")
        elif item_name == "Ramuan":
            return FoodItem("Ramuan", energy_restore=30, buy_price=20, sell_price=10, icon_path="assets/images/items/potion.png")
        elif item_name == "Roti":
            return FoodItem("Roti", energy_restore=20, buy_price=15, sell_price=8, icon_path="assets/images/items/bread.png")
        # ... tambahkan lainnya
        
        return MaterialItem(item_name, 0, 0, None)
        
    def get_recipe_info(self, item_name):
        """Dapatkan info resep"""
        if item_name in self.recipes:
            recipe = self.recipes[item_name]
            bahan_list = ', '.join([f"{bahan} x{jumlah}" for bahan, jumlah in recipe['bahan'].items()])
            return f"{recipe['desc']}\nBahan: {bahan_list}"
        return "Resep tidak ditemukan"
    
