# 🚀 ADMIN PANEL - Gurnama Görkezmeleri

## Ädim-be-ädim Setup

### 1️⃣ Faýllary Göçür
```bash
unzip Admin-Panel.zip -d /var/www/admin
# ýa-da isleýän directory-ňize
```

### 2️⃣ Browser-da Açyň

#### Ýönekeý usul:
```
index.html faýlyny iki gezek basyň
Chrome/Firefox/Safari açylar
```

#### Server bilen (optional):
```bash
# Python
cd admin
python -m http.server 8080

# Node.js
npx serve

# PHP
php -S localhost:8080
```

Soňra: `http://localhost:8080`

### 3️⃣ Backend Birikdirmek

**admin-script.js** faýlynda:
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

Backend işleýän bolmaly:
```bash
cd backend
python app.py
```

### 4️⃣ Test Etmek

1. Dashboard açyň → Stats görkeziler
2. Diller → "Täze dil goş" → Ýatda sakla
3. Sapaklar → Täze sapak döret
4. Maşklar → Täze maşk döret

## 🔧 Configuration

### API URL üýtgetmek
```javascript
// Development
const API_BASE_URL = 'http://localhost:5000';

// Production
const API_BASE_URL = 'https://api.example.com';
```

### Colors üýtgetmek
**admin-styles.css**:
```css
:root {
    --primary-color: #6366f1;  /* Isleýän reňk */
    --secondary-color: #8b5cf6;
}
```

## 📱 Production Deployment

### 1. Static hosting (Netlify, Vercel)
```bash
# Build directory: admin/
# Publish: index.html
```

### 2. Docker
```dockerfile
FROM nginx:alpine
COPY admin/ /usr/share/nginx/html
```

### 3. Backend bilen birlikde
```
backend/
├── app.py
├── admin/
│   ├── index.html
│   ├── admin-styles.css
│   └── admin-script.js
```

Flask-da serve:
```python
@app.route('/admin')
def admin():
    return send_file('admin/index.html')
```

## ✅ Checklist

- [ ] Faýllar göçürildi
- [ ] Browser-da açyldy
- [ ] Backend işleýär
- [ ] API URL dogry
- [ ] Test işleri geçirildi
- [ ] Production-a deploy edildi

## 🎉 Taýýar!

Admin panel işlemäge taýýar! 🚀
