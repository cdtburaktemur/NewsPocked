import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from news_pocked import NewsPocked
import queue
import time

class NewsPockedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NewsPocked - Haber Takip Sistemi")
        self.root.geometry("800x600")
        
        # Log mesajları için queue
        self.log_queue = queue.Queue()
        
        # NewsPocked instance
        self.news_pocked = NewsPocked()
        
        # Çalışma durumu
        self.is_running = False
        
        self.current_news_items = []  # Bulunan haberleri saklamak için liste
        
        self.create_widgets()
        self.update_log()

    def create_widgets(self):
        # Üst frame (Site ekleme kısmı)
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        # Site ekleme alanı
        site_frame = ttk.LabelFrame(top_frame, text="Haber Sitesi Ekle", padding="5")
        site_frame.pack(fill=tk.X, pady=5)

        # Site adı
        ttk.Label(site_frame, text="Site Adı:").grid(row=0, column=0, padx=5)
        self.site_name = ttk.Entry(site_frame)
        self.site_name.grid(row=0, column=1, padx=5)

        # URL
        ttk.Label(site_frame, text="URL:").grid(row=0, column=2, padx=5)
        self.site_url = ttk.Entry(site_frame, width=40)
        self.site_url.grid(row=0, column=3, padx=5)

        # Seçiciler frame
        selectors_frame = ttk.Frame(site_frame)
        selectors_frame.grid(row=1, column=0, columnspan=4, pady=5)

        # Başlık seçici
        ttk.Label(selectors_frame, text="Başlık Seçici:").grid(row=0, column=0, padx=5)
        self.title_selector = ttk.Entry(selectors_frame)
        self.title_selector.grid(row=0, column=1, padx=5)

        # Görsel seçici
        ttk.Label(selectors_frame, text="Görsel Seçici:").grid(row=0, column=2, padx=5)
        self.image_selector = ttk.Entry(selectors_frame)
        self.image_selector.grid(row=0, column=3, padx=5)

        # Link seçici
        ttk.Label(selectors_frame, text="Link Seçici:").grid(row=0, column=4, padx=5)
        self.link_selector = ttk.Entry(selectors_frame)
        self.link_selector.grid(row=0, column=5, padx=5)

        # Site ekle butonu
        ttk.Button(site_frame, text="Site Ekle", command=self.add_site).grid(row=2, column=0, columnspan=4, pady=5)

        # Mevcut siteler listesi
        sites_frame = ttk.LabelFrame(self.root, text="Takip Edilen Siteler", padding="5")
        sites_frame.pack(fill=tk.X, padx=10, pady=5)

        self.sites_text = scrolledtext.ScrolledText(sites_frame, height=5)
        self.sites_text.pack(fill=tk.X)
        self.update_sites_list()

        # Kontrol butonları
        control_frame = ttk.Frame(self.root, padding="5")
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Haberleri Getir butonu
        self.fetch_button = ttk.Button(control_frame, text="Haberleri Getir", command=self.fetch_news)
        self.fetch_button.pack(side=tk.LEFT, padx=5)

        # Haberler listesi frame'i
        news_list_frame = ttk.LabelFrame(self.root, text="Bulunan Haberler", padding="5")
        news_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Haberler listesi
        self.news_listbox = tk.Listbox(news_list_frame, selectmode=tk.MULTIPLE)
        self.news_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(news_list_frame, orient=tk.VERTICAL, command=self.news_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.news_listbox.configure(yscrollcommand=scrollbar.set)

        # Paylaş butonu
        self.share_button = ttk.Button(news_list_frame, text="Seçili Haberleri Paylaş", 
                                     command=self.share_selected_news, state=tk.DISABLED)
        self.share_button.pack(pady=5)

        # Log alanı
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def add_site(self):
        name = self.site_name.get()
        url = self.site_url.get()
        title_sel = self.title_selector.get()
        image_sel = self.image_selector.get()
        link_sel = self.link_selector.get()

        if name and url and title_sel and image_sel and link_sel:
            # Önce test edelim
            try:
                self.log_queue.put(f"Site test ediliyor: {name}")
                test_news = self.news_pocked.scrape_news(url, {
                    'title_selector': title_sel,
                    'image_selector': image_sel,
                    'link_selector': link_sel
                })
                
                if test_news:
                    # Test başarılı, siteyi ekle
                    self.news_pocked.news_sites[name] = {
                        'url': url,
                        'title_selector': title_sel,
                        'image_selector': image_sel,
                        'link_selector': link_sel
                    }
                    self.update_sites_list()
                    self.log_queue.put(f"Site başarıyla eklendi: {name}")
                    self.log_queue.put(f"Bulunan ilk haber: {test_news[0]['title']}")
                    
                    # Input alanlarını temizle
                    self.site_name.delete(0, tk.END)
                    self.site_url.delete(0, tk.END)
                    self.title_selector.delete(0, tk.END)
                    self.image_selector.delete(0, tk.END)
                    self.link_selector.delete(0, tk.END)
                else:
                    self.log_queue.put("Hata: Seçicilerle hiç haber bulunamadı!")
                    
            except Exception as e:
                self.log_queue.put(f"Hata: Site eklenirken bir sorun oluştu: {str(e)}")

    def update_sites_list(self):
        self.sites_text.delete(1.0, tk.END)
        for site, info in self.news_pocked.news_sites.items():
            self.sites_text.insert(tk.END, f"Site: {site}\nURL: {info['url']}\n\n")

    def fetch_news(self):
        """Seçili sitelerden haberleri getirir"""
        self.news_listbox.delete(0, tk.END)  # Listeyi temizle
        self.current_news_items = []  # Haberleri temizle
        
        for site_name, site_info in self.news_pocked.news_sites.items():
            self.log_queue.put(f"{site_name} sitesinden haberler getiriliyor...")
            
            news_items = self.news_pocked.scrape_news(site_info['url'], site_info)
            
            for news in news_items:
                self.current_news_items.append(news)
                # Haberleri daha belirgin göster
                self.news_listbox.insert(tk.END, f"[{site_name}] {news['title']}")
                # Her haberi farklı renkte göster
                if len(self.current_news_items) % 2 == 0:
                    self.news_listbox.itemconfig(tk.END, {'bg': '#f0f0f0'})
        
        if self.current_news_items:
            self.share_button.config(state=tk.NORMAL)
            self.log_queue.put(f"Toplam {len(self.current_news_items)} haber getirildi.")
        else:
            self.log_queue.put("Hiç haber bulunamadı.")

    def share_selected_news(self):
        """Seçili haberleri Twitter'da paylaşır"""
        selected_indices = self.news_listbox.curselection()
        
        if not selected_indices:
            self.log_queue.put("Lütfen paylaşılacak haberleri seçin.")
            return
        
        # Paylaşım onayı al
        selected_news = [self.current_news_items[i]['title'] for i in selected_indices]
        message = "Aşağıdaki haberleri paylaşmak istediğinize emin misiniz?\n\n"
        message += "\n".join(f"- {title}" for title in selected_news)
        
        if not messagebox.askyesno("Paylaşım Onayı", message):
            self.log_queue.put("Paylaşım iptal edildi.")
            return
        
        for index in selected_indices:
            news = self.current_news_items[index]
            if self.news_pocked.post_to_twitter(news):
                self.log_queue.put(f"Haber paylaşıldı: {news['title']}")
                # Paylaşılan haberi listede işaretle
                self.news_listbox.itemconfig(index, {'bg': 'light green'})
            else:
                self.log_queue.put(f"Haber paylaşılamadı: {news['title']}")
                self.news_listbox.itemconfig(index, {'bg': 'light coral'})

    def update_log(self):
        while True:
            try:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
            except queue.Empty:
                break
        self.root.after(100, self.update_log)

# Ana çalıştırma kodu
if __name__ == "__main__":
    root = tk.Tk()
    app = NewsPockedGUI(root)
    root.mainloop() 