<?php
require_once 'src/Exception.php';
require_once 'src/PHPMailer.php';
require_once 'src/SMTP.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

class Auth
{
    private $conn;

    public function __construct($db)
    {
        $this->conn = $db;
    }

    public function register($data)
    {
        try {
            // Veri doğrulama
            $required_fields = ['first_name', 'last_name', 'email', 'password', 'password_confirm', 'birth_date', 'terms_accepted', 'privacy_accepted'];

            foreach ($required_fields as $field) {
                if (!isset($data[$field]) || empty($data[$field])) {
                    return ['success' => false, 'message' => "Gerekli alan eksik: $field"];
                }
            }

            // Şifre doğrulama
            if ($data['password'] !== $data['password_confirm']) {
                return ['success' => false, 'message' => 'Şifreler eşleşmiyor'];
            }

            // Şifre güçlülük kontrolü
            if (strlen($data['password']) < 6) {
                return ['success' => false, 'message' => 'Şifre en az 6 karakter olmalıdır'];
            }

            // Email format kontrolü
            if (!filter_var($data['email'], FILTER_VALIDATE_EMAIL)) {
                return ['success' => false, 'message' => 'Geçersiz email formatı'];
            }

            // Tarih format kontrolü
            $birth_date = DateTime::createFromFormat('d.m.Y', $data['birth_date']);
            if (!$birth_date) {
                return ['success' => false, 'message' => 'Geçersiz tarih formatı (dd.mm.yyyy)'];
            }

            // Kullanım koşulları kontrolü
            if (!$data['terms_accepted'] || !$data['privacy_accepted']) {
                return ['success' => false, 'message' => 'Kullanım koşulları ve gizlilik politikası kabul edilmelidir'];
            }

            // Email benzersizlik kontrolü
            $check_email = "SELECT id FROM users WHERE email = :email";
            $stmt = $this->conn->prepare($check_email);
            $stmt->bindParam(':email', $data['email']);
            $stmt->execute();

            if ($stmt->rowCount() > 0) {
                return ['success' => false, 'message' => 'Bu email adresi zaten kullanılıyor'];
            }

            // Kullanıcı kaydetme
            $query = "INSERT INTO users (first_name, last_name, email, password_hash, birth_date, gender, terms_accepted, privacy_accepted) 
                     VALUES (:first_name, :last_name, :email, :password_hash, :birth_date, :gender, :terms_accepted, :privacy_accepted)";

            $stmt = $this->conn->prepare($query);

            $password_hash = password_hash($data['password'], PASSWORD_BCRYPT);
            $formatted_date = $birth_date->format('Y-m-d');
            $gender = isset($data['gender']) ? $data['gender'] : null;

            $stmt->bindParam(':first_name', $data['first_name']);
            $stmt->bindParam(':last_name', $data['last_name']);
            $stmt->bindParam(':email', $data['email']);
            $stmt->bindParam(':password_hash', $password_hash);
            $stmt->bindParam(':birth_date', $formatted_date);
            $stmt->bindParam(':gender', $gender);
            $stmt->bindParam(':terms_accepted', $data['terms_accepted'], PDO::PARAM_BOOL);
            $stmt->bindParam(':privacy_accepted', $data['privacy_accepted'], PDO::PARAM_BOOL);

            if ($stmt->execute()) {
                return ['success' => true, 'message' => 'Hesap başarıyla oluşturuldu'];
            } else {
                return ['success' => false, 'message' => 'Hesap oluşturulurken hata oluştu'];
            }
        } catch (Exception $e) {
            return ['success' => false, 'message' => 'Sunucu hatası: ' . $e->getMessage()];
        }
    }

    public function login($data)
    {
        try {
            if (!isset($data['email']) || !isset($data['password'])) {
                return ['success' => false, 'message' => 'Email ve şifre gereklidir'];
            }

            // Kullanıcı kontrolü
            $query = "SELECT id, email, password_hash, first_name, last_name FROM users WHERE email = :email AND is_active = 1";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':email', $data['email']);
            $stmt->execute();

            if ($stmt->rowCount() === 0) {
                return ['success' => false, 'message' => 'Geçersiz email veya şifre'];
            }

            $user = $stmt->fetch();

            // Şifre kontrolü
            if (!password_verify($data['password'], $user['password_hash'])) {
                return ['success' => false, 'message' => 'Geçersiz email veya şifre'];
            }

            // Token oluşturma
            $token = $this->generateToken();
            $expires_at = date('Y-m-d H:i:s', strtotime('+30 days'));

            // Eski tokenları deaktif et
            $deactivate_query = "UPDATE user_tokens SET is_active = 0 WHERE user_id = :user_id";
            $stmt = $this->conn->prepare($deactivate_query);
            $stmt->bindParam(':user_id', $user['id']);
            $stmt->execute();

            // Yeni token kaydet
            $token_query = "INSERT INTO user_tokens (user_id, token, expires_at) VALUES (:user_id, :token, :expires_at)";
            $stmt = $this->conn->prepare($token_query);
            $stmt->bindParam(':user_id', $user['id']);
            $stmt->bindParam(':token', $token);
            $stmt->bindParam(':expires_at', $expires_at);
            $stmt->execute();

            return [
                'success' => true,
                'message' => 'Giriş başarılı',
                'token' => $token,
                'user' => [
                    'id' => $user['id'],
                    'email' => $user['email'],
                    'first_name' => $user['first_name'],
                    'last_name' => $user['last_name']
                ]
            ];
        } catch (Exception $e) {
            return ['success' => false, 'message' => 'Sunucu hatası: ' . $e->getMessage()];
        }
    }

    public function logout($token)
    {
        try {
            if (!$token) {
                return ['success' => false, 'message' => 'Token gereklidir'];
            }

            $query = "UPDATE user_tokens SET is_active = 0 WHERE token = :token";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':token', $token);
            $stmt->execute();

            return ['success' => true, 'message' => 'Çıkış yapıldı'];
        } catch (Exception $e) {
            return ['success' => false, 'message' => 'Sunucu hatası: ' . $e->getMessage()];
        }
    }

    public function forgotPassword($data)
    {
        try {
            if (!isset($data['email'])) {
                return ['success' => false, 'message' => 'Email gereklidir'];
            }

            // Kullanıcı kontrolü
            $query = "SELECT id, email FROM users WHERE email = :email AND is_active = 1";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':email', $data['email']);
            $stmt->execute();

            if ($stmt->rowCount() === 0) {
                return ['success' => false, 'message' => 'Bu email adresi ile kayıtlı kullanıcı bulunamadı'];
            }

            $user = $stmt->fetch();

            // Reset token oluştur
            $reset_token = $this->generateToken();
            $expires_at = date('Y-m-d H:i:s', strtotime('+1 hour'));

            // Eski reset tokenları deaktif et
            $deactivate_query = "UPDATE password_reset_tokens SET is_used = 1 WHERE user_id = :user_id";
            $stmt = $this->conn->prepare($deactivate_query);
            $stmt->bindParam(':user_id', $user['id']);
            $stmt->execute();

            // Yeni reset token kaydet
            $token_query = "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (:user_id, :token, :expires_at)";
            $stmt = $this->conn->prepare($token_query);
            $stmt->bindParam(':user_id', $user['id']);
            $stmt->bindParam(':token', $reset_token);
            $stmt->bindParam(':expires_at', $expires_at);
            $stmt->execute();


            $shost = "";
            $sport = 587;
            $suser = "";
            $spass = "";
            $ssite = "";
            $ssender = "";

            defined("SMTP_HOST") or define("SMTP_HOST", "$shost");
            defined("SMTP_PORT") or define("SMTP_PORT", $sport);
            defined("SMTP_USER") or define("SMTP_USER", "$suser");
            defined("SMTP_PASS") or define("SMTP_PASS", "$spass");

            $this->mailSmtp($user['email'], 'Şifre Sıfırlama', 'Reset token: ' . $reset_token, "", "", $ssite, $suser, $ssender);

            return [
                'success' => true,
                'message' => 'Şifre sıfırlama bağlantısı email adresinize gönderildi',
                'reset_token' => $reset_token // Test için, production'da kaldırılmalı
            ];
        } catch (Exception $e) {
            return ['success' => false, 'message' => 'Sunucu hatası: ' . $e->getMessage()];
        }
    }

    public function resetPassword($data)
    {
        try {
            if (!isset($data['token']) || !isset($data['password']) || !isset($data['password_confirm'])) {
                return ['success' => false, 'message' => 'Token ve şifreler gereklidir'];
            }

            if ($data['password'] !== $data['password_confirm']) {
                return ['success' => false, 'message' => 'Şifreler eşleşmiyor'];
            }

            if (strlen($data['password']) < 6) {
                return ['success' => false, 'message' => 'Şifre en az 6 karakter olmalıdır'];
            }

            // Token kontrolü
            $query = "SELECT user_id FROM password_reset_tokens 
                     WHERE token = :token AND expires_at > NOW() AND is_used = 0";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':token', $data['token']);
            $stmt->execute();

            if ($stmt->rowCount() === 0) {
                return ['success' => false, 'message' => 'Geçersiz veya süresi dolmuş token'];
            }

            $token_data = $stmt->fetch();

            // Şifre güncelle
            $password_hash = password_hash($data['password'], PASSWORD_BCRYPT);
            $update_query = "UPDATE users SET password_hash = :password_hash WHERE id = :user_id";
            $stmt = $this->conn->prepare($update_query);
            $stmt->bindParam(':password_hash', $password_hash);
            $stmt->bindParam(':user_id', $token_data['user_id']);
            $stmt->execute();

            // Token'ı kullanılmış olarak işaretle
            $used_query = "UPDATE password_reset_tokens SET is_used = 1 WHERE token = :token";
            $stmt = $this->conn->prepare($used_query);
            $stmt->bindParam(':token', $data['token']);
            $stmt->execute();

            return ['success' => true, 'message' => 'Şifre başarıyla güncellendi'];
        } catch (Exception $e) {
            return ['success' => false, 'message' => 'Sunucu hatası: ' . $e->getMessage()];
        }
    }

    public function validateToken($token)
    {
        try {
            $query = "SELECT u.id, u.email, u.first_name, u.last_name 
                     FROM users u 
                     JOIN user_tokens ut ON u.id = ut.user_id 
                     WHERE ut.token = :token AND ut.expires_at > NOW() AND ut.is_active = 1 AND u.is_active = 1";

            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':token', $token);
            $stmt->execute();

            if ($stmt->rowCount() > 0) {
                return $stmt->fetch();
            }

            return false;
        } catch (Exception $e) {
            return false;
        }
    }

    private function generateToken()
    {
        return bin2hex(random_bytes(32));
    }

    private function mailSmtp($to, $subject, $message, $headers = "", $file = "", $ssite, $suser, $ssender)
    {
        $mail = new PHPMailer(true);
        try {
            $mail->isSMTP();
            $mail->Host       = SMTP_HOST;
            $mail->SMTPAuth   = true;
            $mail->Username   = SMTP_USER;
            $mail->Password   = SMTP_PASS;
            $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
            $mail->Port       = SMTP_PORT;
            $from_name = "$ssite";
            $from_email = "$ssender";
            $mail->setFrom($from_email, $from_name);
            $mail->addAddress($to);
            if (!empty($file)) {
                $mail->addAttachment($file);
            }
            $mail->isHTML(true);
            $mail->CharSet = "UTF-8";
            $mail->Subject = $subject;
            $mail->Body = $message;
            $mail->send();
            #echo "Message Sent OK\n";
        } catch (phpmailerException $e) {
            #echo $e->errorMessage(); //Pretty error messages from PHPMailer
        } catch (Exception $e) {
            #echo $e->getMessage(); //Boring error messages from anything else!
        }
    }
}
