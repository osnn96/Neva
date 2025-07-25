<?php
require_once 'Auth.php';

class User {
    private $conn;
    private $auth;
    
    public function __construct($db) {
        $this->conn = $db;
        $this->auth = new Auth($db);
    }
    
    public function getProfile($token) {
        try {
            $user = $this->auth->validateToken($token);
            if (!$user) {
                return ['success' => false, 'message' => 'Geçersiz token'];
            }
            // Kullanıcı detaylarını getir
            $query = "SELECT id, first_name, last_name, email, birth_date, gender, created_at 
                     FROM users WHERE id = :user_id AND is_active = 1";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':user_id', $user['id']);
            $stmt->execute();
            if ($stmt->rowCount() === 0) {
                return ['success' => false, 'message' => 'Kullanıcı bulunamadı'];
            }
            $profile = $stmt->fetch();
            // Tarih formatını düzenle
            if ($profile['birth_date']) {
                $date = DateTime::createFromFormat('Y-m-d', $profile['birth_date']);
                $profile['birth_date_formatted'] = $date ? $date->format('d.m.Y') : null;
            }
            // Hassas bilgileri kaldır
            unset($profile['id']);
            return [
                'success' => true,
                'profile' => $profile
            ];
        } catch (Exception $e) {
            return ['success' => false, 'message' => 'Sunucu hatası: ' . $e->getMessage()];
        }
    }

    public function updateProfile($token, $data) {
        try {
            $user = $this->auth->validateToken($token);
            if (!$user) {
                return ['success' => false, 'message' => 'Geçersiz token'];
            }
            $updateFields = [];
            $params = [':user_id' => $user['id']];
            // Güncellenebilir alanlar
            $allowedFields = ['first_name', 'last_name', 'birth_date', 'gender'];
            foreach ($allowedFields as $field) {
                if (isset($data[$field])) {
                    if ($field === 'birth_date') {
                        // Tarih format kontrolü
                        $birth_date = DateTime::createFromFormat('d.m.Y', $data[$field]);
                        if (!$birth_date) {
                            return ['success' => false, 'message' => 'Geçersiz tarih formatı (dd.mm.yyyy)'];
                        }
                        $updateFields[] = "$field = :$field";
                        $params[":$field"] = $birth_date->format('Y-m-d');
                    } else {
                        $updateFields[] = "$field = :$field";
                        $params[":$field"] = $data[$field];
                    }
                }
            }
            if (empty($updateFields)) {
                return ['success' => false, 'message' => 'Güncellenecek alan bulunamadı'];
            }
            $query = "UPDATE users SET " . implode(', ', $updateFields) . " WHERE id = :user_id";
            $stmt = $this->conn->prepare($query);
            if ($stmt->execute($params)) {
                return ['success' => true, 'message' => 'Profil başarıyla güncellendi'];
            } else {
                return ['success' => false, 'message' => 'Profil güncellenirken hata oluştu'];
            }
        } catch (Exception $e) {
            return ['success' => false, 'message' => 'Sunucu hatası: ' . $e->getMessage()];
        }
    }
}