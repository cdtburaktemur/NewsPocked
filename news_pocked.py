import os
import time
import requests
from bs4 import BeautifulSoup
import tweepy
from datetime import datetime
from dotenv import load_dotenv
import json
from urllib.parse import urljoin

class NewsPocked:
    def __init__(self):
        # .env dosyasından Twitter API kimlik bilgilerini yükle
        load_dotenv()
        
        # Twitter API kimlik bilgileri
        self.api_key = os.getenv('TWITTER_CLIENT_ID')
        self.api_secret = os.getenv('TWITTER_CLIENT_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Twitter API client'ını başlat
        self.twitter_client = self._init_twitter()
        
        # Haber sitelerini yükle
        self.news_sites = self._load_news_sites()
        
        # Paylaşılan haberleri yükle
        self.posted_news = self._load_posted_news()

    def _init_twitter(self):
        """Twitter API v2 istemcisini başlatır"""
        try:
            # API anahtarlarını kontrol et
            if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                print("Twitter API anahtarları eksik!")
                return None

            # Twitter API v2 client'ı oluştur
            client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Medya yüklemek için v1.1 auth
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret
            )
            self.api_v1 = tweepy.API(auth)
            
            return client
        except Exception as e:
            print(f"Twitter API bağlantısı başarısız: {str(e)}")
            return None

    def _load_posted_news(self):
        """Daha önce paylaşılan haberleri yükler"""
        try:
            with open('posted_news.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _save_posted_news(self):
        """Paylaşılan haberleri kaydeder"""
        with open('posted_news.json', 'w') as f:
            json.dump(self.posted_news, f)

    def _load_news_sites(self):
        """Kayıtlı haber sitelerini yükler"""
        try:
            with open('news_sites.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Varsayılan siteleri döndür
            default_sites = {
                'hurriyet.com.tr': {
                    'url': 'https://www.hurriyet.com.tr/gundem/',
                    'title_selector': '.category__list__item h2',
                    'image_selector': '.category__list__item--cover img',
                    'link_selector': '.category__list__item a[data-tag="h2"]',
                    'card_selector': '.category__list__item'
                },
                'sozcu.com.tr': {
                    'url': 'https://www.sozcu.com.tr/kategori/gundem/',
                    'title_selector': '.d-block.fs-5.fw-semibold',
                    'image_selector': 'img[loading="lazy"]',
                    'link_selector': '.col-md-6.col-lg-4.mb-4 > a',
                    'card_selector': '.col-md-6.col-lg-4.mb-4'
                }
            }
            # Varsayılan siteleri kaydet
            self._save_news_sites(default_sites)
            return default_sites

    def _save_news_sites(self, sites=None):
        """Haber sitelerini kaydeder"""
        if sites is None:
            sites = self.news_sites
        with open('news_sites.json', 'w', encoding='utf-8') as f:
            json.dump(sites, f, ensure_ascii=False, indent=4)

    def add_news_site(self, name, url, selectors):
        """Yeni haber sitesi ekler"""
        self.news_sites[name] = {
            'url': url,
            'title_selector': selectors['title_selector'],
            'image_selector': selectors['image_selector'],
            'link_selector': selectors['link_selector'],
            'card_selector': selectors['card_selector']
        }
        self._save_news_sites()

    def remove_news_site(self, name):
        """Haber sitesini kaldırır"""
        if name in self.news_sites:
            del self.news_sites[name]
            self._save_news_sites()

    def scrape_news(self, site_url, selectors):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr,en-US;q=0.7,en;q=0.3',
            }
            response = requests.get(site_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            
            # Haber kartlarını seç
            news_cards = soup.select(selectors['card_selector'])
            print(f"Bulunan haber kartı sayısı: {len(news_cards)}")
            
            for card in news_cards:
                try:
                    title_elem = card.select_one(selectors['title_selector'])
                    image_elem = card.select_one(selectors['image_selector'])
                    link_elem = card.select_one(selectors['link_selector'])
                    
                    if title_elem and image_elem and link_elem:
                        title = title_elem.text.strip()
                        image_src = image_elem.get('src') or image_elem.get('data-src')
                        link_href = link_elem.get('href')
                        
                        # Link'i tam URL'ye çevir
                        if not link_href.startswith('http'):
                            link_href = urljoin(site_url, link_href)
                        
                        if title and image_src and link_href:
                            news_items.append({
                                'title': title,
                                'image': image_src,
                                'link': link_href
                            })
                            print(f"Haber başarıyla eklendi: {title}")
                except Exception as e:
                    print(f"Haber işlenirken hata: {str(e)}")
                    continue
            
            return news_items
        except Exception as e:
            print(f"Hata: {site_url} sitesinden haberler çekilirken bir sorun oluştu: {str(e)}")
            return []

    def post_to_twitter(self, news):
        """Haberi Twitter'da paylaşır"""
        try:
            # Twitter client'ı kontrol et
            if not self.twitter_client:
                raise Exception("Twitter client başlatılamadı!")
            
            # Haber daha önce paylaşılmış mı kontrol et
            if news['link'] in self.posted_news:
                return False
            
            # Görseli indir
            image_response = requests.get(news['image'])
            with open('temp_image.jpg', 'wb') as f:
                f.write(image_response.content)
            
            try:
                # Görseli yükle (v1.1 API ile)
                media = self.api_v1.media_upload('temp_image.jpg')
                
                # Tweet metni oluştur (280 karakter sınırı)
                title = news['title'][:200] if len(news['title']) > 200 else news['title']
                tweet_text = f"{title}\n\n{news['link']}"
                
                # Tweet'i paylaş (v2 API ile)
                self.twitter_client.create_tweet(
                    text=tweet_text,
                    media_ids=[media.media_id]
                )
                
                # Paylaşılan haberi kaydet
                self.posted_news.append(news['link'])
                self._save_posted_news()
                
                return True
                
            except tweepy.errors.TooManyRequests as e:
                # Rate limit hatasını özel bir formatta ilet
                reset_time = int(e.response.headers.get('x-rate-limit-reset', 0))
                current_time = int(time.time())
                sleep_time = reset_time - current_time
                raise Exception(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                
            except Exception as e:
                raise Exception(f"Tweet paylaşılırken hata: {str(e)}")
                
            finally:
                # Geçici görseli sil
                if os.path.exists('temp_image.jpg'):
                    os.remove('temp_image.jpg')
                
        except Exception as e:
            # Tüm hataları yukarı ilet
            raise e

    def run(self):
        """Ana program döngüsü"""
        while True:
            for site_name, site_info in self.news_sites.items():
                print(f"{site_name} sitesinden haberler kontrol ediliyor...")
                
                news_items = self.scrape_news(site_info['url'], site_info)
                
                for news in news_items:
                    if self.post_to_twitter(news):
                        print(f"Haber paylaşıldı: {news['title']}")
                        # Her haber paylaşımı arasında 5 dakika bekle
                        time.sleep(300)
            
            # Tüm siteleri kontrol ettikten sonra 15 dakika bekle
            print("Tüm siteler kontrol edildi. 15 dakika bekleniyor...")
            time.sleep(900)

if __name__ == "__main__":
    news_pocked = NewsPocked()
    news_pocked.run() 