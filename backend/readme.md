# Chat App API Dokümantasyonu

## Genel Bilgiler

**Base URL:** `http://aiproje.guryeli.com/`
**Postman:** `postmanV2.json içeri aktarın`
**Content-Type:** `application/json`
**Authentication:** Bearer Token (Header: `Authorization: Bearer {token}`)

---

## Authentication Endpoints

### 1. Kullanıcı Kaydı
**POST** `/api/auth/register`

**İstek Body:**
```json
{
    "first_name": "Ahmet",
    "last_name": "Yılmaz", 
    "email": "ahmet@example.com",
    "password": "123456",
    "password_confirm": "123456",
    "birth_date": "15.08.1990",
    "gender": "male",
    "terms_accepted": true,
    "privacy_accepted": true
}
```

**Başarılı Yanıt:**
```json
{
    "success": true,
    "message": "Hesap başarıyla oluşturuldu"
}
```

### 2. Giriş Yapma
**POST** `/api/auth/login`

**İstek Body:**
```json
{
    "email": "ahmet@example.com",
    "password": "123456"
}
```

**Başarılı Yanıt:**
```json
{
    "success": true,
    "message": "Giriş başarılı",
    "token": "abc123def456...",
    "user": {
        "id": 1,
        "email": "ahmet@example.com",
        "first_name": "Ahmet",
        "last_name": "Yılmaz"
    }
}
```

### 3. Çıkış Yapma
**POST** `/api/auth/logout`
**Headers:** `Authorization: Bearer {token}`

**Başarılı Yanıt:**
```json
{
    "success": true,
    "message": "Çıkış yapıldı"
}
```

### 4. Şifre Sıfırlama Talebi
**POST** `/api/auth/forgot-password`

**İstek Body:**
```json
{
    "email": "ahmet@example.com"
}
```

**Başarılı Yanıt:**
```json
{
    "success": true,
    "message": "Şifre sıfırlama bağlantısı email adresinize gönderildi",
    "reset_token": "reset123token456"
}
```

### 5. Şifre Sıfırlama
**POST** `/api/auth/reset-password`

**İstek Body:**
```json
{
    "token": "reset123token456",
    "password": "yenisifre123",
    "password_confirm": "yenisifre123"
}
```

---

## User Endpoints

### 1. Profil Bilgilerini Getirme
**GET** `/api/user/profile`
**Headers:** `Authorization: Bearer {token}`

**Başarılı Yanıt:**
```json
{
    "success": true,
    "profile": {
        "first_name": "Ahmet",
        "last_name": "Yılmaz",
        "email": "ahmet@example.com",
        "birth_date": "1990-08-15",
        "birth_date_formatted": "15.08.1990",
        "gender": "male",
        "created_at": "2024-01-15 10:30:00"
    }
}
```

### 2. Profil Güncelleme
**PUT** `/api/user/profile`
**Headers:** `Authorization: Bearer {token}`

**İstek Body:**
```json
{
    "first_name": "Mehmet",
    "last_name": "Özkan",
    "birth_date": "20.05.1988",
    "gender": "male"
}
```

---