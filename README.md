# NewsPocked - Haber Takip ve Paylaşım Sistemi

NewsPocked, haber sitelerinden haberleri otomatik olarak takip eden ve X Twitter'da paylaşmanıza olanak sağlayan bir Python uygulamasıdır.

## Özellikler

- Haber sitelerinden otomatik haber çekme
- Çoklu haber sitesi desteği
- Özelleştirilebilir CSS seçiciler
- Twitter'da manuel haber paylaşımı
- Kullanıcı dostu arayüz
- Haber önizleme ve seçme
- Log sistemi

## Kurulum

1. Gerekli kütüphaneleri yükleyin: 

```bash
pip install requests beautifulsoup4 tweepy python-dotenv`
```

2. Projeyi klonlayın:

```bash
git clone https://github.com/yourusername/NewsPocket.git
```

3. `.env` dosyası oluşturun ve Twitter API bilgilerinizi ekleyin:

```bash
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=
```


## Kullanım

1. Programı başlatın:

```bash
python main.py
```


2. Haber sitesi eklemek için:
   - Site adı girin
   - URL'yi girin
   - CSS seçicileri belirleyin (başlık, görsel ve link için)
   - "Site Ekle" butonuna tıklayın

3. Haberleri getirmek için:
   - "Haberleri Getir" butonuna tıklayın
   - Getirilen haberler listede görünecektir

4. Haber paylaşmak için:
   - Listeden paylaşmak istediğiniz haberleri seçin
   - "Seçili Haberleri Paylaş" butonuna tıklayın
   - Onay verdikten sonra haberler Twitter'da paylaşılacaktır

## CSS Seçici Örnekleri

Hürriyet için örnek seçiciler

```python
{
'title_selector': '.categorylist_item h2',
'image_selector': '.categorylist_item--cover img',
'link_selector': '.categorylist_item a[data-tag="h2"]'
}
```

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

