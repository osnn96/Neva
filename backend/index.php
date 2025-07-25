<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Auth');

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(0);

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

require_once 'config/database.php';
require_once 'classes/User.php';
require_once 'classes/Auth.php';

// URL routing
$request_uri = $_SERVER['REQUEST_URI'];
$path = parse_url($request_uri, PHP_URL_PATH);
$path_parts = explode('/', trim($path, '/'));



// API base path'i çıkar
if ($path_parts[0] === 'api') {
    array_shift($path_parts);
}

$endpoint = $path_parts[0] ?? '';
$method = $_SERVER['REQUEST_METHOD'];

// Database bağlantısı
try {
    $database = new Database();
    $db = $database->getConnection();
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database connection failed']);
    exit();
}

// Route handling
switch ($endpoint) {
    case 'auth':
        $auth = new Auth($db);
        handleAuthRoutes($auth, $path_parts, $method);
        break;
        
    case 'user':
        $user = new User($db);
        handleUserRoutes($user, $path_parts, $method);
        break;
        
    default:
        http_response_code(404);
        echo json_encode(['error' => 'Endpoint not found']);
        break;
}

function handleAuthRoutes($auth, $path_parts, $method) {
    $action = $path_parts[1] ?? '';
    
    switch ($action) {
        case 'register':
            if ($method === 'POST') {
                $data = json_decode(file_get_contents('php://input'), true);
                echo json_encode($auth->register($data));
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        case 'login':
            if ($method === 'POST') {
                $data = json_decode(file_get_contents('php://input'), true);
                echo json_encode($auth->login($data));
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        case 'logout':
            if ($method === 'POST') {
                $token = getBearerToken();
                echo json_encode($auth->logout($token));
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        case 'forgot-password':
            if ($method === 'POST') {
                $data = json_decode(file_get_contents('php://input'), true);
                echo json_encode($auth->forgotPassword($data));
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        case 'reset-password':
            if ($method === 'POST') {
                $data = json_decode(file_get_contents('php://input'), true);
                echo json_encode($auth->resetPassword($data));
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        default:
            http_response_code(404);
            echo json_encode(['error' => 'Auth endpoint not found']);
            break;
    }
}

function handleUserRoutes($user, $path_parts, $method) {
    $token = getBearerToken();
    
    if (!$token) {
        http_response_code(401);
        echo json_encode(['error' => 'Authentication required']);
        return;
    }
    
    $action = $path_parts[1] ?? '';
    
    switch ($action) {
        case 'profile':
            if ($method === 'GET') {
                echo json_encode($user->getProfile($token));
            } elseif ($method === 'PUT') {
                $data = json_decode(file_get_contents('php://input'), true);
                echo json_encode($user->updateProfile($token, $data));
            } else {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
            }
            break;
            
        default:
            http_response_code(404);
            echo json_encode(['error' => 'User endpoint not found']);
            break;
    }
}

function getBearerToken() {
    $headers = getallheaders();
    
    
    if (isset($headers['Auth'])) {
        $auth_header = $headers['Auth'];
        if (preg_match('/Bearer\s+(.*)$/i', $auth_header, $matches)) {
            return $matches[1];
        }
    }
    
    return null;
}
?>