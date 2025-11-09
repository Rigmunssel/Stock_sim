#!/bin/sh
# Script to inject environment variables into JavaScript at runtime

# Create env-config.js with the backend URL
cat > /usr/share/nginx/html/env-config.js <<EOF
window.BACKEND_URL = '${BACKEND_URL:-http://localhost:5001}';
EOF

echo "Environment configuration created:"
cat /usr/share/nginx/html/env-config.js

# Start nginx
exec nginx -g 'daemon off;'


