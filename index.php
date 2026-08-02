<?php
/**
 * Root handler for PHP-stack hosting (Cloudways / DigitalOcean).
 *
 * A PHP stack resolves index.php before index.html, so the provider's default
 * welcome page was being served at the site root even though every other URL
 * worked. This file overwrites that welcome page and serves the real homepage.
 *
 * .htaccess cannot fix this here: the stack ignores it (a missing URL still
 * returned the provider page, proving DirectoryIndex and ErrorDocument were
 * never applied).
 *
 * Static hosts are unaffected. GitHub Pages serves index.html directly and
 * never executes or requests this file.
 */

$home = __DIR__ . '/index.html';

if (!is_readable($home)) {
    http_response_code(500);
    exit('Homepage missing: index.html was not found next to index.php.');
}

header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: public, max-age=0, must-revalidate');
readfile($home);
