import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from news_pocked import NewsPocked
import queue
import time
import json

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

        # Alt kısım için frame
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Sol taraf (Bulunan Haberler)
        left_frame = ttk.Frame(bottom_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bulunan Haberler frame'i
        news_list_frame = ttk.LabelFrame(left_frame, text="Bulunan Haberler", padding="5")
        news_list_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        # Renk açıklamaları frame'i
        color_info_frame = ttk.Frame(news_list_frame)
        color_info_frame.pack(fill=tk.X, padx=5, pady=2)

        # Renk açıklamaları
        colors = [
            ("🟩 Yeşil", "light green", "Başarıyla paylaşıldı"),
            ("🟧 Turuncu", "orange", "Rate limit bekliyor"),
            ("🟥 Kırmızı", "light coral", "Paylaşılamadı"),
            ("⬜ Gri", "#f0f0f0", "Henüz paylaşılmadı")
        ]

        for i, (text, color, desc) in enumerate(colors):
            frame = ttk.Frame(color_info_frame)
            frame.pack(side=tk.LEFT, padx=10)
            
            # Renk örneği
            color_sample = tk.Label(frame, text="   ", bg=color, relief="solid")
            color_sample.pack(side=tk.LEFT, padx=2)
            
            # Açıklama
            ttk.Label(frame, text=f"{text}: {desc}").pack(side=tk.LEFT)

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

        # Sağ taraf (Paylaşılan Haberler)
        right_frame = ttk.Frame(bottom_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Paylaşılan Haberler frame'i
        shared_news_frame = ttk.LabelFrame(right_frame, text="Paylaşılan Haberler", padding="5")
        shared_news_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        # Paylaşılan haberler listesi
        self.shared_news_listbox = tk.Listbox(shared_news_frame)
        self.shared_news_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Paylaşılan haberler scrollbar
        shared_scrollbar = ttk.Scrollbar(shared_news_frame, orient=tk.VERTICAL, command=self.shared_news_listbox.yview)
        shared_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.shared_news_listbox.configure(yscrollcommand=shared_scrollbar.set)

        # Log alanı
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # İlerleme çubuğu frame'i
        self.progress_frame = ttk.LabelFrame(self.root, text="Paylaşım Durumu", padding="5")
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
        self.progress_frame.pack_forget()  # Başlangıçta gizli

        # İlerleme çubuğu
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

        # İlerleme durumu etiketi
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(pady=5)

        # Paylaşılan haberleri yükle
        self.load_shared_news()

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
        
        # Paylaşılmış haberlerin URL'lerini al
        try:
            with open('posted_news.json', 'r') as f:
                posted_urls = json.load(f)
        except FileNotFoundError:
            posted_urls = []
        
        for site_name, site_info in self.news_pocked.news_sites.items():
            self.log_queue.put(f"{site_name} sitesinden haberler getiriliyor...")
            
            news_items = self.news_pocked.scrape_news(site_info['url'], site_info)
            
            for news in news_items:
                # Daha önce paylaşılmamış haberleri ekle
                if news['link'] not in posted_urls:
                    self.current_news_items.append(news)
                    self.news_listbox.insert(tk.END, f"[{site_name}] {news['title']}")
                    if len(self.current_news_items) % 2 == 0:
                        self.news_listbox.itemconfig(tk.END, {'bg': '#f0f0f0'})
        
        if self.current_news_items:
            self.share_button.config(state=tk.NORMAL)
            self.log_queue.put(f"Toplam {len(self.current_news_items)} yeni haber getirildi.")
        else:
            self.log_queue.put("Hiç yeni haber bulunamadı.")

    def share_selected_news(self):
        """Seçili haberleri Twitter'da paylaşır"""
        selected_indices = self.news_listbox.curselection()
        
        if not selected_indices:
            self.log_queue.put("Lütfen paylaşılacak haberleri seçin.")
            return
        
        # Maksimum 10 haber seçilebilir
        if len(selected_indices) > 10:
            self.log_queue.put("En fazla 10 haber seçebilirsiniz!")
            return
        
        # Paylaşım onayı al
        selected_news = [self.current_news_items[i]['title'] for i in selected_indices]
        message = f"Seçilen {len(selected_news)} haberi paylaşmak istediğinize emin misiniz?\n\n"
        message += "\n".join(f"- {title}" for title in selected_news)
        
        if not messagebox.askyesno("Paylaşım Onayı", message):
            self.log_queue.put("Paylaşım iptal edildi.")
            return

        # Paylaşım işlemini ayrı bir thread'de başlat
        sharing_thread = threading.Thread(
            target=self._share_news_thread,
            args=(selected_indices,),
            daemon=True
        )
        sharing_thread.start()

    def _countdown_timer(self, sleep_time):
        """Rate limit geri sayımını yönetir"""
        def countdown_thread():
            remaining = sleep_time
            while remaining > 0:
                minutes = remaining // 60
                seconds = remaining % 60
                countdown_str = f"{minutes:02d}:{seconds:02d}"
                
                # GUI güncellemelerini ana thread'e gönder
                self.root.after(0, lambda t=countdown_str: self._update_countdown_gui(t, sleep_time, remaining))
                
                time.sleep(1)
                remaining -= 1
            
            # Geri sayım tamamlandığında
            self.root.after(0, self._countdown_finished)
        
        # Geri sayımı ayrı thread'de başlat
        threading.Thread(target=countdown_thread, daemon=True).start()

    def _update_countdown_gui(self, time_str, total_time, remaining):
        """Geri sayım GUI'sini günceller"""
        self.log_queue.put(f"⏳ Rate limit geri sayım: {time_str}")
        self.progress_label.config(text=f"Rate limit bekleniyor... {time_str}")
        self.progress_var.set(((total_time - remaining) / total_time) * 100)
        self.root.update()

    def _countdown_finished(self):
        """Geri sayım tamamlandığında çağrılır"""
        self.log_queue.put("✓ Rate limit süresi doldu. Tekrar deneyebilirsiniz.")
        self.share_button.config(state=tk.NORMAL)
        self.fetch_button.config(state=tk.NORMAL)
        self.progress_frame.pack_forget()
        self.root.update()

    def _handle_rate_limit(self, error_str, index):
        """Rate limit hatasını yönetir"""
        try:
            sleep_time = int(error_str.split('Sleeping for ')[1].split(' seconds')[0])
            minutes = sleep_time // 60
            seconds = sleep_time % 60
            time_str = f"{minutes} dakika {seconds} saniye" if minutes > 0 else f"{seconds} saniye"
            
            warning = (
                f"Twitter paylaşım limiti aşıldı!\n\n"
                f"Bekleme süresi: {time_str}\n\n"
                "Twitter'ın paylaşım limitleri:\n"
                "- 15 dakikada maksimum 300 tweet\n"
                "- Her tweet için 1 medya\n\n"
                "Geri sayım başlıyor, lütfen bekleyin..."
            )
            
            # GUI güncellemelerini ana thread'de yap
            self.log_queue.put(f"⚠ Rate limit nedeniyle işlem duraklatıldı. ({time_str} bekleniyor)")
            messagebox.showwarning("Rate Limit Aşıldı", warning)
            self.news_listbox.itemconfig(index, {'bg': 'orange'})
            
            # Butonları devre dışı bırak
            self.share_button.config(state=tk.DISABLED)
            self.fetch_button.config(state=tk.DISABLED)
            
            # İlerleme çubuğunu göster
            self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
            self.root.update()
            
            # Geri sayımı başlat
            self._countdown_timer(sleep_time)
            
        except Exception as parse_error:
            self.log_queue.put(f"⚠ Rate limit süresi alınamadı: {str(parse_error)}")

    def _share_news_thread(self, selected_indices):
        """Haber paylaşım işlemini ayrı thread'de yürütür"""
        # İlerleme çubuğunu göster
        self.root.after(0, lambda: self.progress_frame.pack(fill=tk.X, padx=10, pady=5))
        self.root.after(0, lambda: self.share_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.fetch_button.config(state=tk.DISABLED))
        
        # Log alanını temizle
        self.root.after(0, lambda: self.log_text.delete(1.0, tk.END))
        self.log_queue.put("Paylaşım işlemi başlatılıyor...")
        
        total_news = len(selected_indices)
        
        try:
            for i, index in enumerate(selected_indices, 1):
                news = self.current_news_items[index]
                
                # İlerleme durumunu güncelle
                progress = (i / total_news) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
                current_news = f"Paylaşılıyor ({i}/{total_news}): {news['title']}"
                self.root.after(0, lambda msg=current_news: self.progress_label.config(text=msg))
                self.log_queue.put(current_news)
                
                try:
                    result = self.news_pocked.post_to_twitter(news)
                    if result:
                        success_msg = f"✓ Haber paylaşıldı: {news['title']}"
                        self.log_queue.put(success_msg)
                        self.root.after(0, lambda idx=index: self.news_listbox.itemconfig(idx, {'bg': 'light green'}))
                        
                        # Paylaşılan haberi listeye ekle
                        self.root.after(0, lambda t=news['title']: self.shared_news_listbox.insert(0, f"✓ {t}"))
                        
                        # Başarılı paylaşımı listeden kaldır (5 saniye sonra)
                        self.root.after(5000, lambda idx=index: self.remove_shared_news(idx))
                    else:
                        error_msg = f"✗ Haber paylaşılamadı: {news['title']}"
                        self.log_queue.put(error_msg)
                        self.root.after(0, lambda idx=index: self.news_listbox.itemconfig(idx, {'bg': 'light coral'}))
                
                except Exception as e:
                    error_str = str(e)
                    self.log_queue.put(f"⚠ Hata yakalandı: {error_str}")
                    
                    if "Rate limit exceeded" in error_str:
                        self._handle_rate_limit(error_str, index)
                        return
                    else:
                        self.log_queue.put(f"✗ Hata: {error_str}")
                        self.root.after(0, lambda idx=index: self.news_listbox.itemconfig(idx, {'bg': 'light coral'}))
                
                # Her paylaşım arasında 5 saniye bekle
                if i < total_news:
                    for j in range(5, 0, -1):
                        wait_msg = f"⏳ Sonraki paylaşım için bekleniyor... {j} saniye"
                        self.root.after(0, lambda msg=wait_msg: self.progress_label.config(text=msg))
                        self.log_queue.put(wait_msg)
                        time.sleep(1)
        
        finally:
            # İşlem bittiğinde temizlik yap
            self.root.after(0, lambda: self.progress_frame.pack_forget())
            self.root.after(0, lambda: self.share_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.fetch_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress_label.config(text=""))
            self.root.after(0, lambda: self.progress_var.set(0))
            self.log_queue.put("✓ İşlem tamamlandı.")

    def update_log(self):
        """Log mesajlarını günceller"""
        try:
            while True:  # Tüm mesajları işle
                message = self.log_queue.get_nowait()
                current_time = time.strftime("%H:%M:%S")
                formatted_message = f"[{current_time}] {message}"
                self.log_text.insert(tk.END, formatted_message + "\n")
                self.log_text.see(tk.END)  # Otomatik kaydır
                self.root.update()  # Arayüzü hemen güncelle
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.update_log)  # Her 100ms'de bir kontrol et

    def load_shared_news(self):
        """Paylaşılan haberleri listeler"""
        self.shared_news_listbox.delete(0, tk.END)
        try:
            with open('posted_news.json', 'r') as f:
                posted_news = json.load(f)
                for url in posted_news:
                    # URL'den başlığı bul
                    for news in self.current_news_items:
                        if news['link'] == url:
                            self.shared_news_listbox.insert(0, f"✓ {news['title']}")
                            break
        except FileNotFoundError:
            pass

    def remove_shared_news(self, index):
        """Paylaşılan haberi listeden kaldırır"""
        try:
            self.news_listbox.delete(index)
            # current_news_items listesinden de kaldır
            self.current_news_items.pop(index)
        except:
            pass

# Ana çalıştırma kodu
if __name__ == "__main__":
    root = tk.Tk()
    app = NewsPockedGUI(root)
    root.mainloop() 