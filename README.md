<h1 align="center">
 🕹️⋆˚࿔ Projek UAS  Pemrograman Berorientasi Objek
</h1>

<div align="center">
<h2>Nama Project: Game pixel berjudul Monster Island</h2>

![Kelompok](https://img.shields.io/badge/Kelompok-2-1E3A8A?style=for-the-badge)
![Kelas](https://img.shields.io/badge/Kelas-TIC%202025-1E3A8A?style=for-the-badge)



</div>

---

## ⚔⊹ ࣪ ˖ Deskripsi Project
<div align="justify">

Game ini merupakan game pixel art dengan tema survival dan farming.
Pada awal game MC akan spawn di sebuah pulau kosong dan bertemu
dengan NPC. Saat awal NPC akan memberikan tutorial menanam tanaman
yang akan digunakan dalam mode bertempur, menambang di gua untuk
mendapatkan item dan membeli benih untuk ditanam.
MC dapat menanam biji yang didapat dari NPC ataupun yang
didapatkan dari gua atau saat selesai mode pertempuran. MC wajib menyiram
tanaman agar tanaman dapat tumbuh dan digunakan untuk mode
pertempuran. Ada sistem cuaca yang dapat mempengaruhi tanaman dan
tanaman dapat bermutasi.
MC bisa menentukan waktu bertempurnya, jika MC melewatkan satu
hari tampa mode bertempur maka akan game over. Mode bertempur seperti
Plant VS Zombie. MC menggunakan tanaman yang didapatkan dari farming
untuk mode bertempur. MC juga bisa menambang dan mendapatkan item
secara acak di salahsatu gua.
</div>
---

## ᯤ⁹⁹⁹⁺ Anggota Kelompok

| No | Nama | NIM |
|----|------|-----|
| 1 | **Dhika Karya Prasetya** | 25051204086 | 
| 2 | **Bintang Atsal Faros** | 25051204139 | 
| 3 | **Febriana Regina Artanti** | 25051204148 |
| 4 | **Maulana dwi febrian arajak** | 25051204186 | 


---

## ִ🎮🎧 Fitur Utamaִֶָ

- Spawn
- Jual beli benih di NPC
- Menanam tanaman
- Battle mode
- Mining
- Iventory
  
---


## ᯓ★ Cara Menjalankan Program
1. Download Zip dari github
3. Ekstrak semua file zip
4. Download pygame ika anda belum mendownload library tersebut
5. Download library pytmx jika anda belum mendownload library tersebut
6. Jalankan main kode di teks editor anda


---

## 👾 Penjelasan implementasi OOP ˖ ݁𖥔 ݁˖
<div align ="justify">
 <ul>
<li><b>Encapsulation :</b> : Setiap objek dalam game direpresentasikan sebagai class yang memiliki atribut dan method masing-masing. Contohnya: Player menyimpan data <i>inventory</i>, <i>plant</i> menyimpan informasi tumbuhan tanaman, monster menyimpan atribut <i>damage</i> dan HP, <i>inventory</i> menyimpan kumpulan item yang dimiliki pemain</li>
<li><b>Inheritance :</b> Dalam game ada beberapa class yang mewarisi class lain seperti: Player dan NPC mewarisi <i>Character</i>, <i>sedds</i>, <i>food item</i>, dan <i>tools</i> mewarisi class item, slime dan zommbie mewarisi class monster</li>
<li><b>Polymorphism :</b> Polymorphism diterapkan melalui pewarisan class. Contohnya: Method use() pada class Item dapat memiliki implementasi berbeda pada <i>Seed</i>, <i>FoodItem</i>, dan <i>Tool.</i> Method attack() pada class Monster dapat dijalankan berbeda oleh Slime maupun Zombie. </li>
<li><b>Abstraction :</b>  Abstraksi diterapkan dengan memisahkan sistem game menjadi beberapa komponen utama, antara lain: Sistem karakter (Character, Player, NPC), Sistem item (Item, Seed, FoodItem, Tool), Sistem pertanian (Farm, Plant), Sistem pertarungan (Monster, Slime, Zombie),  Sistem <i>world</i> (Map, Cave, DaySystem, WeatherSystem)</li>
</ul>
 </div>
 
---
## ⚔️ Screenshot tampilan program

