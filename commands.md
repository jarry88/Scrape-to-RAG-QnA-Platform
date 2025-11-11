docker-compose exec \
      -e EMAIL_IMAP_SERVER=$(grep EMAIL_IMAP_SERVER .env | cut -d '=' -f2) \
      -e EMAIL_USERNAME=$(grep EMAIL_USERNAME .env | cut -d '=' -f2) \
      -e EMAIL_APP_PASSWORD=$(grep EMAIL_APP_PASSWORD .env | cut -d '=' -f2) \
      backend python /scripts/monitor_email.py
openssl s_client -crlf -connect outlook.office365.com:993
A1 LOGIN "whitewind68@outlook.com" "691094@Ap"

docker run -d --name greenmail --network email_test_net -p 3143:3143 -p 3025:3025 greenmail/stand

docker run -d --name greenmail --network email_test_net -p 3143:3143 -p 3025:3025 greenmail/standalone:2.1.0
#Username: user@greenmail
#Password: password

docker run -d \
  --name greenmail \
  --network email_test_net \
  -p 3143:3143 \  # IMAP 端口（容器内默认143，这里映射为3143，保持你的原有配置）
  -p 3025:3025 \  # SMTP 端口（容器内默认25，这里映射为3025，保持你的原有配置）
  -e GREENMAIL_USER="user@example.com:123456" \  # 初始账号：user@example.com，密码：123456（可自定义修改）
  -e GREENMAIL_OPTS="-Dgreenmail.hostname=0.0.0.0 -Dgreenmail.port.imap=143 -Dgreenmail.port.smtp=25" \  # 明确容器内默认端口，确保映射正常
  greenmail/standalone:2.1.0

  docker-compose exec backend apt-get update && docker-compose exec backend apt-get install -y netcat-openbsd
  nc -vz greenmail 993